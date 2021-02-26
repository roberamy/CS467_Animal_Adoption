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
#             https://cloud.google.com/storage/docs/access-public-data#api-link
#             https://jinja.palletsprojects.com/en/2.10.x/templates/
#             https://stackoverflow.com/questions/48002297/how-to-concatenate-int-with-str-type-in-jinja2-template
#             https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9 per_page solution flask
#             https://flask-paginate.readthedocs.io/en/master/
#             
# 
###############################################################################################################

# Library modules
from flask import Blueprint, request, Response, redirect, render_template, session, make_response
# from flask import Blueprint, request, Response, redirect, render_template, session, send_from_directory, jsonify, make_response, url_for
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime

from flask_paginate import Pagination, get_page_args

# User modules
from repository import *

# Used for /profiles route
species = "Any"
breed = "Any" 
pdata = PetDsRepository.all()

#import requests
bp = Blueprint('adopt', __name__)
client = datastore.Client()

from OAuth import printSession

# bucket name for GCS public URL + subfolder
BUCKET_NAME = "datingappforanimaladoption.appspot.com/uploads/"

##############################################################################################################
# temperary route to figure pet pages out
@bp.route('/pet_page/<pet_id>', methods=["GET"])
def view_pet_page(pet_id):
    if request.method == 'GET':
        # get specific pet data from pet key
        pet_data = PetDsRepository.get(pet_id)
        # API Link accessing public data format https://storage.googleapis.com/BUCKET_NAME/OBJECT_NAME
        public_url = "https://storage.googleapis.com/" + BUCKET_NAME
        return render_template('pet_page.html', pet_data=pet_data, public_url=public_url)
    else:
        # redo temporary error response
        return "Error"

###############################################################################
# helper pagination function, per_page modified in __init__py
def get_pet_page(data, offset=0, per_page=10):
    return data[offset: offset + per_page]

@bp.route('/adopt_profiles', methods=["GET", "POST"])
def view_profile():
    global species, breed, pdata
    if 'sub' not in session:
        return "sub not in session."
    else:
        if request.method == 'POST':
            content = request.get_json()
            species = content['species']
            breed = content['breed']

            if species == 'Any' and breed == "Any":
                pdata = PetDsRepository.all()

        else: # psuedo GET
            if species == 'Any' and breed == "Any":
                pdata = PetDsRepository.all()
            else:
                pdata = PetDsRepository.filter(species,breed)

        # start of filtering out of adopted in pets for adopt cards
        # print(pdata)
        print("****************"*10)
        print(species)
        print(breed)

        # Discovered datastore doesn't allow combiningsg filters on 
        # one property and order on another property for query so 
        # filter post query of pet entities
        def filter_out_adopt(pet_data_datastore):
            adopted = "Adopted"
            pet_data_filtered=[]

            for pet in pet_data_datastore:
                if pet['availability'] != adopted:
                    pet_data_filtered.append(pet)

            return pet_data_filtered

        # new filtered pet data to not listed adopted in card profiles
        pdata_filtered = filter_out_adopt(pdata)

        # start of pagination code
        total = len(pdata_filtered)

        # pagination code
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

        # change per page value after get_page_args
        per_page = 9
        offset = (page - 1) * per_page

        pagination_adopt_profile = get_pet_page(pdata_filtered, offset=offset, per_page=per_page)

        pagination = Pagination(page=page, 
                                per_page=per_page, 
                                total=total,
                                css_framework='bootstrap4'
                                )    

        # API Link accessing public data format https://storage.googleapis.com/BUCKET_NAME/OBJECT_NAME
        public_url = "https://storage.googleapis.com/" + BUCKET_NAME

        # Get all breeds from database & sort alphabetically
        query = client.query(kind=constants.breeds)
        query.order = ["name"]
        breeds = list(query.fetch())

        return render_template('adopt_profiles.html',
                               pets=pagination_adopt_profile,
                               page=page,
                               per_page=per_page,
                               pagination=pagination,
                               breed=breed, 
                               species=species,
                               public_url=public_url,
                               breeds=breeds
                               )