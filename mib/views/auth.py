from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from flask.globals import request
from mib.rao.user_manager import UserManager

from mib.forms import LoginForm
from datetime import datetime, date

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Allows the user to log into the system

    Args:
        re (bool, optional): boolean value that describes whenever
        the user's session is new or needs to be reloaded. Defaults to False.

    Returns:
        Redirects the view to the personal page of the user
    """
    form = LoginForm()
    error= ""
    code = 200
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password'] #getting data from form
        user = UserManager.authenticate_user(email, password)
        
        if user is not None: #check that user exists
            if user.ban_expired_date is None: #check ban on user
                login_user(user)
                return redirect(url_for('index.html'))
            elif user.ban_expired_date < datetime.today(): #the ban date has expired, need to set the ban_expired_date to None
                """"
                TODO 
                usr = db.session.query(User).filter(User.email == email).first()
                usr.ban_expired_date = None
                db.session.commit()
                """
                
                login_user(user)
                return redirect(url_for('index.html'))
            else: #The account is under ban, so the user can't login
                error="Account under ban"
                code = 401
                return render_template('login.html', form=form, error = error), code   #added error to detect bad login
        error="Login failed"
        code = 401
    else:
        error = "Invalid login form"
        code = 400
    return render_template('login.html', form=form, error = error), code   #added error to detect bad login

#route to logout a user
@auth.route("/logout")
@login_required
def logout():
    """This method allows the users to log out of the system

    Returns:
        Redirects the view to the home page
    """
    logout_user()
    return redirect('/')
