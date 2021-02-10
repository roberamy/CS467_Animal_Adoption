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
# References: https://stackoverflow.com/questions/35444880/how-to-view-an-image-stored-in-google-cloud-storage-bucket
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
# User modules
from repository import *

#import requests
bp = Blueprint('profiles', __name__)
client = datastore.Client()

from OAuth import printSession



###############################################################################################################
@bp.route('/profiles', methods=["GET"])
def view_profile():
    if 'sub' not in session:
        return "Error: \'sub\' not in session!!!"
    else:
        # Direct requests to GAE database
        if request.method == 'GET':
            # Return all pet entities in the datastore to populate 'admin_profiles.html'
            # Instantiate singleton PetDsRepository class with member functions -- see 'repository.py'
            data = PetDsRepository.all()
            return render_template('profiles.html', pets=data)
        return render_template('Real response message')
