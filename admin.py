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

from flask import Blueprint, request, Response, redirect, render_template, session, send_from_directory, jsonify,make_response,url_for
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime
from repository import *
from forms.admin_profile_form import AdminProfileForm
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname, realpath
import random
import string
from google.cloud import storage

UPLOADS_PATH = join(dirname(realpath(__file__)), 'uploads/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

bp = Blueprint('admin', __name__)
client = datastore.Client()

CLIENT_ID = r'939115278036-he2m51te7ohrp1m9r457nos1dbnh5u2o.apps.googleusercontent.com'
CLIENT_SECRET = r'LQQ_RyrsV-eA1uiuux0RrI7J'
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'https://datingappforanimaladoption.wl.r.appspot.com/authorization'

###############################################################################################################

@bp.route('/admin_profiles', methods=['GET'])
def adminPage():
    #if 'isAdmin' not in session:
     #   return "isAdmin not in session."
    #elif session['isAdmin'] == False:
     #   return "Not an admin account."
    #else:
    data = PetDsRepository.all()
    return render_template('admin_profiles.html', pets=data)
    
###############################################################################################################
    
@bp.route('/add_profile', methods=["GET"])
def add_profile():

    #if 'isAdmin' not in session:
    #    return "isAdmin not in session."
    #elif session['isAdmin'] == False:
    #    return "Not an admin account."
    #else:
    form = AdminProfileForm()
    return render_template('add_edit_profile.html')
        
 ###############################################################################################################   
    
@bp.route('/update_profile/<key>', methods=["GET"])
def update_profile(key):
    pet = PetDsRepository.get(key)
    #if 'isAdmin' not in session:
        #return "isAdmin not in session."
    #elif session['isAdmin'] == False:
    #    return "Not an admin account."
    #else:
    return render_template('add_edit_profile.html',pet=pet)

###############################################################################################################
species = "Any"
breed = "Any" 

pdata = PetDsRepository.all()

@bp.route('/profiles', methods=["GET", "POST"])
def profiles():
    global species, breed, pdata
    #form = FilterForm()
    if request.method == 'POST':
        content = request.get_json()

        species = content['species']
        breed = content['breed']
        if species == 'Any' and breed == "Any":
            pdata = PetDsRepository.all()    
    else:
        if species == 'Any' and breed == "Any":
            pdata = PetDsRepository.all() 
        else:
            pdata = PetDsRepository.filter(species,breed)

        print(pdata)
    return render_template('profiles.html', pets = pdata,  breed = breed, species=species)

#added route to filter pets
@bp.route('/filter', methods=["POST"])
def filter():
    global species, breed, pdata
    #form = FilterForm()
    content = request.get_json()
    species = content['species']
    breed = content['breed']
    if species == 'Any' and breed == "Any":
        pdata = PetDsRepository.all()
    else:
        pdata = PetDsRepository.filter(species,breed)
    return render_template('profiles.html', pets = pdata)


###############################################################################################################
        
@bp.route('/store_profile', methods=["POST"])
def store_profile():
    form = AdminProfileForm(request.form)
    if form.validate():
        if request.form['pet_key'] == '':
            PetDsRepository.create(request.form)
        else:
            PetDsRepository.update(form=request.form,key=request.form['pet_key'])
        responseBody = {"success": True, "message": "Data Successfully saved"}
    else:
        errors = []
        for fieldName, errorMessages in form.errors.items():
            field = []
            print(fieldName)
            for err in errorMessages:
                print(err)
        responseBody = {"success": False, "message": "There are errors in the inputs"}
    #if 'sub' not in session:
      #  return "sub not in session."
    #else:
        #content = request.get_json()
    # try:
    #     content = request.get_json()
    #     for c in content:
    #         print(c)
    # except:
    #     pass
    return (json.dumps(responseBody), 200)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@bp.route('/add_image', methods=["POST"])
def add_image():
    file = request.files['image']
    client = storage.Client()
    bucket = client.get_bucket('datingappforanimaladoption.appspot.com')

    if file.filename == '':
        responseBody = {"success": False, "message": "No File Selected"}
    if file:
        name = file.filename.split('.')[0] + get_random_string(8)
        filename = secure_filename(name + '.' + file.filename.split('.')[1])
        #file.save(os.path.join(UPLOADS_PATH, filename))
        blob = bucket.blob('uploads/' + filename)
        blob.upload_from_string(file.getvalue())
        responseBody = {"success": True, "message": "File Saved", "profile_image_name": filename}
    return (json.dumps(responseBody), 200)


@bp.route('/delete_profile', methods=["POST"])
def delete_profile():
    key = request.form['key']
    PetDsRepository.delete_profile(key=key)
    responseBody = {"success": True, "message": "Deleted"}
    return (json.dumps(responseBody), 200)


@bp.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOADS_PATH, filename)

print("admin imported")