###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description: Routes for news pages
#
# Note:
#
# References:
# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# https://pythonhosted.org/Flask-paginate/
# https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9
###############################################################################

# Library modules
from flask import Blueprint, request, redirect, render_template
from flask import session
from flask_paginate import Pagination, get_page_args
from google.cloud import datastore
import json
from datetime import datetime
from os.path import join, dirname, realpath
# User modules
from repository import NewsRepository
from forms.news_form import NewsForm
from OAuth import printSession
import news
import constants

UPLOADS_PATH = join(dirname(realpath(__file__)), 'uploads/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

bp = Blueprint('news', __name__)
client = datastore.Client()

###############################################################################


# helper pagination function
def get_news_page(data, offset=0, per_page=10):
    return data[offset: offset + per_page]


# General user view of news posts
@bp.route('/news', methods=["GET"])
def get_news():
    printSession('***** NEWS *****')
    if 'sub' not in session:
        # return "sub not in session."
        return redirect('/')
    else:
        data = NewsRepository.all()
        total = len(data)
        # print('LENGHT: ' + str(total))
        for d in data:
            d['created'] = datetime.strftime(d['created'], "%B %d, %Y")
        # pagination code
        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')
        pagination_news = get_news_page(data, offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap4')
        return render_template('news.html',
                               news=pagination_news,
                               page=page,
                               per_page=per_page,
                               pagination=pagination,
                               public_url=constants.BUCKET)

###############################################################################


# Route to add/edit a news post
@bp.route('/add_news', methods=["GET"])
def add_news():
    printSession('***** ADD NEWS *****')
    if 'isAdmin' not in session:
        return "isAdmin not in session."
        # return redirect('/')
    elif session['isAdmin'] is False:
        # return "Not an admin account."
        return redirect('/')
    else:
        form = NewsForm()
        return render_template('news_add_edit.html',
                               form=form,
                               public_url=constants.BUCKET)

###############################################################################


# Route to render update news post template
@bp.route('/update_news/<key>', methods=["GET"])
def update_news(key):
    printSession('***** UPDATE NEWS *****')
    petNews = NewsRepository.get(key)
    print(news)
    # print(pet['type'])
    if 'isAdmin' not in session:
        # return "isAdmin not in session."
        return redirect('/')
    elif session['isAdmin'] is False:
        # return "Not an admin account."
        return redirect('/')
    else:
        return render_template('news_add_edit.html',
                               pet=petNews,
                               public_url=constants.BUCKET)

###############################################################################


# Route to store updated news post
@bp.route('/store_news', methods=["POST"])
def store_news():
    # Instantiate AdminProfileForm class used for input validation
    form = NewsForm(request.form)
    if form.validate():
        # Create new 'news' entity in data store if no key provided
        if request.form['pet_key'] == '':
            NewsRepository.create(request.form)
        # Update 'news' entity if key provided
        else:
            NewsRepository.update(
                form=request.form, key=request.form['pet_key'])
        responseBody = {"success": True, "message": "Data Successfully saved"}
    else:
        # errors = []
        for fieldName, errorMessages in form.errors.items():
            # field = []
            print(fieldName)
            for err in errorMessages:
                print(err)
        responseBody = {"success": False,
                        "message": fieldName.title() + ': ' + err}
    return (json.dumps(responseBody), 200)

###############################################################################


# Route for admin view of all news posts
@bp.route('/admin_news', methods=["GET"])
def news_admin():
    printSession('***** NEWS ADMIN *****')
    if 'isAdmin' not in session:
        return "isAdmin not in session."
        # return redirect('/')
    elif session['isAdmin'] is False:
        return "Not an admin account."
        # return redirect('/')
    else:
        # Return all 'news' entities to populate 'admin_news.html'
        # Instantiate singleton NewsRepository class with member functions
        # See 'repository.py'
        data = NewsRepository.all()
        # print(data)
        for d in data:
            d['created'] = datetime.strftime(d['created'], "%Y-%m-%d")
        return render_template('news_admin.html', news=data)

###############################################################################


# Route to delete news post from datastore
@bp.route('/delete_news', methods=["POST"])
def delete_post():
    key = request.form['key']
    # Instantiate singleton NewsRepository class with member functions
    # See 'repository.py'
    NewsRepository.delete_news(key=key)
    responseBody = {"success": True, "message": "Deleted"}
    return (json.dumps(responseBody), 200)
