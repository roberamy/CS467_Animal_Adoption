###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# Description: Routes for news page                                                                           #
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
from OAuth import printSession

bp = Blueprint('news', __name__)
client = datastore.Client()

###############################################################################################################

@bp.route('/news', methods=["GET"])
def news():
    printSession('***** NEWS *****')
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('news.html')
        
###############################################################################################################

@bp.route('/news_post', methods=["GET"])
def news_post():
    printSession('***** NEWS POST *****')
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('news_post.html')
        
###############################################################################################################

@bp.route('/pet_page', methods=["GET"])
def pet_page():
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('pet_page.html')

