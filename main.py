

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
@app.route("/sign_up", methods=["GET"])
def sign_up():
    return render_template('sign_up.html') 

# 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
