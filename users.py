###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# Description: Routes for admin page                                                                          #
#                                                                                                             #
# Note:                                                                                                       #
#                                                                                                             #
###############################################################################################################

from flask import Blueprint, request, Response, redirect, render_template, session
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime

bp = Blueprint('users', __name__)
client = datastore.Client()

###############################################################################################################

@bp.route('/users', methods=['GET'])
def getUsers():
       
    # Get all users from the datastore
    query = client.query(kind=constants.users)
    results = list(query.fetch())
    
    # Store users for return 
    responseBody = []
    for r in results:
        r["self"] = 'https://bauergr-final.wl.r.appspot.com/boats/' + str(r.key.id)
        responseBody.append(r)
             
    return (json.dumps(responseBody), 200)
    
    
###############################################################################################################