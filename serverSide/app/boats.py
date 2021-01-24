###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer                                                                                    #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS493_400_F2020                                                                                     #
#                                                                                                             #
# This module peform CRUD operations for boats                                                                #
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

bp = Blueprint('boat', __name__)

CLIENT_ID = r'28610645966-l9g6bjn4eccktrl5es9564llt503rul7.apps.googleusercontent.com'
CLIENT_SECRET = r'gwZPBrrJWEG-vJFNpUzycPmU'

# Helper function to validate boat attributes
def _validateRequiredAttributes(content):
    # Required attributes are there
    if ("name" in content) and ("type" in content) and ("length" in content):
        return True
    # Required attributes are not there
    else:
        return False

# Helper function to validate boat attributes' data types
def _validateDataTypes(content):
    # Data types are as expected
    if isinstance(content['name'], str) and isinstance(content['type'], str) and isinstance(content['length'], int):
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

@bp.route('/boats', methods=['POST', 'PUT', 'DELETE'])
def create_boat():

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
               
        # Validate json formatting, then verify JWT, then store new boat
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
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            # Update datastore
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"], \
                "owner": sub, "loads": [], "creation_date": dt_string, "last_modified": None})
            client.put(new_boat)
            
            # Contruct response
            responseBody = {"id": new_boat.key.id, "name": content["name"], "type": content["type"], "length": content["length"], \
                "loads": [], "owner": sub, "self": "https://bauergr-final.wl.r.appspot.com/boats/" + str(new_boat.key.id)}
            return (json.dumps(responseBody), 201)
            
        else:
            responseBody = {"Error": "Missing one or more required attributes and/or data types are incorrect"}
            return (json.dumps(responseBody), 400)
            
    else:
        if (request.method == 'PUT') or (request.method == 'DELETE'):
            responseBody = {"Error": "PUT or DELETE not permitted on entire list of boats"}
            return (json.dumps(responseBody), 405)
        else:
            responseBody = {"Error": "Method not allowed!"}
            return (json.dumps(responseBody), 405)
            
###############################################################################################################
       
@bp.route('/boats', methods=['GET'])
def read_boats():
    
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
                
        # Get all boats from the datastore owned by user
        query = client.query(kind=constants.boats)
        query.add_filter("owner", "=", sub)
        
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
            r['self'] = 'https://bauergr-final.wl.r.appspot.com/boats/' + str(r.key.id)
        
        output = {"boats": results} 
        if next_url:
            output["next"] = next_url    
        
        return (json.dumps(output), 200)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
           
############################################################################################################### 

@bp.route('/boats/<boat_id>', methods=['GET'])
def get_boat(boat_id):
    
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
            
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
        
        # If results returned from datastore
        if boat is not None:
            boat['id'] = boat_id
            boat['self'] = 'https://bauergr-final.wl.r.appspot.com/boats/' + str(boat_id)
            return (json.dumps(boat), 200)
        else:
            responseBody = { "Error": "No boat with this boat_id exists" }
            return (json.dumps(responseBody), 403)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

###############################################################################################################

@bp.route('/boats/<boat_id>', methods=['PUT', 'PATCH'])
def update_boat(boat_id):
    
    # Record account modify date
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    
    # Complete boat replaces existing
    if request.method == 'PUT':
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
    
        # Check for properly formatted json in request body
        try:
            # Raises 'BadRequest' if fails
            content = request.get_json()
        except:
            responseBody = {"Error": "Not properly formatted JSON"}
            return (json.dumps(responseBody), 406)
        
        # Validate json formatting, then verify JWT, then store new boat
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
        
            # Check if boat exists
            if boat != None:
                # Are you the owner?
                if boat['owner'] == sub:
                    boat['name'] = content['name']
                    boat['type'] = content['type']
                    boat['length'] = content['length']
                    boat['last_modified'] = dt_string
                    client.put(boat)
                    return ('', 204)
                else:
                    responseBody = { "Error": "You do not own this boat" }
                    return (json.dumps(responseBody), 403)
            else:
                responseBody = { "Error": "No boat with this boat_id exists" }
                return (json.dumps(responseBody), 403)  
        else:
            # Not all attributes are contained within the request body or invalid data types are present
            responseBody = {"Error": "The request body is missing at least one of the required attributes or invalid data types are present"}
            return(json.dumps(responseBody), 400)
    
    # Update some attributes to existing boat, but not all
    elif request.method == 'PATCH':
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
        
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
        
        # Check if boat exists
        if boat != None:
            # Are you the owner?
            if boat['owner'] == sub:
                if 'name' in content:
                    boat['name'] = content['name']
                if 'type' in content:
                    boat['type'] = content['type']
                if 'length' in content:
                    boat['length'] = content['length']
                boat['last_modified'] = dt_string
                client.put(boat)
                return ('', 204)
            else:
                responseBody = { "Error": "You do not own this boat" }
                return (json.dumps(responseBody), 403)
        else:
            responseBody = { "Error": "No boat with this boat_id exists" }
            return (json.dumps(responseBody), 403) 
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

############################################################################################################### 

@bp.route('/boats/<boat_id>', methods=['DELETE'])
def delete_boat(boat_id):

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
            
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
        
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
        
            # Check if boat exists
            if boat != None:
        
                # Delete boat if owned by requestor
                if (boat['owner'] == sub):
                    # Remove loads from boat (do not delete)
                    for l in boat['loads']:
                        # Get load from datastore
                        load_key = client.key(constants.loads, int(l))
                        load = client.get(key=load_key)
                        load['loaded_on_boat'] = None
                        client.put(load)
                    # Delete boat on datastore
                    client.delete(boat_key)
                    return ('',204)
                
                elif (boat['owner'] != sub):
                    responseBody = { "Error": "You do not own this boat" }
                    return (json.dumps(responseBody), 403)   
            else:           
                responseBody = { "Error": "No boat with this boat_id exists" }
                return (json.dumps(responseBody), 403) 
               
        except: # JWT is not valid
            responseBody = {"Error": "Invalid JWT"}
            return (json.dumps(responseBody), 401) 
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
        
###############################################################################################################

@bp.route('/boats/<boat_id>/loads/<load_id>', methods=['PUT'])
def boats_assign_load(boat_id, load_id):
    
    if request.method == 'PUT':
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
        
        # Check if boat_id or load_id exists
        if ((load is None) or (boat is None)):
            responseBody = {"Error": "Load or Boat does not exist"}
            return (json.dumps(responseBody), 400)
        
        # Query the datastore of all boats using the contants file 'boats'
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        
        # Check if this load has already been assigned to any other boat
        for r in results:
            if str(load_id) in str(r['loads']):
                responseBody = {"Error": "Load has already been assigned to another boat"}
                return (json.dumps(responseBody), 400)
        
        # Update boat with load
        boat['loads'].append(load_id)
        client.put(boat)
        # Update load with carrier
        load['loaded_on_boat'] = boat_id
        client.put(load)
        
        return('', 204)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)

###############################################################################################################

@bp.route('/boats/<boat_id>/loads/<load_id>', methods=['DELETE'])
def boats_remove_load(boat_id, load_id):
    
    if request.method == 'DELETE':
        # Get boat key object from datastore
        boat_key = client.key(constants.boats, int(boat_id))
        # Retrieve desired boat from datastore
        boat = client.get(key=boat_key)
        # Get load key object from datastore
        load_key = client.key(constants.loads, int(load_id))
        # Retrieve desired load from datastore
        load = client.get(key=load_key)
        
        # Check if boat_id or load_id exists
        if ((load is None) or (boat is None)):
            responseBody = {"Error": "Load or Boat does not exist"}
            return (json.dumps(responseBody), 400)
            
        # Check if this load has been assigned to this boat
        if str(load_id) in str(boat['loads']):
            # Remove load from boat
            boat['loads'].remove(str(load_id))
            client.put(boat)
            load['loaded_on_boat'] = None
            client.put(load)
            return ('', 204)
        else:
            responseBody = {"Error": "Load has not been assigned to this boat"}
            return (json.dumps(responseBody), 400)
    else:
        responseBody = {"Error": "Method not allowed!"}
        return (json.dumps(responseBody), 405)
        
###############################################################################################################


                