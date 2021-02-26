###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# Description: private singleton class that handles all interfaces with datastore                             #
#                                                                                                             #
# Ref: https://www.tutorialspoint.com/python_design_patterns/python_design_patterns_singleton.htm             #
#      https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html                          #
#      https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python                             #
#                                                                                                             #
# Note: The purpose of the singleton class is to control object creation, limiting the number of objects to   #
#       only one. The singleton allows only one entry point to create the new instance of the class. ...      #
#       Singletons are often useful where we have to control the resources, such as database connections or   #
#       sockets.  'https://www.google.com/search?q=why+use+a+singleton+class&rlz=1C1CHBD_enUS885US885         #
#                  &oq=why+use+a+singleton+class&aqs=chrome..69i57.6661j0j7&sourceid=chrome&ie=UTF-8          #                                                                                      #
###############################################################################################################

from google.cloud import datastore
from google.cloud.datastore.key import Key
import datetime


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})): pass


class PetDsRepository(Singleton):

    # Return all pets in datastore
    def all():
        db = datastore.Client()
        query = db.query(kind='pets')
        # sort in descending order (newest to oldest)
        query.order = ["-created_at"]
        return list(query.fetch())

    def filter(species, breed):
        db = datastore.Client()
        query = db.query(kind='pets')
        query.add_filter("type", "=", species)
        query.add_filter("breed", "=", breed)
        pets = list(query.fetch())
        return pets

    # Create new pet entity in datastore
    # Takes multi-part form as argument
    def create(form):
        db = datastore.Client()
        entity = datastore.Entity(key=db.key('pets'))
        now = datetime.datetime.now()
        entity.update({
            'age': form['age'],
            'name': form['name'],
            'availability': form['availability'],
            'breed': form['breed'],
            'description': form['description'],
            'gender': form['gender'],
            'location': form['location'],
            'status': form['status'],
            'properties': form['properties'],
            'type': form['type'],
            'created_at': now,
            'updated_at': now,
            'adoption_date': '',
            'adopted_by': '',
            'picked_up': False,
            'profile_image_name': form['profile_image_name']
        })
        db.put(entity)
        return entity.key

    # Update entity in datastore
    # Takes multi-part form as argument
    def update(form, key):
        db = datastore.Client()
        key = Key('pets', int(key), project='datingappforanimaladoption')
        # entity = datastore.Entity(key=key)

        entity = db.get(key)
        now = datetime.datetime.now()
        print("Form - PICKED UP:")
        print(form['picked_up'])
        if form['picked_up'] == "yes":
            pickedUp = True
        else:
            pickedUp = False
        entity.update({
            'age': form['age'],
            'name': form['name'],
            'availability': form['availability'],
            'breed': form['breed'],
            'description': form['description'],
            'gender': form['gender'],
            'location': form['location'],
            'status': form['status'],
            'properties': form['properties'],
            'type': form['type'],
            'updated_at': now,
            'adoption_date': form['adoption_date'],
            'adopted_by': form['adopted_by'],
            'picked_up': pickedUp,
            'profile_image_name': form['profile_image_name']
        })
        print('UPDATED ENTITY:')
        print(entity['picked_up'])
        db.put(entity)
        return entity.key

    def upload_image(image_name):
        db = datastore.Client()
        entity = datastore.Entity(key=db.key('profile_images'))
        entity.update({
            'image_name': image_name
        })
        db.put(entity)
        return entity.key

    def delete_profile(key):
        db = datastore.Client()
        ent_key = Key('pets', int(key), project='datingappforanimaladoption')
        entity = db.get(ent_key)
        db.delete(entity.key)

    def get(key):
        db = datastore.Client()
        ent_key = Key('pets', int(key), project='datingappforanimaladoption')
        entity = db.get(ent_key)
        return entity

    def getLatestStatus():
        db = datastore.Client()
        query = db.query(kind='pets')
        # sort in descending order (newest to oldest)
        query.order = ["-created_at"]
        data = list(query.fetch())
        available = []
        for d in data:
            if d['availability'] == 'Available':
                available.append(d)
        # print('AVAILABLE: ' + str(len(available)))
        if len(available) <= 6:
            return available
        else:
            return available[0:6]


class NewsRepository(Singleton):

    # Return all pets in datastore
    def all():
        db = datastore.Client()
        query = db.query(kind='news')
        # sort in descending order (newest to oldest)
        query.order = ["-created"]
        return list(query.fetch())

    # Create new 'news' entity in datastore
    # Takes multi-part form as argument
    def create(form):
        db = datastore.Client()
        entity = datastore.Entity(key=db.key('news'))
        now = datetime.datetime.now()
        entity.update({
            'title': form['title'],
            'content': form['content'],
            'author': form['author'],
            'created': now,
            'updated': now,
            'news_image_name': form['profile_image_name']
        })
        db.put(entity)
        return entity.key

    # Update entity in datastore
    # Takes multi-part form as argument
    def update(form, key):
        db = datastore.Client()
        key = Key('news', int(key), project='datingappforanimaladoption')
        # entity = datastore.Entity(key=key)
        entity = db.get(key)
        now = datetime.datetime.now()
        entity.update({
            'title': form['title'],
            'content': form['content'],
            'author': form['author'],
            'updated': now,
            'news_image_name': form['profile_image_name']
        })
        db.put(entity)
        return entity.key

    def upload_image(image_name):
        db = datastore.Client()
        entity = datastore.Entity(key=db.key('profile_images'))
        entity.update({
            'image_name': image_name
        })
        db.put(entity)
        return entity.key

    def delete_news(key):
        db = datastore.Client()
        ent_key = Key('news', int(key), project='datingappforanimaladoption')
        entity = db.get(ent_key)
        db.delete(entity.key)

    def get(key):
        db = datastore.Client()
        ent_key = Key('news', int(key), project='datingappforanimaladoption')
        entity = db.get(ent_key)
        return entity
