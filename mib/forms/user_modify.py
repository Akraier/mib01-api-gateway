import wtforms as f
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import DataRequired

class UserModifyForm(FlaskForm):
    """ A form for modify users """

    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    newpassword = f.PasswordField('new password')
    repeatnewpassword = f.PasswordField('repeat new password')
    date_of_birth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password','newpassword','repeatnewpassword', 'date_of_birth']