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

    def all():
        db = datastore.Client()
        query = db.query(kind='pets')
        return list(query.fetch())

    def filter(species,breed):
        db = datastore.Client()
        query = db.query(kind='pets')
        query.add_filter("type", "=", species)
        query.add_filter("breed", "=", breed)
        pets = list(query.fetch())
        return pets

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
          'profile_image_name': form['profile_image_name']
        })
      db.put(entity)
      return entity.key

    def update(form, key):
      db = datastore.Client()
      key = Key('pets',int(key),project='datingappforanimaladoption')
      entity = datastore.Entity(key=key)
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
          'profile_image_name': form['profile_image_name']
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
    

    def delete_profile(key):
      db = datastore.Client()
      ent_key = Key('pets',int(key),project='datingappforanimaladoption')
      entity = db.get(ent_key)
      db.delete(entity.key)

    
    def get(key):
      db = datastore.Client()
      ent_key = Key('pets',int(key),project='datingappforanimaladoption')
      entity = db.get(ent_key)
      return entity