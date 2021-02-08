###############################################################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
#
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# This module peform CRUD operations for applictions entity
#
###############################################################################################################

from flask import Blueprint, render_template, request, Response, session
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime

bp = Blueprint('applications', __name__)
client = datastore.Client()

###############################################################################################################

@bp.route('/admin_applications', methods=['GET'])
def adminApplication():
    if 'isAdmin' not in session:
        return "Error: \'isAdmin\' not in session."
    elif session['isAdmin'] == False:
        return "Error: \'sub\' is not an admin."
    else:
        return render_template('applications_admin.html')
            
###############################################################################################################
       
@bp.route('/application', methods=['GET'])
def newApplication():
    if 'sub' not in session:
        return "Error: \'sub\' not in session."
    else:
        return render_template('application_new.html')
            
###############################################################################################################

@bp.route('/my_applications', methods=['GET'])
def userApplication():
    if 'sub' not in session:
        return "Error: \'sub\' not in session."
    else:
        return render_template('applications_user.html')
          
###############################################################################################################
