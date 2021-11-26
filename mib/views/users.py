from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required, current_user)

from mib.forms import UserForm
from mib.rao.user_manager import UserManager
from mib.auth.user import User

users = Blueprint('users', __name__)


@users.route('/create_user/', methods=['GET', 'POST'])
def create_user():
    """This method allows the creation of a new user into the database

    Returns:
        Redirects the user into his profile page, once he's logged in
    """
    form = UserForm()

    if form.is_submitted():
        email = form.data['email']
        password = form.data['password']
        firstname = form.data['firstname']
        lastname = form.data['lastname']
        birthdate = form.data['birthdate']
        date = birthdate.strftime('%Y-%m-%d')
        phone = form.data['phone']
        response = UserManager.create_user(
            email,
            password,
            firstname,
            lastname,
            date,
            phone
        )

        if response.status_code == 201:
            # in this case the request is ok!
            user = response.json()
            to_login = User.build_from_json(user["user"])
            login_user(to_login)
            return redirect(url_for('home.index', id=to_login.id))
        elif response.status_code == 200:
            # user already exists
            flash('User already exists!')
            return render_template('create_user.html', form=form)
        else:
            flash('Unexpected response from users microservice!')
            return render_template('create_user.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for errorMessage in errorMessages:
                flash('The field %s is incorrect: %s' % (fieldName, errorMessage))

    return render_template('create_user.html', form=form)


@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """Deletes the data of the user from the database.

    Args:
        id_ (int): takes the unique id as a parameter

    Returns:
        Redirects the view to the home page
    """

    response = UserManager.delete_user(id)
    if response.status_code != 202:
        flash("Error while deleting the user")
        return redirect(url_for('auth.profile', id=id))
        
    return redirect(url_for('home.index'))

@users.route('/blacklist',methods=['GET','DELETE'])
#@login_required
def get_blacklist():
    if request.method == 'GET':
        #get blacklist of current user
        response = UserManager.get_user_by_id(current_user.id)
        if response.status_code != 200:
            flash("Error while getting the blacklist")
            return render_template('black_list.html',action="Error while retrieving blacklist",black_list=[])
        data = response.json()
        return render_template('black_list.html',action="This is your blacklist",black_list=data['extra'])
    elif request.method == 'DELETE':
        #Clear the whole blacklist
        pass
        #black_list = db.session.query(blacklist.c.user_id).filter(blacklist.c.user_id==current_user.id).first()
        #if black_list is not None:
        #    #clear only if the blacklist is not empty
        #    st = blacklist.delete().where(blacklist.c.user_id == current_user.id)
        #    db.session.execute(st)   
        #    db.session.commit()
        #    black_list = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id)
        #
        #    return render_template('black_list.html',action="Your blacklist is now empty",black_list=black_list,new_msg=_new_msg)
        #else:
        #    return render_template('black_list.html',action="Your blacklist is already empty",black_list=[],new_msg=_new_msg)
