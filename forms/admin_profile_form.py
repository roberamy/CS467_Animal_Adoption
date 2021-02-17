###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# Description: Form validation package used in 'add_profile' template. Creates form class with form           #
#              fields and pertinent validation rules                                                          #
#                                                                                                             #
# ref: https://wtforms.readthedocs.io/en/2.3.x/crash_course/                                                  #
#                                                                                                             #
###############################################################################################################

from wtforms import *
from google.cloud import datastore
import constants


client = datastore.Client()


# Function gets & formats breed types from database for form validation
def petBreeds():
    query = client.query(kind=constants.breeds)
    query.order = ["name"]
    breeds = list(query.fetch())
    breed_options = []
    # length = 0
    for e in breeds:
        # option = e["name"]
        breed_options.append(e["name"])
    return breed_options


class AdminProfileForm(Form):
    ''' Form Field Options '''
    type_select = [('Cat', 'Cat'),('Dog', 'Dog'),('Other', 'Other')]
    breed_select = petBreeds()
    #breed_select = [('Abyssinian','Abyssinian'), ('Akita','Akita'), ('Alaskan Malamute','Alaskan Malamute'), ('American Shorthair','American Shorthair'), ('Australian Shepherd','Australian Shepherd'), ('Basset Hound','Basset Hound'), ('Bearded Dragon','Bearded Dragon'), ('Bernese Mountain Dog','Bernese Mountain Dog'), ('Border Collie','Border Collie'), ('Boxer','Boxer'), ('Bull Terrier','Bull Terrier'), ('Bulldog','Bulldog'), ('Bullmastiff','Bullmastiff'), ('Burmese','Burmese'), ('Canarie','Canarie'), ('Cavalier King Charles Spaniel','Cavalier King Charles Spaniel'), ('Chameleon','Chameleon'), ('Chihuahua','Chihuahua'), ('Chinchilla','Chinchilla'), ('Chow Chow','Chow Chow'), ('Cockatiel','Cockatiel'), ('Cockatoo','Cockatoo'), ('Cocker Spaniel','Cocker Spaniel'), ('Collie','Collie'), ('Corgi','Corgi'), ('Dachshund','Dachshund'), ('Dalmatian','Dalmatian'), ('Doberman Pinscher','Doberman Pinscher'), ('Domestic Longhair','Domestic Longhair'), ('Finch','Finch'), ('French Bulldog','French Bulldog'), ('Gecko','Gecko'), ('Gerbil','Gerbil'), ('German Shepherd','German Shepherd'), ('Golden Retriever','Golden Retriever'), ('Great Dane','Great Dane'), ('Guinea Pig','Guinea Pig'), ('Hamster','Hamster'), ('Himalayan','Himalayan'), ('Iguana','Iguana'), ('Labrador Retriever','Labrador Retriever'), ('Macaw','Macaw'), ('Maine Coon','Maine Coon'), ('Manx','Manx'), ('Mouse','Mouse'), ('Newfoundland','Newfoundland'), ('Papillon','Papillon'), ('Parakeet','Parakeet'), ('Parrot','Parrot'), ('Pekingese','Pekingese'), ('Persian','Persian'), ('Pomeranian','Pomeranian'), ('Poodle','Poodle'), ('Pug','Pug'), ('Ragdoll','Ragdoll'), ('Rat','Rat'), ('Rottweiler','Rottweiler'), ('Russell Terrier','Russell Terrier'), ('Shiba Inu','Shiba Inu'), ('Siamese','Siamese'), ('Siberian Husky','Siberian Husky'), ('Sphynx','Sphynx'), ('Springer Spaniel','Springer Spaniel'), ('St. Bernard','St. Bernard'), ('Weimaraner','Weimaraner'), ('Yorkshire Terrier','Yorkshire Terrier')]
    age_select = [('Adult','Adult'),('Baby','Baby'),('Senior','Senior'),('Young','Young')]
    gender_select = [('Male', 'Male'),('Female', 'Female')]
    availability_select = [('Adopted','Adopted'),('Available','Available'),('Pending','Pending'),('Not Available','Not Available')]
    ''' End Form Field Options '''
    ''' Begin Form Validation Options '''
    name = StringField('Enter Name', [validators.Length(min=3), validators.InputRequired()])
    type = SelectField(u'Type',choices = type_select, validators=[validators.InputRequired()])
    breed = SelectField(u'Breed',choices = breed_select, validators=[validators.InputRequired()])
    age = SelectField(u'Age', choices = age_select,validators=[validators.InputRequired()])
    gender = SelectField(u'Gender',choices = gender_select,validators=[validators.InputRequired()])
    status = StringField('Status',[validators.Length(min=3), validators.InputRequired()])
    description = TextAreaField('Description',[validators.Length(min=3), validators.InputRequired()])
    location = StringField('Location',[validators.Length(min=3), validators.InputRequired()])
    availability = SelectField(u'Availability',choices = availability_select,validators=[validators.InputRequired()])
    properties = StringField('Properties', [validators.InputRequired()])
    adoption_date = StringField('adoption_date')
    adopted_by = StringField('adopted_by')
    picked_up = StringField('picked_up')
    profile_image = FileField('Image')
    ''' End Form Validation Options '''
