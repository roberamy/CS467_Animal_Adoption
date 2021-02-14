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
import news
from repository import *


bp = Blueprint('news', __name__)
client = datastore.Client()

CLIENT_ID = r'939115278036-he2m51te7ohrp1m9r457nos1dbnh5u2o.apps.googleusercontent.com'
CLIENT_SECRET = r'LQQ_RyrsV-eA1uiuux0RrI7J'
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'https://datingappforanimaladoption.wl.r.appspot.com/authorization'

###############################################################################################################

@bp.route('/news', methods=["GET"])
def news():
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('news.html')
        
###############################################################################################################

@bp.route("/news_post", methods=["GET"])
def news_post():
    if 'sub' not in session:
        return "sub not in session."
    else:
        return render_template('news_post.html')
        
###############################################################################################################

@bp.route("/pet_page/<key>", methods=["GET"])
def pet_page(key):
    data = PetDsRepository.get(key)
    if 'sub' not in session:
        return render_template('pet_page.html', pet=data)
    else:
        return render_template('pet_page.html', pet=data)

