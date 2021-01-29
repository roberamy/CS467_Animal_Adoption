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
  
# # manual type to admin index until integration 
# @app.route("/", methods=["GET"])
# def root():
#     return render_template('index_j.html')

# @app.route("/admin", methods=["GET"])
# def root_admin():
# return render_template('index.html')

    
    
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

# Jasper Added


# @app.route("/adopt_cat", methods=["GET"])
# def adopt_cat():
#     return render_template('adopt_cat.html') 

# @app.route("/adopt_dog", methods=["GET"])
# def adopt_dog():
#     return render_template('adopt_dog.html') 

# @app.route("/adopt_other_pets", methods=["GET"])
# def adopt_other_pets():
#     return render_template('adopt_other_pets.html') 

@app.route("/log_in", methods=["GET"])
def log_in():
    return render_template('log_in_j.html') 

@app.route("/news_list", methods=["GET"])
def news_list():
    return render_template('news_list.html')

@app.route("/news_post", methods=["GET"])
def news_post():
    return render_template('news_post.html')

@app.route("/pet_page", methods=["GET"])
def pet_page():
    return render_template('pet_page.html')

@app.route("/service_page", methods=["GET"])
def service_page():
    return render_template('service_page.html')

# @app.route("/sign_up", methods=["GET"])
# def sign_up():
#     return render_template('sign_up_j.html')

# 


    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
