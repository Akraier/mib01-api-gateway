import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.core import DateTimeField, StringField
from wtforms.fields.html5 import DateField, EmailField, TelField
from wtforms.validators import DataRequired, Email


class UserForm(FlaskForm):
    """Form created to allow the customers sign up to the application.
    This form requires all the personal information, in order to create the account.
    """

    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    firstname = f.StringField(
        'Firstname',
        validators=[DataRequired()]
    )

    lastname = f.StringField(
        'Lastname',
        validators=[DataRequired()]
    )

    password = f.PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    birthdate = StringField(
        'Birthday',
        validators=[DataRequired()]
    )

    phone = TelField(
        'Phone',
        validators=[DataRequired()]
    )

    display = ['email', 'firstname', 'lastname', 'password',
               'birthdate', 'phone']
