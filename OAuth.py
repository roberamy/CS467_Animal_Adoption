###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
# Sources: https://developers.google.com/identity/protocols/oauth2/web-server#httprest,                       #
#   https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments,                            #
#   https://flask.palletsprojects.com/en/1.1.x/quickstart/,                                                   #
#   https://stackoverflow.com/questions/51262531/flask-context-variable-not-available-in-template/51262916    #
#                                                                                                             #  
#                                                                                                             #
###############################################################################################################

from flask import Blueprint, request, Response, redirect, render_template, session
import json
import requests
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from google.cloud import datastore
import constants
from datetime import datetime

bp = Blueprint('OAuth', __name__)
client = datastore.Client()



OAUTH = OAuth2Session(constants.CLIENT_ID, redirect_uri=constants.REDIRECT_URI, scope=constants.SCOPES)
    
###############################################################################################################

def printSession(header):
    print(header)
    # Check JWT in session
    if 'id_token' in session:
        print('JWT: jwt exists')
    else:
        print('JWT: jwt not in session')
    # Check sub in session
    if 'sub' in session:
        print('SUB: ' + session['sub'])
    else:
        print('SUB: sub not in session')
    # Check usr_email in session
    if 'usr_email' in session:
        print('EMAIL: ' + session['usr_email'])
    else:
        print('EMAIL: usr_email not in session')
    # Check isAdmin in session
    if 'isAdmin' in session:
        print('IS ADMIN: ' + str(session['isAdmin']))
    else:
        print('IS ADMIN: isAdmin not in session')
        
    print ('******************')
    
###############################################################################################################
    
@bp.route('/index', methods=['GET'])
def index():

    # This url renders a diaglog box to authenticate using google account
    authorization_url, state = OAUTH.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        # access_type and prompt are Google specific extra
        # parameters.
        access_type="offline", prompt="select_account")
        
    return redirect(authorization_url)

###############################################################################################################
 
@bp.route('/authorization', methods=['GET'])
def callback():
  
    # After redirect from authentication, this route returns the authorization token
    token = OAUTH.fetch_token(
        # Token endpoint
        'https://accounts.google.com/o/oauth2/token',
        authorization_response=request.url,
        client_secret=constants.CLIENT_SECRET)
        
    req = requests.Request()

    # Get email of authenticated user
    id_info = id_token.verify_oauth2_token(token['id_token'], req, constants.CLIENT_ID)
    
    # Store token, sub, and email in session
    session['id_token'] = token['id_token']
    session['usr_email'] = id_info['email']
    session['sub'] = id_info['sub']

    email = session['usr_email']
    jwt = session['id_token']
    sub = session['sub']

    # query all users in database
    query = client.query(kind=constants.users)
    users = list(query.fetch())
    
    # Check if user has account
    for user in users:
        try:
            # User already exists
            if user['uniqueID'] == sub:
                session['isAdmin'] = user['isAdmin']
                #return render_template('index.html')
                printSession('***** RESULTS EXISTING USER *****')
                return redirect('/')
                #return render_template('results.html', sub=sub, email=email, jwt=jwt, isAdmin=session['isAdmin'])
        except:
            pass
    
    # User doesn't exist, store user and record account creation date
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    new_user = datastore.entity.Entity(key=client.key(constants.users))
    new_user.update({"uniqueID": sub, "email": email, "isAdmin": False, "creation_date": dt_string, "last_modified": None})
    session['isAdmin'] = False
    client.put(new_user)
    printSession('***** RESULTS NEW USER *****')
    return redirect('/')

###############################################################################################################   

@bp.route('/results', methods=['GET'])
def results():
    if 'sub' not in session:
        return "sub not in session."
    else:
        #return render_template('index.html')
        printSession('***** RESULTS *****')
        return render_template('results.html', sub=session['sub'], email=session['usr_email'],
            jwt=session['id_token'], isAdmin=session['isAdmin'])
    
############################################################################################################### 
                   


