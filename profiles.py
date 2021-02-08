###############################################################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description: Routes for profiles page. Profile card dynamic.
#
# Note:
#
#
# References:
# 
###############################################################################################################

from flask import Blueprint, request, Response, redirect, render_template, session, make_response
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime
#import requests
bp = Blueprint('profiles', __name__)
client = datastore.Client()

from OAuth import printSession

###############################################################################################################
@bp.route('/profiles', methods=["GET"])
def view_profile():
    # printSession('***** ADOPT *****')
    if 'sub' not in session:
        return "Error: \'sub\' not in session!!!"
    else:
        # Direct requests to GAE database
        if request.method == 'GET':
            JWT = session['id_token']
            # Grab 'sub' ID from JWT verification
            req = requests.Request()
            # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
            id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
            if session['sub'] != id_info['sub']:
                return 'Error": "Invalid JWT'
            # Get all pets from the datastore owned by user
            query = client.query(kind=constants.pets)
            profiles = list(query.fetch())

            profile_img = []
            for r in profiles:
                r['id'] = r.key.id
                r['self'] = constants.url + '/pets/' + str(r.key.id)
                # temp url, file name needs to be from dogs assets file and remove numbers
                r['img'] = str(r['name']) + "/" + str(r['name']) + "-01.jpeg"
                profile_img.append(r['img'])
                print(r)
                print(r['img'])
                print(profile_img)
            return render_template('profiles.html', profiles=profiles, profile_img=profile_img)
        return render_template('Real response message')
