###############################################################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description: Launches web application by serving up landing page
#
# Note: Main should be clear of excessive routes. All other routes have been modularized and placed in
# separate python modules.
#
###############################################################################################################

from flask import Flask, Blueprint, render_template, session, redirect
import OAuth
import pets
import users
import admin
import news
import adopt_profiles
import applications

# This disables the requirement to use HTTPS so that you can test locally.
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(OAuth.bp)
app.register_blueprint(users.bp)
app.register_blueprint(pets.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(news.bp)
app.register_blueprint(adopt_profiles.bp)
app.register_blueprint(applications.bp)

app.secret_key = os.urandom(24)

###############################################################################################################

#Landing page with google login
@app.route('/')
def index():
    return render_template('index.html') 
  
###############################################################################################################

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return render_template('index.html')

###############################################################################################################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
