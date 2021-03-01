###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description:
# Launches web application by serving up landing page
#
# Note:
# Main should be clear of excessive routes. All other routes have been
# modularized and placed in separate python modules.
#
# References:
# https://stackoverflow.com/questions/53176162/google-oauth-scope-changed-during-authentication-but-scope-is-same
# https://stackoverflow.com/questions/22669528/securely-storing-environment-variables-in-gae-with-app-yaml?rq=1
# https://stackoverflow.com/questions/18709213/flask-session-not-persisting
###############################################################################

from flask import Flask, render_template, session, redirect
import OAuth
import pets
import users
import admin
import news
import adopt
import applications
import constants
from repository import PetDsRepository


import os
# This disables the requirement to use HTTPS so that you can test locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Disables scope change warning
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)

app.register_blueprint(OAuth.bp)
app.register_blueprint(users.bp)
app.register_blueprint(pets.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(news.bp)
app.register_blueprint(adopt.bp)
app.register_blueprint(applications.bp)

# app.secret_key = os.urandom(24)
app.secret_key = constants.SECRET_KEY

###############################################################################


# Landing page with google login
@app.route('/')
def index():
    status = PetDsRepository.getLatestStatus()
    return render_template('index.html',
                           status=status,
                           public_url=constants.BUCKET)

###############################################################################


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

###############################################################################


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
