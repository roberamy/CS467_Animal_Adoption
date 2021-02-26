###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description:
#   Form validation package used in 'add_profile' template.
#   Creates form class with form fields and pertinent validation rules
#
# References:
# https://wtforms.readthedocs.io/en/2.3.x/crash_course/
# https://wtforms.readthedocs.io/en/2.3.x/validators/
################################################################################

from wtforms import Form, validators, ValidationError, TextAreaField
from wtforms import StringField, SelectField, FileField
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


# Helper function to validate location input
def validateLocation(field):
    states = [
        'AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
        'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
        'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD',
        'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']
    state = field.data[-2:]
    checkState = False
    length = len(field.data)
    # Check that 4th character from end is a comma
    if field.data[length-4] != ',':
        raise ValidationError('Format Error (ex: Portland, OR)')
    # Check that 4th character from end is a space
    if field.data[length-3] != ' ':
        raise ValidationError('Format Error (ex: Portland, OR)')
    # Check that last two characters are capital
    if (field.data[length-1]).isupper() is False:
        raise ValidationError('Format Error (ex: Portland, OR)')
    if (field.data[length-2]).isupper() is False:
        raise ValidationError('Format Error (ex: Portland, OR)')
    # Check that state is valid
    for s in states:
        if state == s:
            checkState = True
    if checkState is False:
        raise ValidationError('Invalid State (ex: Portland, OR)')


class AdminProfileForm(Form):
    ''' Form Field Options '''
    type_select = [('Cat', 'Cat'), ('Dog', 'Dog'), ('Other', 'Other')]
    breed_select = petBreeds()
    age_select = [('Adult', 'Adult'), ('Baby', 'Baby'),
                  ('Senior', 'Senior'), ('Young', 'Young')]
    gender_select = [('Male', 'Male'), ('Female', 'Female')]
    availability_select = [('Adopted', 'Adopted'),
                           ('Available', 'Available'),
                           ('Pending', 'Pending'),
                           ('Not Available', 'Not Available')]
    ''' End Form Field Options '''
    ''' Begin Form Validation Options '''
    name = StringField('Enter Name', validators=[validators.Length(min=3), validators.InputRequired()])
    type = SelectField(u'Type', choices=type_select, validators=[validators.InputRequired()])
    breed = SelectField(u'Breed', choices=breed_select, validators=[validators.InputRequired()])
    age = SelectField(u'Age', choices=age_select, validators=[validators.InputRequired()])
    gender = SelectField(u'Gender', choices=gender_select, validators=[validators.InputRequired()])
    status = StringField('Status', validators=[validators.Length(min=3), validators.InputRequired()])
    description = TextAreaField('Description', [validators.Length(min=3), validators.InputRequired()])
    location = StringField('Location', validators=[validators.InputRequired(), validateLocation(Form['location'])])
    availability = SelectField(u'Availability', choices=availability_select, validators=[validators.InputRequired()])
    properties = StringField('Properties', validators=[validators.InputRequired()])
    adoption_date = StringField('adoption_date')
    adopted_by = StringField('adopted_by')
    picked_up = StringField('picked_up')
    profile_image = FileField('Image')
    ''' End Form Validation Options '''
