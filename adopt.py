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
from OAuth import printSession
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
from repository import PetDsRepository

# Used for /profiles route
species = "Any"
breed = "Any"
pdata = PetDsRepository.all()

# set disposition intial
disposition = "Any"

# Import requests
bp = Blueprint('adopt', __name__)
client = datastore.Client()


###############################################################################
# temperary route to figure pet pages out
@bp.route('/pet_page/<pet_id>', methods=["GET"])
def view_pet_page(pet_id):
    if request.method == 'GET':
        # get specific pet data from pet key
        pet_data = PetDsRepository.get(pet_id)
        # For improved display, add space after comma
        pet_data['properties'] = ", ".join(pet_data['properties'].split(','))
        # API Link accessing public data format https://storage.googleapis.com/BUCKET_NAME/OBJECT_NAME
        return render_template('pet_page.html',
                               pet_data=pet_data,
                               public_url=constants.BUCKET)
    else:
        # redo temporary error response
        return "Error"

###############################################################################
# helper pagination function, per_page modified in __init__py


def get_pet_page(data, offset=0, per_page=10):
    return data[offset: offset + per_page]

# Discovered datastore doesn't allow combining filters on one property
# and order on another property for query. So filtering out adopted in
# pets for adopt cards after query of pet entities


def filter_out_adopt(pet_data_datastore):
    adopted = "Adopted"
    pet_data_filtered = []

    for pet in pet_data_datastore:
        if pet['availability'] != adopted:
            pet_data_filtered.append(pet)

    return pet_data_filtered

def filter_disposition(pet_data_datastore, disposition):
    pet_data_filtered = []
    # print("I'm filter_disposition function")
    for pet in pet_data_datastore:
        pet_disposition_split = pet['properties'].split(",")
        # check if list is empty
        if not pet_disposition_split:
            # print("The pet properties if pet_disposition_split is empty " +str(pet['properties']))
            if pet['properties'] == disposition:
                pet_data_filtered.append(pet)
        if disposition in pet_disposition_split:
            pet_data_filtered.append(pet)
    # print("Pet_data_filtered: "+str(pet_data_filtered))
    return pet_data_filtered

@bp.route('/adopt_profiles', methods=["GET", "POST"])
def view_profile():
    global species, breed, pdata
    global disposition # test disposition global value for filtering
    if 'sub' not in session:
        return "sub not in session."
        # return redirect('/')
    else:
        if request.method == 'POST':
            content = request.get_json()
            species = content['species']
            breed = content['breed']

            disposition = content['disposition']

            if species == 'Any' and breed == "Any" and disposition == "Any":
                print("I'm in POST")
                pdata = PetDsRepository.all()
            elif species == 'Any' and breed == "Any" and disposition != "Any":
                print("I'm in POST again")
                pdata_pre = PetDsRepository.all()
                pdata = filter_disposition(pdata_pre, disposition)
            elif species == 'Any' and breed != "Any" and disposition != "Any":
                pdata_pre = PetDsRepository.filter(species,breed)
                pdata = filter_disposition(pdata_pre, disposition)
            elif species != 'Any' and breed != "Any" and disposition != "Any":
                pdata_pre = PetDsRepository.filter(species,breed)
                pdata = filter_disposition(pdata_pre, disposition)
                print("In POST of last elif statement")
                print(species)
                print(breed)
                print(disposition)

        else:  # psuedo GET
            if species == 'Any' and breed == "Any" and disposition == "Any":
                pdata = PetDsRepository.all()
                print("I'm in GET")
                print("I'm in if 1. statement")
                print(species)
                print(breed)
                print(disposition)
            elif species == 'Any' and breed == "Any" and disposition != "Any":
                pdata_pre = PetDsRepository.all()
                pdata = filter_disposition(pdata_pre, disposition)
                print("These are accounts that are filtered by disposition only")
                print("I'm in GET elif")
                print(species)
                print(breed)
                print(disposition)
            elif species == 'Any' and breed != "Any" and disposition != "Any":
                pdata_pre = PetDsRepository.filter(species,breed)
                pdata = filter_disposition(pdata_pre, disposition)
                print(species)
                print(breed)
                print(disposition)
            elif species != 'Any' and breed != "Any" and disposition != "Any":
                pdata_pre = PetDsRepository.filter(species,breed)
                pdata = filter_disposition(pdata_pre, disposition)
                print(species)
                print(breed)
                print(disposition)
            else:
                pdata = PetDsRepository.filter(species, breed)
                print("Else statement if dispostion not Any")
                print(species)
                print(breed)
                print(disposition)

        # print("****************"*10)
        # print(species)
        # print(breed)

        # new filtered pet data to not listed adopted in card profiles
        pdata_filtered = filter_out_adopt(pdata)

        # start of pagination code
        total = len(pdata_filtered)

        # pagination code
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page')

        # change per page value after get_page_args
        per_page = 9
        offset = (page - 1) * per_page

        pagination_adopt_profile = get_pet_page(
            pdata_filtered, offset=offset, per_page=per_page)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total,
                                css_framework='bootstrap4'
                                )

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
                               public_url=constants.BUCKET,
                               breeds=breeds
                               )
