###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                                                   #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# This module peform CRUD operations for pets entity                                                              #
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

client = datastore.Client()

bp = Blueprint('pets', __name__)

# Helper function to validate pet attributes
# TODO: need to figure out how to continue on next line
def _validateRequiredAttributes(content):
    # Required attributes are there
    if ("name" in content) and ("type" in content) and ("breed" in content) and ("disposition" in content) and ("availability" in content) and ("status" in content) and ("description" in content) and ("location" in content) and ("gender" in content):
        return True
    # Required attributes are not there
    else:
        return False

# Helper function to validate pet attributes' data types
# TODO: need to figure out how to continue on next line
def _validateDataTypes(content):
    # Data types are as expected
    if isinstance(content['name'], str) and isinstance(content['type'], str) and isinstance(content['breed'], str) and isinstance(content['disposition'], str) and isinstance(content['availability'], str) and isinstance(content['status'], str) and isinstance(content['location'], str) and isinstance(content['gender'], str):
        return True
    # Data types are incorrect for one or more attributes
    else:
        return False
            
# Helper function to validate 'Accept' in header of request
def _validateAcceptType(request):
    if request.headers['accept'] == 'application/json':
        return True
    else:
        return False
        
# Helper function to validate content-type in header of request
def _validateContentType(request):
    if request.headers['content-type'] == 'application/json':
        return True
    else:
        return False
        
###############################################################################################################


@bp.route('/pets', methods=['POST', 'PUT', 'DELETE'])
def create_pet():

    # Record account creation date
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    
    if request.method == 'POST':        
        # Request header ('content-type') must be JSON
        if not _validateContentType(request):
            responseBody = {"Error": "'content-type' sent must be JSON"}
            return (json.dumps(responseBody), 406)
        
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
               
        # Validate json formatting, then verify JWT, then store new pet
        if (_validateRequiredAttributes(content)) and (_validateDataTypes(content)):
            
            JWT = None
            sub = None
            # Get JWT from Authorization header
            try:
                JWT = request.headers.get('Authorization')
                JWT = JWT[7:]
            except:
                responseBody = {"Error": "Missing JWT"}
                return (json.dumps(responseBody), 401)
            
            try:
                # Grab 'sub' ID from JWT verification
                req = requests.Request()
                # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
                id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
                sub = id_info['sub']
            except:
                responseBody = {"Error": "Invalid JWT"}
                return (json.dumps(responseBody), 401)
                
            # Create new Entity in the datastore using constants file
            new_pet = datastore.entity.Entity(key=client.key(constants.pets))
            # Update datastore
            new_pet.update({"name": content["name"],
                            "type": content["type"],
                            "breed": content["breed"],
                            "disposition": content["disposition"],
                            "availability": content["availability"],
                            "status": content["status"],
                            "description": content["description"],
                            "adoption_date": None,
                            "date_created": dt_string,
                            "location": content["location"],
                            "adopted": False,
                            "adopted_by": None,
                            "owner": sub})
            client.put(new_pet)
            
            # Contruct response
            responseBody = {"id": new_pet.key.id, "name": content["name"], "type": content["type"], "breed": content["breed"], \
                "disposition": content["disposition"], "availability": content["availability"], \
                "status": content["status"], "description": content["description"], "adoption_date": None, \
                "date_created": dt_string, "location": content["location"], "adopted": False, "adopted_by": None, \
                "owner": sub, "self": "https://datingappforanimaladoption.wl.r.appspot.com/pets/" + str(new_pet.key.id)}
            return (json.dumps(responseBody), 201)
            
        else:
            responseBody = {"Error": "Missing one or more required attributes and/or data types are incorrect"}
            return (json.dumps(responseBody), 400)
            
    else:
        if (request.method == 'PUT') or (request.method == 'DELETE'):
            responseBody = {"Error": "PUT or DELETE not permitted on entire list of pets"}
            return (json.dumps(responseBody), 405)
        else:
            responseBody = {"Error": "Method not allowed!"}
            return (json.dumps(responseBody), 405)
            
###############################################################################################################
       
@bp.route('/pets', methods=['GET'])
def read_pets():
    
    if request.method == 'GET':  
        # Request header ('accept') must be application/json
        if not _validateAcceptType(request):
            responseBody = {"Error": "'accept' sent must be application/json"}
            return (json.dumps(responseBody), 406)
            
        JWT = None
        sub = None
        # Get JWT from Authorization header
        try:
            JWT = request.headers.get('Authorization')
            #JWT = JWT[7:]
        except:
            responseBody = {"Error": "Missing JWT"}
            return (json.dumps(responseBody), 401)
            
        try:
            # Grab 'sub' ID from JWT verification
            req = requests.Request()
            # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
            id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
            sub = id_info['sub']
            if sub != request.headers.get('Sub'):
                responseBody = {"Error": "Invalid JWT"}
                return (json.dumps(responseBody), 401)
        except:
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401)
                
        # Get all pets from the datastore owned by user
        query = client.query(kind=constants.pets)
        #query.add_filter("owner", "=", sub)
        results = list(query.fetch())
        
        # Set the number of files per page of pagination
        #b_limit = int(request.args.get('limit', '5'))
        ## Set the offset to begin next page of pagination
        #b_offset = int(request.args.get('offset', '0'))
        ## Iterator object to pages with limit and offset applied
        #b_iterator = query.fetch(limit= b_limit, offset=b_offset)
        #pages = b_iterator.pages
        #results = list(next(pages))
        ## If next page exists
        #if b_iterator.next_page_token:
        #    next_offset = b_offset + b_limit
        #    next_url = request.base_url + "?limit=" + str(b_limit) + "&offset=" + str(next_offset)
        #else:
        #    next_url = None
                
        # Add extra attributes to response
        for r in results:
            r['id'] = r.key.id
            r['self'] = constants.url + '/pets/' + str(r.key.id)
        
        #output = {"pets": results}
        #if next_url:
        #    output["next"] = next_url
        
        return (json.dumps(results), 200)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
           
############################################################################################################### 

@bp.route('/pets/<pet_id>', methods=['GET'])
def get_pet(pet_id):
    
    if request.method == 'GET':  
        # Request header ('accept') must be application/json
        if not _validateAcceptType(request):
            responseBody = {"Error": "'accept' sent must be application/json"}
            return (json.dumps(responseBody), 406)
            
        JWT = None
        sub = None
        # Get JWT from Authorization header
        try:
            JWT = request.headers.get('Authorization')
            JWT = JWT[7:]
        except:
            responseBody = {"Error": "Missing JWT"}
            return (json.dumps(responseBody), 401)
            
        try:
            # Grab 'sub' ID from JWT verification
            req = requests.Request()
            # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
            id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
            sub = id_info['sub']
            if sub != request.headers.get('Sub'):
                responseBody = {"Error": "Invalid JWT"}
                return (json.dumps(responseBody), 401)
        except:
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401)
            
        # Get pet key object from datastore
        pet_key = client.key(constants.pets, int(pet_id))
        # Retrieve desired pet from datastore
        pet = client.get(key=pet_key)
        
        # If results returned from datastore
        if pet is not None:
            pet['id'] = pet_id
            pet['self'] = constants.url + '/pets/' + str(pet_id)
            return (json.dumps(pet), 200)
        else:
            responseBody = { "Error": "No pet with this pet_id exists" }
            return (json.dumps(responseBody), 403)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

###############################################################################################################

@bp.route('/pets/<pet_id>', methods=['PUT', 'PATCH'])
def update_pet(pet_id):
    
    # Record account modify date
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    
    # Complete pet replaces existing
    if request.method == 'PUT':
        # Get pet key object from datastore
        pet_key = client.key(constants.pets, int(pet_id))
        # Retrieve desired pet from datastore
        pet = client.get(key=pet_key)
    
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
        
        # Validate json formatting, then verify JWT, then store new pet
        if (_validateRequiredAttributes(content)) and (_validateDataTypes(content)):
            
            JWT = None
            sub = None
            # Get JWT from Authorization header
            try:
                JWT = request.headers.get('Authorization')
                JWT = JWT[7:]
            except:
                responseBody = {"Error": "Missing JWT"}
                return (json.dumps(responseBody), 401)
            
            try:
                # Grab 'sub' ID from JWT verification
                req = requests.Request()
                # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
                id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
                sub = id_info['sub']
            except:
                responseBody = {"Error": "Invalid JWT"}
                return (json.dumps(responseBody), 401)
        
            # Check if pet exists
            if pet != None:
                # Are you the owner?
                if pet['owner'] == sub:
                    pet['name'] = content['name']
                    pet['type'] = content['type']
                    pet['breed'] = content['breed']
                    pet['disposition'] = content['disposition']
                    pet['availability'] = content['availability']
                    pet['status'] = content['status']
                    pet['description'] = content['description']
                    pet['location'] = content['location']
                    pet['gender'] = content['gender']
                    client.put(pet)
                    return ('', 204)
                else:
                    responseBody = { "Error": "You do not own this pet" }
                    return (json.dumps(responseBody), 403)
            else:
                responseBody = { "Error": "No pet with this pet_id exists" }
                return (json.dumps(responseBody), 403)  
        else:
            # Not all attributes are contained within the request body or invalid data types are present
            responseBody = {"Error": "The request body is missing at least one of the required attributes or invalid data types are present"}
            return(json.dumps(responseBody), 400)
    
    # Update some attributes to existing pet, but not all
    elif request.method == 'PATCH':
        # Get pet key object from datastore
        pet_key = client.key(constants.pets, int(pet_id))
        # Retrieve desired pet from datastore
        pet = client.get(key=pet_key)
        
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
            
        JWT = None
        sub = None
        # Get JWT from Authorization header
        try:
            JWT = request.headers.get('Authorization')
            JWT = JWT[7:]
        except:
            responseBody = {"Error": "Missing JWT"}
            return (json.dumps(responseBody), 401)
            
        try:
            # Grab 'sub' ID from JWT verification
            req = requests.Request()
            # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
            id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
            sub = id_info['sub']
        except:
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401)
        
        # Check if pet exists
        if pet != None:
            # Are you the owner?
            if pet['owner'] == sub:
                if 'name' in content:
                    pet['name'] = content['name']
                if 'type' in content:
                    pet['type'] = content['type']
                if 'breed' in content:
                    pet['breed'] = content['breed']
                if 'disposition' in content:
                    pet['disposition'] = content['disposition']
                if 'availability' in content:
                    pet['availability'] = content['availability']
                if 'status' in content:
                    pet['status'] = content['status']
                if 'description' in content:
                    pet['description'] = content['description']
                if 'location' in content:
                    pet['location'] = content['location']
                if 'gender' in content:
                    pet['gender'] = content['gender']
                client.put(pet)
                return ('', 204)
            else:
                responseBody = { "Error": "You do not own this pet" }
                return (json.dumps(responseBody), 403)
        else:
            responseBody = { "Error": "No pet with this pet_id exists" }
            return (json.dumps(responseBody), 403) 
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

############################################################################################################### 

@bp.route('/pets/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):

    if request.method == 'DELETE':
        
        # Request header ('accept') must be application/json
        if not _validateAcceptType(request):
            responseBody = {"Error": "'accept' sent must be application/json"}
            return (json.dumps(responseBody), 406)
            
        try:
            # Get JWT from Authorization header
            JWT = request.headers.get('Authorization')
            JWT = JWT[7:]
        except:
            responseBody = {"Error": "Missing JWT"}
            return (json.dumps(responseBody), 401)
            
        # Get pet key object from datastore
        pet_key = client.key(constants.pets, int(pet_id))
        # Retrieve desired pet from datastore
        pet = client.get(key=pet_key)
        
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
        
        try: # JWT is valid
            # Grab 'sub' ID from JWT verification
            req = requests.Request()
            id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
            sub = id_info['sub']
        
            # Check if pet exists
            if pet != None:
        
                # Delete pet if owned by requestor
                if (pet['owner'] == sub):
                    # Delete pet on datastore
                    client.delete(pet_key)
                    return ('',204)
                
                elif (pet['owner'] != sub):
                    responseBody = { "Error": "You do not own this pet" }
                    return (json.dumps(responseBody), 403)   
            else:           
                responseBody = { "Error": "No pet with this pet_id exists" }
                return (json.dumps(responseBody), 403) 
               
        except: # JWT is not valid
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401) 
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
        

###############################################################################################################
        
# @bp.route('/profiles', methods=["GET"])
# def view_profile():
#     printSession('***** ADOPT *****')
#     if 'sub' not in session:
#         return "sub not in session."
#     else:
#         return render_template('profiles.html')
