###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer                                                                                    #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS493_400_F2020                                                                                     #
#                                                                                                             #
###############################################################################################################

from flask import Flask, Blueprint, render_template, session
import OAuth
#import users
#import boats
#import loads
import pets

# This disables the requirement to use HTTPS so that you can test locally.
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(OAuth.bp)
#app.register_blueprint(users.bp)
app.register_blueprint(pets.bp)

app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/admin_profiles', methods=['GET'])
def adminPage():
    if 'isAdmin' not in session:
        return "Page Not Found."
    elif session['isAdmin'] == False:
        return "Page Not Found."
    else:
        return render_template('admin_profiles.html')
    
    
@app.route('/add_profile', methods=["GET"])
def add_profile():
    if 'isAdmin' not in session:
        return "Page Not Found."
    elif session['isAdmin'] == False:
        return "Page Not Found."
    else:
        return render_template('add_profile.html')
        
    
    
@app.route('/update_profile', methods=["GET"])
def update_profile():
    if 'isAdmin' not in session:
        return "Page Not Found."
    elif session['isAdmin'] == False:
        return "Page Not Found."
    else:
        return render_template('update_profile.html')

        
@app.route('/profiles', methods=["GET"])
def view_profile():
    if 'sub' not in session:
        return "Page Not Found."
    else:
        return render_template('profiles.html')
        
    
@app.route('/news', methods=["GET"])
def news():
    if 'sub' not in session:
        return "Page Not Found."
    else:
        return render_template('news.html')

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
