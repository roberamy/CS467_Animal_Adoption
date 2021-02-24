###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description: Routes for admin page
#
# Ref:  https://werkzeug.palletsprojects.com/en/1.0.x/utils/
#       https://wtforms.readthedocs.io/en/2.3.x/crash_course/
#       https://docs.python.org/3/library/io.html
#       https://wtforms.readthedocs.io/en/2.3.x/forms/
#       https://flask.palletsprojects.com/en/1.1.x/api/
#       https://www.w3schools.com/python/ref_string_join.asp
###############################################################################

# Library modules
from flask import Blueprint, request, Response, redirect, render_template
from flask import session, send_from_directory
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname, realpath
import random
import string
from google.cloud import storage
# User modules
from repository import PetDsRepository
from forms.admin_profile_form import AdminProfileForm
from OAuth import printSession


UPLOADS_PATH = join(dirname(realpath(__file__)), 'uploads/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

bp = Blueprint('admin', __name__)
client = datastore.Client()

# Used for /profiles route
species = "Any"
breed = "Any" 
pdata = PetDsRepository.all()

###############################################################################


@bp.route('/admin_profiles', methods=['GET'])
def adminPage():
    printSession('***** PROFILE ADMIN *****')
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] is False:
        return "Not an admin account."
    else:
        # Return all pet entities to populate 'admin_profiles.html'
        # Instantiate singleton PetDsRepository class with member functions
        # See 'repository.py'
        data = PetDsRepository.all()
        for d in data:
            # Format datetime to yyyy-mm-dd
            d['created_at'] = datetime.strftime(d['created_at'], "%Y-%m-%d")
            # Format properties to include \n to improve html display
            d['properties'] = "\n".join(d['properties'].split(','))
        return render_template('admin_profiles.html', pets=data)

###############################################################################


@bp.route('/add_profile', methods=["GET"])
def add_profile():
    printSession('***** ADD PROFILE *****')
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] is False:
        return "Not an admin account."
    else:
        # Get all breeds from database & sort alphabetically
        query = client.query(kind=constants.breeds)
        query.order = ["name"]
        breeds = list(query.fetch())
        # print("LENGTH:" + str(length))
        form = AdminProfileForm()
        return render_template('add_edit_profile.html',
                               breeds=breeds, form=form)

###############################################################################


@bp.route('/update_profile/<key>', methods=["GET"])
def update_profile(key):
    printSession('***** UPDATE PROFILE *****')
    pet = PetDsRepository.get(key)
    # print(pet)
    # print(pet['type'])
    if 'isAdmin' not in session:
        return "isAdmin not in session."
    elif session['isAdmin'] is False:
        return "Not an admin account."
    else:
        # Get all breeds from database & sort alphabetically
        query = client.query(kind=constants.breeds)
        query.order = ["name"]
        breeds = list(query.fetch())
        return render_template('add_edit_profile.html', pet=pet, breeds=breeds)
    
###############################################################################

@bp.route('/store_profile', methods=["POST"])
def store_profile():
    if 'sub' not in session:
        return ("sub not in session.", 403)
    else:
        # Instantiate AdminProfileForm class used for input validation
        form = AdminProfileForm(request.form)
        if form.validate():
            # Create new pet entity in data store if no key provided
            if request.form['pet_key'] == '':
                PetDsRepository.create(request.form)
            # Update pet entity if key provided
            else:
                PetDsRepository.update(
                    form=request.form, key=request.form['pet_key'])
            responseBody = {"success": True, "message": "Data Successfully saved"}
            return (json.dumps(responseBody), 200)
        else:
            errors = []
            for fieldName, errorMessages in form.errors.items():
                field = []
                print(fieldName)
                for err in errorMessages:
                    print(err)
            responseBody = {"success": False,
                        "message": fieldName.title() + ': ' + err}
            return (json.dumps(responseBody), 400)
        

###############################################################################


# Returns random character string of provided length to be concatenated
# with fileName before storing in Google Storage bucket
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

###############################################################################


# Route to add image to storage bucket
@bp.route('/add_image', methods=["POST"])
def add_image():
    file = request.files['image']
    client = storage.Client()
    bucket = client.get_bucket('datingappforanimaladoption.appspot.com')

    if file.filename == '':
        responseBody = {"success": False, "message": "No File Selected"}
    if file:
        # Construct secure filename with werkzeug module
        name = file.filename.split(
            '.')[0] + get_random_string(8)  # Secure file names
        filename = secure_filename(name + '.' + file.filename.split('.')[1])
        # file.save(os.path.join(UPLOADS_PATH, filename)) # Didn't work!!
        blob = bucket.blob('uploads/' + filename)
        blob.upload_from_string(file.getvalue())
        responseBody = {"success": True, "message": "File Saved",
                        "profile_image_name": filename}
    return (json.dumps(responseBody), 200)

###############################################################################


# Route to delete profile from datastore
@bp.route('/delete_profile', methods=["POST"])
def delete_profile():
    key = request.form['key']
    # Instantiate singleton PetDsRepository class with member functions
    # see 'repository.py'
    PetDsRepository.delete_profile(key=key)
    responseBody = {"success": True, "message": "Deleted"}
    return (json.dumps(responseBody), 200)

###############################################################################


# Route to download file from
@bp.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOADS_PATH, filename)
