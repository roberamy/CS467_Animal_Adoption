from wtforms import *

class AdminProfileForm(Form):
    type_select = [('Cat', 'Cat'),('Dog', 'Dog'),('Other', 'Other')]
    breed_select = [('American Shorthair','American Shorthair'),('German Shepherd','German Shepherd'),
    ('Golden Retriever','Golden Retriever')]
    age_select = [('Adult','Adult'),('Baby','Baby'),('Senior','Senior'),('Young','Young')]
    gender_select = [('Male', 'Male'),('Female', 'Female')]
    availability_select = [('Adopted','Adopted'),('Available','Available'),('Pending','Pending'),('Not Available','Not Available')]
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