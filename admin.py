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

bp = Blueprint('admin', __name__)
client = datastore.Client()

# CLIENT_ID = r'939115278036-he2m51te7ohrp1m9r457nos1dbnh5u2o.apps.googleusercontent.com'
# CLIENT_SECRET = r'LQQ_RyrsV-eA1uiuux0RrI7J'
# SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
#     'https://www.googleapis.com/auth/userinfo.profile']
# REDIRECT_URI = 'https://datingappforanimaladoption.wl.r.appspot.com/authorization'

# J local 
CLIENT_ID = r'20872689223-stjkrofc8280dtpnghpinqfif2dt7sqg.apps.googleusercontent.com'
CLIENT_SECRET = r'LUKL4Udr-T3Pki4lhUgZP32J'
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'http://localhost:8080/authorization'

###############################################################################################################

@bp.route('/admin_profiles', methods=['GET'])
def adminPage():
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] == False:
        return "Not an admin account."
    else:
        return render_template('admin_profiles.html')
    
###############################################################################################################
    
@bp.route('/add_profile', methods=["GET"])
def add_profile():
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] == False:
        return "Not an admin account."
    else:
        return render_template('add_profile.html')
        
 ###############################################################################################################   
    
@bp.route('/update_profile', methods=["GET"])
def update_profile():
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] == False:
        return "Not an admin account."
    else:
        return render_template('update_profile.html')

###############################################################################################################
        
@bp.route('/profiles', methods=["GET"])
def view_profile():
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('profiles.html')