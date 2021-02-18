###############################################################################
#
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson                                                        
# Email: bauergr@oregonstate.edu                                                                              
# Course: CS467_400_W2021
# Description: Form validation package used in 'news_add_edit' template.
#   Creates form class with form fields and pertinent validation rules
#
# Referenced: https://wtforms.readthedocs.io/en/2.3.x/crash_course/
#
###############################################################################

from wtforms import *

class NewsForm(Form):
    ''' Form Field Options '''
    ''' End Form Field Options '''
    ''' Begin Form Validation Options '''
    name = StringField('Enter Name', [validators.Length(min=3), validators.InputRequired()])
    author = StringField('Author',[validators.Length(min=3), validators.InputRequired()])
    content = TextAreaField('Content',[validators.Length(min=3), validators.InputRequired()])
    profile_image = FileField('Image')
    ''' End Form Validation Options '''
