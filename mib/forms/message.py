import wtforms as f
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import DataRequired

class NewMessageForm(FlaskForm):
    destinator = f.StringField('Destinator', validators=[DataRequired()])
    title = f.StringField('Title', validators=[DataRequired()])    
    content = f.TextAreaField('Content')
    display = ['destinator', 'title','content']
