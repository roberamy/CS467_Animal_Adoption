###############################################################################################################
#                                                                                                             #          
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        #
# Email: bauergr@oregonstate.edu                                                                              #
# Course: CS467_400_W2021                                                                                     #
#                                                                                                             #
# Description: Form validation package used in 'add_profile' template. Creates form class with form           #
#              fields and pertinent validation rules                                                          #
#                                                                                                             #
# ref: https://wtforms.readthedocs.io/en/2.3.x/crash_course/                                                  #                                                                        #
#                                                                                                             #
###############################################################################################################

from wtforms import *

class AdminProfileForm(Form):
    ''' Form Field Options '''
    type_select = [('Cat', 'Cat'),('Dog', 'Dog'),('Other', 'Other')]
    breed_select = [('American Shorthair','American Shorthair'),('German Shepherd','German Shepherd'),
    ('Golden Retriever','Golden Retriever')]
    age_select = [('Adult','Adult'),('Baby','Baby'),('Senior','Senior'),('Young','Young')]
    gender_select = [('Male', 'Male'),('Female', 'Female')]
    availability_select = [('Adopted','Adopted'),('Available','Available'),('Pending','Pending'),('Not Available','Not Available')]
    ''' End Form Field Options '''
    ''' Begin Form Validation Options '''
    name = StringField('Enter Name', [validators.Length(min=3), validators.InputRequired()])
    type = SelectField(u'Type',choices = type_select, validators=[validators.InputRequired()])
    breed = StringField('Breed',[validators.Length(min=3), validators.InputRequired()])
    age = SelectField(u'Age', choices = age_select,validators=[validators.InputRequired()])
    gender = SelectField(u'Gender',choices = gender_select,validators=[validators.InputRequired()])
    status = StringField('Status',[validators.Length(min=3), validators.InputRequired()])
    description = TextAreaField('Description',[validators.Length(min=3), validators.InputRequired()])
    location = StringField('Location',[validators.Length(min=3), validators.InputRequired()])
    availability = SelectField(u'Availability',choices = availability_select,validators=[validators.InputRequired()])
    properties = StringField('Properties', [validators.InputRequired()])
    profile_image = FileField('Image')
    ''' End Form Validation Options '''