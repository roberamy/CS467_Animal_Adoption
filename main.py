

import os

from flask import Flask, render_template, request, Response



app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return render_template('index.html')

@app.route("/admin_profiles", methods=["GET"])
def admin_profiles():
    return render_template('admin_profiles.html')

@app.route("/add_profile", methods=["GET"])
def add_profile():
    return render_template('add_profile.html')
    
@app.route("/update_profile", methods=["GET"])
def update_profile():
    return render_template('update_profile.html')

# Jasper Added
@app.route("/adopt_cat", methods=["GET"])
def adopt_cat():
    return render_template('adopt_cat.html') 

@app.route("/adopt_dog", methods=["GET"])
def adopt_dog():
    return render_template('adopt_dog.html') 

@app.route("/adopt_other_pets", methods=["GET"])
def adopt_other_pets():
    return render_template('adopt_other_pets.html') 

@app.route("/log_in", methods=["GET"])
def log_in():
    return render_template('log_in.html') 

@app.route("/news_list", methods=["GET"])
def news_list():
    return render_template('news_list.html')

@app.route("/news_post", methods=["GET"])
def news_post():
    return render_template('news_post.html')

@app.route("/service_page", methods=["GET"])
def service_page():
    return render_template('service_page.html')

@app.route("/sign_up", methods=["GET"])
def sign_up():
    return render_template('sign_up.html')

# 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
