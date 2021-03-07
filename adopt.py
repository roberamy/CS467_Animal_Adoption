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
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime, timedelta, timezone
# import pytz
from flask_paginate import Pagination, get_page_args

# User modules
from repository import PetDsRepository

# use for datetime compare naive vs aware


# Used for /profiles route
species = "Any"
breed = "Any"
disposition = "Any"
days_on = "Any"
pdata = PetDsRepository.all()

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

def filter_out_adopt(pet_data_datastore):
    adopted = "Adopted"
    pet_data_filtered = []

    for pet in pet_data_datastore:
        if pet['availability'] != adopted:
            pet_data_filtered.append(pet)

    return pet_data_filtered

def filter_disposition(pet_data_datastore, disposition):
    pet_data_filtered = []

    # splits property string for filter comparison
    for pet in pet_data_datastore:
        pet_disposition_split = pet['properties'].split(",")

        # check if list is empty
        if not pet_disposition_split:
             # append pet profile to list if filter matches single item list
            if pet['properties'] == disposition:
                pet_data_filtered.append(pet)

        # append pet profile to list if filter matches multi-item list
        if disposition in pet_disposition_split:
            pet_data_filtered.append(pet)

    return pet_data_filtered

def filter_days_on(pet_data, days_on):
    pet_data_filtered = []
    time_now = datetime.now()

    # account for 30+ days, just return all data
    if days_on == "Over 30":
        return pet_data

    else:
        if days_on != "Any":
            days = timedelta(days=int(days_on))
        else:
            days = timedelta(days=0)

        time_delta = datetime.now() - days

        # make time delta offset aware (UTC timezone) instead of .tzinfo none value
        aware_time_delta = pytz.UTC.localize(time_delta)

        for pet in pet_data:
            if pet['created_at'] >= aware_time_delta:
                pet_data_filtered.append(pet)

    return pet_data_filtered

# sort orders are ignored on properties with quality filters
def filter_species_breed(pet_data, species, breed):
    pet_data_filtered = []
    if species != "Any" and breed == "Any":
        for pet in pet_data:
            if pet['type'] == species:
                pet_data_filtered.append(pet)
    elif species == "Any" and breed != "Any":
        for pet in pet_data:
            if pet['breed'] == breed:
                pet_data_filtered.append(pet)
    else:
        for pet in pet_data:
            if pet['type'] == species and pet['breed'] == breed:
                pet_data_filtered.append(pet)                

    return pet_data_filtered

@bp.route('/adopt_profiles', methods=["GET", "POST"])
def view_profile():
    global species, breed, pdata, disposition, days_on

    if 'sub' not in session:
        return "sub not in session."

    else:
        if request.method == 'POST':
            content = request.get_json()
            species = content['species']
            breed = content['breed']
            disposition = content['disposition']
            days_on = content['days_on']

            # no filtering just all 
            if species == 'Any' and breed == "Any" and disposition == "Any" and days_on == "Any": #1
                pdata = PetDsRepository.all()
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)

            # # filter for all animals by days on app
            # elif species == 'Any' and breed == "Any" and disposition == "Any" and days_on != "Any": # 2
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on == "Any": # 3
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_disposition(pet_data_all, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on != "Any": # 4
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_disposition(pet_data_all, disposition)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed != "Any" and disposition == "Any" and days_on == "Any": # 5
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_species_breed(pet_data_all, species, breed)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed != "Any" and disposition == "Any" and days_on != "Any": # 6
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on == "Any": # 7
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on != "Any": # 8
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_2 = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_2, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed == "Any" and disposition == "Any" and days_on == "Any": # 9
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_species_breed(pet_data_all, species, breed)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed == "Any" and disposition == "Any" and days_on != "Any": # 10
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed == "Any" and disposition != "Any" and days_on == "Any": # 11
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed == "Any" and disposition != "Any" and days_on !="Any": # 12
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_2 = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_2, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed != "Any" and disposition == "Any" and days_on =="Any": # 13
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_species_breed(pet_data_all, species, breed)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed != "Any" and disposition == "Any" and days_on !="Any": # 14
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed != "Any" and disposition != "Any" and days_on =="Any": # 15
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # elif species != 'Any' and breed != "Any" and disposition != "Any" and days_on !="Any": # 16
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_2 = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_2, days_on)


            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # # filter for all animals by disposition
            # elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on == "Any":
            #     # pdata_pre = PetDsRepository.all()
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_disposition(pet_data_all, disposition)
            #     # pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # # filter for all animals by disposition and days
            # elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on != "Any":
            #     pet_data_all = PetDsRepository.all()
            #     # pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre = filter_disposition(pet_data_all, disposition)
            #     pdata = filter_days_on(pdata_pre, days_on)
            # # filter by breed and disposition
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on == "Any":
            #     # pdata_pre = PetDsRepository.filter(species,breed)
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            # # filter by breed, disposition, and days
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on != "Any":
            #     # pdata_pre = PetDsRepository.filter(species,breed)
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_dis = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_dis, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # # filter by all criteria
            # elif species != 'Any' and breed != "Any" and disposition != "Any":
            #     pdata_pre = PetDsRepository.filter(species,breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            #     # print("Date time now: " +  str(days_on) + " " + str(datetime.now()))
        else:  # psuedo GET

            # no filtering just all 
            if species == 'Any' and breed == "Any" and disposition == "Any" and days_on == "Any": #1
                pdata = PetDsRepository.all()
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter for all animals by days on app
            elif species == 'Any' and breed == "Any" and disposition == "Any" and days_on != "Any": # 2
                pet_data_all = PetDsRepository.all()
                pdata = filter_days_on(pet_data_all, days_on)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter for all animal by disposition
            elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on == "Any": # 3
                pet_data_all = PetDsRepository.all()
                pdata = filter_disposition(pet_data_all, disposition)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            #filter all by disposition and days on app
            elif species == 'Any' and breed == "Any" and disposition != "Any" and days_on != "Any": # 4
                pet_data_all = PetDsRepository.all()
                pdata_pre = filter_disposition(pet_data_all, disposition)
                pdata = filter_days_on(pdata_pre, days_on)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter by breed, species, or both
            # elif species == 'Any' and breed != "Any" and disposition == "Any" and days_on == "Any": # 5
            elif (((species == 'Any' and breed != "Any") or (species != 'Any' and breed == "Any") 
                    or (species != 'Any' and breed != "Any")) and disposition == "Any" and days_on == "Any"): # 5
                pet_data_all = PetDsRepository.all()
                pdata = filter_species_breed(pet_data_all, species, breed)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter by breed, species, or both by days on the app
            # elif species == 'Any' and breed != "Any" and disposition == "Any" and days_on != "Any": # 6
            elif (((species == 'Any' and breed != "Any") or (species != 'Any' and breed == "Any") 
                    or (species != 'Any' and breed != "Any")) and disposition == "Any" and days_on != "Any"): # 6
                pet_data_all = PetDsRepository.all()
                pdata_pre = filter_species_breed(pet_data_all, species, breed)
                pdata = filter_days_on(pdata_pre, days_on)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter by breed, species, or both for disposition
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on == "Any": # 7
            elif (((species == 'Any' and breed != "Any") or (species != 'Any' and breed == "Any") 
                    or (species != 'Any' and breed != "Any")) and disposition != "Any" and days_on == "Any"): # 7
                pet_data_all = PetDsRepository.all()
                pdata_pre = filter_species_breed(pet_data_all, species, breed)
                pdata = filter_disposition(pdata_pre, disposition)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)
            # filter by breed, species, or both for disposition and days on app
            # elif species == 'Any' and breed != "Any" and disposition != "Any" and days_on != "Any": # 8
            elif (((species == 'Any' and breed != "Any") or (species != 'Any' and breed == "Any") 
                    or (species != 'Any' and breed != "Any")) and disposition != "Any" and days_on != "Any"): # 8
                pet_data_all = PetDsRepository.all()
                pdata_pre = filter_species_breed(pet_data_all, species, breed)
                pdata_pre_2 = filter_disposition(pdata_pre, disposition)
                pdata = filter_days_on(pdata_pre_2, days_on)
                # print(species)
                # print(breed)
                # print(disposition)
                # print(days_on)

            # # filter by species 
            # elif species != 'Any' and breed == "Any" and disposition == "Any" and days_on == "Any": # 9
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_species_breed(pet_data_all, species, breed)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by species and days on app
            # elif species != 'Any' and breed == "Any" and disposition == "Any" and days_on != "Any": # 10
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by species and disposition
            # elif species != 'Any' and breed == "Any" and disposition != "Any" and days_on == "Any": # 11
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by species, disposition, and days on app
            # elif species != 'Any' and breed == "Any" and disposition != "Any" and days_on != "Any": # 12
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_2 = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_2, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # # filter by specieies and breed
            # elif species != 'Any' and breed != "Any" and disposition == "Any" and days_on =="Any": # 13
            #     pet_data_all = PetDsRepository.all()
            #     pdata = filter_species_breed(pet_data_all, species, breed)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by species and breed for specific days on app
            # elif species != 'Any' and breed != "Any" and disposition == "Any" and days_on !="Any": # 14
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by species and breed by disposition
            # elif species != 'Any' and breed != "Any" and disposition != "Any" and days_on =="Any": # 15
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # filter by all criterias
            # else: # elif species != 'Any' and breed != "Any" and disposition != "Any" and days_on !="Any": # 16
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata_pre_2 = filter_disposition(pdata_pre, disposition)
            #     pdata = filter_days_on(pdata_pre_2, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)

            # # no filtering just all 
            # if species == 'Any' and breed == "Any" and disposition == "Any"and days_on == "Any":
            #     pdata = PetDsRepository.all()
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            # # filter for all animals by disposition
            # elif species == 'Any' and breed == "Any" and disposition == "Any" and days_on !="Any":
            #     pdata_pre = PetDsRepository.all()
            #     pdata = filter_days_on(pdata_pre, days_on)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            # # filter for all animals by disposition
            # elif species == 'Any' and breed == "Any" and disposition != "Any":
            #     pdata_pre = PetDsRepository.all()
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print("Date time now: " +  str(days_on) + " " + str(datetime.now()))
            # # filter by species and disposition
            # elif species != 'Any' and breed == "Any" and disposition != "Any":
            #     pdata_pre = PetDsRepository.filter(species,breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     # print("Date time now: " +  str(days_on) + " " + str(datetime.now()))
            # # filter by breed and disposition
            # elif species == 'Any' and breed != "Any" and disposition != "Any":
            #     # pdata_pre = PetDsRepository.filter(species,breed)
            #     pet_data_all = PetDsRepository.all()
            #     pdata_pre = filter_species_breed(pet_data_all, species, breed)
            #     pdata = filter_disposition(pdata_filtered, disposition)
            #     # pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            #     # print("Date time now: " +  str(days_on) + " " + str(datetime.now()))
            # # filter by all criteria
            # elif species != 'Any' and breed != "Any" and disposition != "Any":
            #     pdata_pre = PetDsRepository.filter(species,breed)
            #     pdata = filter_disposition(pdata_pre, disposition)
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     # print("Date time now: " +  str(days_on) + " " + str(datetime.now()))
            # # filters by species and breed with any disposition
            # else:
            #     pdata = PetDsRepository.filter(species, breed)
            #     print("I'm in else")
            #     print(species)
            #     print(breed)
            #     print(disposition)
            #     print(days_on)
            #     # print("Date time now: " +  str(days_on) + " " + str(datetime.now()))

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
