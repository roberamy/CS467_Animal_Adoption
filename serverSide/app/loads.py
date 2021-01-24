###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer                                                                                    #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS493_400_F2020                                                                                     #
#                                                                                                             #
# This module peform CRUD operations for loads                                                                #
#                                                                                                             #
###############################################################################################################

from flask import Blueprint, request, Response
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime

client = datastore.Client()

bp = Blueprint('load', __name__)

CLIENT_ID = r'28610645966-l9g6bjn4eccktrl5es9564llt503rul7.apps.googleusercontent.com'
CLIENT_SECRET = r'gwZPBrrJWEG-vJFNpUzycPmU'

# Helper function to validate load attributes
def _validateRequiredAttributes(content):
    # Required attributes are there
    if ("weight" in content) and ("content" in content) and ("delivery_date" in content):
        return True
    # Required attributes are not there
    else:
        return False

# Helper function to validate load attributes' data types
def _validateDataTypes(content):
    # Data types are as expected
    if isinstance(content['weight'], int) and isinstance(content['content'], str) and isinstance(content['delivery_date'], str):
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

@bp.route('/loads', methods=['POST', 'PUT', 'DELETE'])
def create_load():

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
               
        # Validate json formatting, then verify JWT, then store new load
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
            new_load = datastore.entity.Entity(key=client.key(constants.loads))
            # Update datastore
            new_load.update({"weight": content["weight"], "content": content["content"], "delivery_date": content["delivery_date"], \
                "owner": sub, "loaded_on_boat": None, "creation_date": dt_string, "last_modified": None})
            client.put(new_load)
            
            # Contruct response
            responseBody = {"id": new_load.key.id, "weight": content["weight"], "content": content["content"], "delivery_date": content["delivery_date"], \
                "loaded_on_boat": None, "owner": sub, "self": "https://bauergr-final.wl.r.appspot.com/loads/" + str(new_load.key.id)}
            return (json.dumps(responseBody), 201)
            
        else:
            responseBody = {"Error": "Missing one or more required attributes and/or data types are incorrect"}
            return (json.dumps(responseBody), 400)
            
    else:
        if (request.method == 'PUT') or (request.method == 'DELETE'):
            responseBody = {"Error": "PUT or DELETE not permitted on entire list of loads"}
            return (json.dumps(responseBody), 405)
        else:
            responseBody = {"Error": "Method not allowed!"}
            return (json.dumps(responseBody), 405)
            
###############################################################################################################
       
@bp.route('/loads', methods=['GET'])
def read_loads():
    
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
            id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
            sub = id_info['sub']
        except:
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401)
                
        # Get all loads from the datastore owned by user
        query = client.query(kind=constants.loads)
                
        # Set the number of files per page of pagination
        b_limit = int(request.args.get('limit', '5'))
        # Set the offset to begin next page of pagination
        b_offset = int(request.args.get('offset', '0'))
        # Iterator object to pages with limit and offset applied
        b_iterator = query.fetch(limit= b_limit, offset=b_offset)
        pages = b_iterator.pages
        results = list(next(pages))
        # If next page exists
        if b_iterator.next_page_token:
            next_offset = b_offset + b_limit
            next_url = request.base_url + "?limit=" + str(b_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
                
        # Add extra attributes to response
        for r in results:
            r['id'] = r.key.id
            r['self'] = 'https://bauergr-final.wl.r.appspot.com/loads/' + str(r.key.id)
        
        output = {"loads": results} 
        if next_url:
            output["next"] = next_url    
        
        return (json.dumps(output), 200)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
           
############################################################################################################### 

@bp.route('/loads/<load_id>', methods=['GET'])
def get_load(load_id):
    
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
            id_info = id_token.verify_oauth2_token(JWT, req, CLIENT_ID)
            sub = id_info['sub']
        except:
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401)
            
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
        
        # If results returned from datastore
        if load is not None:
            load['id'] = load_id
            load['self'] = 'https://bauergr-final.wl.r.appspot.com/loads/' + str(load_id)
            return (json.dumps(load), 200)
        else:
            responseBody = { "Error": "No load with this load_id exists" }
            return (json.dumps(responseBody), 404)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

###############################################################################################################

@bp.route('/loads/<load_id>', methods=['PUT', 'PATCH'])
def update_load(load_id):
    
    # Record account modify date
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    
    # Complete load replaces existing
    if request.method == 'PUT':
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
    
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
        
        # Validate json formatting, then verify JWT, then store new load
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
        
            # Check if load exists
            if load != None:   
                load['weight'] = content['weight']
                load['content'] = content['content']
                load['delivery_date'] = content['delivery_date']
                load['last_modified'] = dt_string
                client.put(load)
                return ('', 204)
            else:
                responseBody = { "Error": "No load with this load_id exists" }
                return (json.dumps(responseBody), 403)  
        else:
            # Not all attributes are contained within the request body or invalid data types are present
            responseBody = {"Error": "The request body is missing at least one of the required attributes or invalid data types are present"}
            return(json.dumps(responseBody), 400)
    
    # Update some attributes to existing load, but not all
    elif request.method == 'PATCH':
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
        
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
        
        # Check if load exists
        if load != None:
            if 'weight' in content:
                load['weight'] = content['weight']
            if 'content' in content:
                load['content'] = content['content']
            if 'delivery_date' in content:
                load['delivery_date'] = content['delivery_date']
            load['last_modified'] = dt_string
            client.put(load)
            return ('', 204)
        else:
            responseBody = { "Error": "No load with this load_id exists" }
            return (json.dumps(responseBody), 403) 
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

############################################################################################################### 

@bp.route('/loads/<load_id>', methods=['DELETE'])
def delete_load(load_id):

    if request.method == 'DELETE':
    
        try:
            # Get JWT from Authorization header
            JWT = request.headers.get('Authorization')
            JWT = JWT[7:]
        except:
            responseBody = {"Error": "Missing JWT"}
            return (json.dumps(responseBody), 401)
            
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
        
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
        
            # Check if load exists
            if load != None:
        
                # Get boat from datastore
                if load['loaded_on_boat'] != None:
                    boat_key = client.key(constants.boats, int(load['loaded_on_boat']))
                    boat = client.get(key=boat_key)
                    boat['loads'].remove(load.key.id)
                # Delete load on datastore
                client.delete(load_key)
                return ('',204)                    
            else:
                responseBody = { "Error": "No load with this load_id exists" }
                return (json.dumps(responseBody), 403) 
               
        except: # JWT is not valid
           responseBody = {"Error": "Invalid JWT"}
           return (json.dumps(responseBody), 401)   
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
        
###############################################################################################################


                