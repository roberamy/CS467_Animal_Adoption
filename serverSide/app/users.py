###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer                                                                                    #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS493_400_F2020                                                                                     #
#                                                                                                             #
###############################################################################################################

from flask import Blueprint, request, Response, redirect, render_template, session
import json
import requests
from google.cloud import datastore
import constants

bp = Blueprint('users', __name__)
client = datastore.Client()

###############################################################################################################

@bp.route('/users', methods=['GET'])
def getUsers():
       
    # Get all users from the datastore
    query = client.query(kind=constants.users)
    results = list(query.fetch())
    
    # Store users for return 
    responseBody = []
    for r in results:
        r["self"] = 'https://bauergr-final.wl.r.appspot.com/boats/' + str(r.key.id)
        responseBody.append(r)
             
    return (json.dumps(responseBody), 200)
    
    
###############################################################################################################