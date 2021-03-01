###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
# Sources: https://developers.google.com/identity/protocols/oauth2/web-server#httprest,
#   https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments,
#   https://flask.palletsprojects.com/en/1.1.x/quickstart/,
#   https://stackoverflow.com/questions/51262531/flask-context-variable-not-available-in-template/51262916
#   https://stackoverflow.com/questions/39261260/flask-session-variable-not-persisting-between-requests/39261335
#
###############################################################################

from flask import Blueprint, request, redirect
from flask import render_template, session
import json
import requests
import flask
from requests_oauthlib import OAuth2Session
from google.cloud import datastore
from datetime import datetime
import constants

bp = Blueprint('OAuth', __name__)
client = datastore.Client()


###############################################################################

# Helper function to debug OAuth
def printSession(header):
    print(header)
    # Check JWT in session
    if 'credentials' in session:
        print('JWT: jwt exists')
    else:
        print('JWT: jwt not in session')
    # Check sub in session
    if 'sub' in session:
        print('SUB: ' + session['sub'])
    else:
        print('SUB: sub not in session')
    # Check usr_email in session
    if 'user_email' in session:
        print('EMAIL: ' + session['user_email'])
    else:
        print('EMAIL: usr_email not in session')
    # Check isAdmin in session
    if 'isAdmin' in session:
        print('IS ADMIN: ' + str(session['isAdmin']))
    else:
        print('IS ADMIN: isAdmin not in session')
    print('******************')

###############################################################################


@bp.route('/authorization', methods=['GET'])
def callback():
    # Authorization 'code' not stored, send request to get code
    if 'code' not in flask.request.args:
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                    '&client_id={}&redirect_uri={}&scope={}&state={}').format(
                        constants.CLIENT_ID,
                        constants.REDIRECT_URI,
                        constants.SCOPE,
                        constants.SECRET_KEY)
        return flask.redirect(auth_uri)
    else:
        # Get authorization code & state sent from server
        # auth_code = flask.request.args.get('code')
        auth_state = flask.request.args.get('state')
        # Compare 'state' returned by server to 'state' created by app
        # If the same, complete oauth requests & redirect to user info
        if auth_state == constants.SECRET_KEY:
            myOauth = OAuth2Session(
                constants.CLIENT_ID,
                redirect_uri=constants.REDIRECT_URI,
                scope=constants.SCOPE)
            token = myOauth.fetch_token('https://accounts.google.com/o/oauth2/token',
                                        authorization_response=request.url,
                                        client_secret=constants.CLIENT_SECRET)
            flask.session['credentials'] = token
            # print('TOKEN:')
            # print(token['access_token'])
            # print('JWT:')
            # print(token['id_token'])
            # Send token to get user info
            request_uri = (
                'https://www.googleapis.com/oauth2/v3/userinfo?access_token={}').format(token['access_token'])
            myInfo = requests.get(request_uri)
            flask.session['user'] = myInfo.text
            user = json.loads(flask.session['user'])
            # print('USER')
            # print(user)
            userID = user['sub']
            flask.session['sub'] = user['sub']
            flask.session['user_email'] = user['email']
            # print('USER ID:')
            # print(flask.session['sub'])
            # print('USER EMAIL:')
            # print(flask.session['user_email'])
            query = client.query(kind=constants.users)
            results = list(query.fetch())
            length = len(results)
            now = datetime.now()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            # print(length)
            if length > 0:
                exists = False
                for e in results:
                    if e['uniqueID'] == str(userID):
                        exists = True
                        if e['isAdmin'] is True:
                            flask.session['isAdmin'] = True
                        else:
                            flask.session['isAdmin'] = False
                if exists is False:
                    new_user = datastore.entity.Entity(
                        key=client.key(constants.users))
                    new_user.update({"uniqueID": user['sub'],
                                     "email": user['email'],
                                     "isAdmin": False,
                                     "creation_date": dt_string,
                                     "last_modified": None})
                    client.put(new_user)
                    print("NEW USER ID:")
                    print(new_user.key.id)
                    flask.session['isAdmin'] = False
            # First user login, add user entity
            else:
                new_user = datastore.entity.Entity(
                    key=client.key(constants.users))
                new_user.update({"uniqueID": user['sub'],
                                 "email": user['email'],
                                 "isAdmin": False,
                                 "creation_date": dt_string,
                                 "last_modified": None})
                client.put(new_user)
                print("NEW USER ID:")
                print(new_user.key.id)
                flask.session['isAdmin'] = False
            return redirect('/')
        # 'state' values not the same, redirect back to home
        else:
            return redirect('/')

###############################################################################


@bp.route('/results', methods=['GET'])
def results():
    # No user info available, render empty user info page
    if 'credentials' not in flask.session:
        return redirect('/')
    # User info stored in session, render completed page
    else:
        user = json.loads(flask.session['user'])
        print('*** USER ***')
        # print(user)
        userjwt = flask.session['credentials']['id_token']
        # print('*** USER JWT ***')
        # print(userjwt)
        userID = flask.session['sub']
        userEmail = user['email']
        isAdmin = flask.session['isAdmin']
        return render_template('results.html',
                               sub=userID,
                               email=userEmail,
                               jwt=userjwt,
                               isAdmin=isAdmin)

###############################################################################
