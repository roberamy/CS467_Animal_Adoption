###############################################################################################################
#                                                                                                                      
# Author: Gregory A. Bauer, Jasper Wong, Amy Robertson
# Email: bauergr@oregonstate.edu
# Course: CS467_400_W2021
#
# Description: Form validation package used in 'add_news' template. Creates form class with form
#              fields and pertinent validation rules
#
# ref: https://wtforms.readthedocs.io/en/2.3.x/crash_course/
#
###############################################################################################################

from wtforms import *
        
class NewsForm(Form):
    ''' Form Field Options '''
    ''' End Form Field Options '''
    
    ''' Begin Form Validation Options '''
    author = StringField('Author', [validators.Length(min=3), validators.InputRequired()])
    title = StringField('Title', [validators.Length(min=3), validators.InputRequired()])
    content = StringField('Author', [validators.Length(min=3), validators.InputRequired()])
    image_name = FileField('news_image')
    ''' End Form Validation Options '''
