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
# References:
# 
###############################################################################################################

from flask import Blueprint, request, Response, redirect, render_template, session, make_response
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
import json
import constants
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests
from datetime import datetime
#import requests
bp = Blueprint('profiles', __name__)
client = datastore.Client()

from OAuth import printSession

###############################################################################################################

# @bp.route('/admin', methods=['GET'])
# def adminPage():
#     printSession('***** ADMIN PROFILES *****')
#     if 'sub' not in session:
#         #return redirect('/')
#         return "Error: \'sub\' not in session."
#     elif 'isAdmin' not in session:
#         #return redirect('/')
#         return "Error: \'isAdmin\' not in session."
#     elif session['isAdmin'] == False:
#         #return redirect('/')
#         return "Error: Not an admin account."
#     else:
#     #    # POST request to /pets API
#     #    response = None
#     #    response = requests.get(constants.url + '/pets',
#     #        headers={'Accept': 'application/json', 'Authorization': session['id_token'], 'Sub': session['sub']})
#     #    if response == None:
#     #        print ('No response received.')
#     #    else:
#     #        print ('Response received.')
#     #        print(response.status_code)
#     #        print(response.text)
#     #        profiles = json.loads(response.text)
#     #        print(profiles)
#     #        return render_template('admin_profiles.html', profiles=profiles)

#         # Direct requests to GAE database
#         if request.method == 'GET':
#             JWT = session['id_token']
#             # Grab 'sub' ID from JWT verification
#             req = requests.Request()
#             # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
#             id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
#             if session['sub'] != id_info['sub']:
#                 return 'Error": "Invalid JWT'
#             # Get all pets from the datastore owned by user
#             query = client.query(kind=constants.pets)
#             profiles = list(query.fetch())
#             for r in profiles:
#                 r['id'] = r.key.id
#                 r['self'] = constants.url + '/pets/' + str(r.key.id)
#             return render_template('admin_profiles.html', profiles=profiles)
#         else:
#             return redirect('/')
        
# ###############################################################################################################
    
# @bp.route('/delete/<profile_id>')
# def delete_profile(profile_id):
#     printSession('***** DELETE PROFILES *****')
#     print('PROFILE ID: ' + profile_id)
#     if 'sub' not in session:
#         return "Error: \'sub\' not in session."
#         #return redirect('/')
#     elif 'isAdmin' not in session:
#         return "Error: \'isAdmin\' not in session."
#         #return redirect('/')
#     elif session['isAdmin'] == False:
#         return "Error: Not an admin account."
#         #return redirect('/')
#     else:
#         # Direct requests to GAE database
#         JWT = session['id_token']
#         # Grab 'sub' ID from JWT verification
#         req = requests.Request()
#         # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
#         id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
#         if session['sub'] != id_info['sub']:
#             return 'Error": "Invalid JWT'
#         # User validated, send delete request
#         else:
#             #print('Valid JWT & SUB...')
#             # Get pet key object from datastore
#             profile_key = client.key(constants.pets, int(profile_id))
#             # Retrieve desired pet from datastore
#             profile = client.get(key=profile_key)
#             # If profile exists, delete
#             if profile:
#                 client.delete(profile_key)
#             return redirect('/admin')
        
# ###############################################################################################################
    
# @bp.route('/view/<profile_id>')
# def view_profile(profile_id):
#     printSession('***** VIEW PROFILE *****')
#     print('PROFILE ID: ' + profile_id)
#     if 'sub' not in session:
#         return "Error: \'sub\' not in session."
#         #return redirect('/')
#     elif 'isAdmin' not in session:
#         return "Error: \'isAdmin\' not in session."
#         #return redirect('/')
#     elif session['isAdmin'] == False:
#         return "Error: Not an admin account."
#         #return redirect('/')
#     else:
#     # Direct requests to GAE database
#         JWT = session['id_token']
#         # Grab 'sub' ID from JWT verification
#         req = requests.Request()
#         # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
#         id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
#         if session['sub'] != id_info['sub']:
#             return 'Error": "Invalid JWT'
#         # User validated, send delete request
#         else:
#             #print('Valid JWT & SUB...')
#             # Get pet key object from datastore
#             profile_key = client.key(constants.pets, int(profile_id))
#             # Retrieve desired pet from datastore
#             profile = client.get(key=profile_key)
#             # If profile exists, delete
#             if profile:
#                 print(profile['adopted'])
#                 return render_template('update_profile.html', profile=profile)
#             else:
#                 return 'Error": "Invalid profile ID'
#                 #return redirect('/admin')
        
# ###############################################################################################################
    
# @bp.route('/update/<profile_id>', methods=['POST'])
# def update_profile(profile_id):
#     printSession('***** ADMIN PROFILES *****')
#     print('PROFILE ID: ' + profile_id)
#     if 'sub' not in session:
#         return "Error: \'sub\' not in session."
#         #return redirect('/')
#     elif 'isAdmin' not in session:
#         return "Error: \'isAdmin\' not in session."
#         #return redirect('/')
#     elif session['isAdmin'] == False:
#         return "Error: Not an admin account."
#         #return redirect('/')
#     else:
#         # Direct requests to GAE database
#         JWT = session['id_token']
#         # Grab 'sub' ID from JWT verification
#         req = requests.Request()
#         # Raises: exceptions.GoogleAuthError – If the issuer is invalid.
#         id_info = id_token.verify_oauth2_token(JWT, req, constants.CLIENT_ID)
#         if session['sub'] != id_info['sub']:
#             return 'Error": "Invalid JWT'
#         # User validated, send delete request
#         else:
#             #print('Valid JWT & SUB...')
#             # Get pet key object from datastore
#             profile_key = client.key(constants.pets, int(profile_id))
#             # Retrieve desired pet from datastore
#             profile = client.get(key=profile_key)
#             # If profile exists, delete
#             if profile:
#                 print("PROFILE exists...")
#                 print(profile)
#                 print("***** Getting Form Data *****")
#                 formData = request.form
#                 print("FORM DATA:")
#                 print(formData)
#                 if formData['name']:
#                     profile['name'] = formData['name']
#                 if formData['type']:
#                     profile['type'] = formData['type']
#                 if formData['breed']:
#                     profile['breed'] = formData['breed']
#                 # TODO handle disposition checkbox results
#                 #profile['disposition'] = formData['disposition']
#                 #TO DO handle photo(s)
#                 if formData['status']:
#                     profile['status'] = formData['status']
#                 if formData['description']:
#                     profile['description'] = formData['description']
#                 if formData['location']:
#                     profile['location'] = formData['location']
#                 if formData['gender']:
#                     profile['gender'] = formData['gender']
#                 if formData['availability']:
#                     profile['availability'] = formData['availability']
#                     #If 'availability' selection in form is 'Adopted', update adopted boolean to true
#                     if formData['availability'] == 'Adopted':
#                         adopted = True
#                         if formData['adoption_date']:
#                             profile['adoption_date'] = formData['adoption_date']
#                         if formData['adopted_by']:
#                             profile['adopted_by'] = formData['adopted_by']
#                     #Other option besides 'Adopted' selected for 'availability', clear 'adoption_date' & 'adopted_by'
#                     else:
#                         adopted = False
#                         profile['adoption_date'] = ""
#                         profile['adopted_by'] = ""
#                     #update profile 'adopted' boolean
#                     profile['adopted'] = adopted
#                 client.put(profile)
#             return redirect('/admin')
# ###############################################################################################################
# @bp.route('/add_profile', methods=["GET"])
# def add_profile():
#     if 'isAdmin' not in session:
#         return "isAdmin not in session."
#     elif session['isAdmin'] == False:
#         return "Not an admin account."
#     else:
#         return render_template('add_profile.html')
        
# ###############################################################################################################