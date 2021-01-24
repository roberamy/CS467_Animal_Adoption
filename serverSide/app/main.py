###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer                                                                                    #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS493_400_F2020                                                                                     #
#                                                                                                             #
###############################################################################################################

from flask import Flask, Blueprint
import OAuth
import users
import boats
import loads
import pets

# This disables the requirement to use HTTPS so that you can test locally.
import os 
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(OAuth.bp)
#app.register_blueprint(users.bp)
app.register_blueprint(pets.bp)

app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return "Please navigate to /home to use this app"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)