from flask import Blueprint, redirect, render_template, url_for, flash, request, abort
from flask_login import (login_user, login_required, current_user)

from mib.forms import UserForm, UserModifyForm
from mib.auth.user import User
from mib.rao.user_manager import UserManager
from mib.rao.message_manager import MessageManager
from mib.rao.lottery_manager import LotteryManager
import bcrypt
from datetime import datetime
from dateutil.parser import parse
import hashlib
import json
from json import dumps

from datetime import datetime

users = Blueprint('users', __name__)

@users.route('/create_user', methods=['GET', 'POST'])
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
        phone = form.data['phone']

        date = parse(birthdate)
        date = date.strftime('%d/%m/%Y')
        
        #This function calls the usermicroservice and the lottery microservice to initialize the database and create the user
        #UserManager.create_user calls user's microservice and lottery microservice
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

            id = response.json()['user']['id']
            rsp = LotteryManager.create_lottery_row(id) #creating the row in the lottery db
            
            user = response.json() 
            to_login = User.build_from_json(user["user"]) 
            login_user(to_login) 
            return redirect('/') 
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


@users.route('/users')
@login_required
def _users():
    #Filtering only registered users
    _users = UserManager.get_all_users()
    return render_template("users.html", users=list(_users))


@users.route('/users/start/<s>')
def _users_start(s):
    #Select the first user in the db with firstname starting by "s", used in search bar for message sending
    users = UserManager.get_all_users() #db.session.query(User).filter(User.is_active==True).filter(User.firstname.startswith(s)).limit(2).all()
    
    #Filtering the list of users
    for usr in users:
        if usr['is_active'] == True:
            if usr['firstname'].startswith(s) == True:
                return  dumps({'id':usr['id'],'firstname' : usr['firstname'], 'lastname':usr['lastname'],'email':usr['email']})
    
    return dumps({})


#LOGIC SHOULD BE DONE - TO TEST
@users.route('/myaccount', methods=['DELETE', 'GET'])
@login_required
def myaccount():
    if request.method == 'DELETE':
        UserManager.delete_user(current_user.id) # retrieve the current user
        return redirect("/logout",code=303)
    elif request.method == 'GET':
        #get my account info
        usr = UserManager.get_user_by_id(current_user.id)
        usr_birth = parse(usr.extra_data['date_of_birth'])
        usr_birth = usr_birth.strftime('%d/%m/%Y')
        usr_content_filter = usr.extra_data['filter_isactive']
        return render_template("myaccount.html", my_current_user = usr, my_birth = usr_birth, my_content_filter = usr_content_filter)


@users.route('/myaccount/modify',methods=['GET','POST'])
@login_required
def modify_data():
    #modify user data
    form = UserModifyForm()
    if request.method == 'GET':
        #render the form with current values of my account
        user = UserManager.get_user_by_id(current_user.id)
        
        usr_birth = parse(user.extra_data['date_of_birth'])
        form.date_of_birth.data = usr_birth
    
        form.email.data = user.email
        form.firstname.data = user.firstname
        form.lastname.data = user.lastname
        return render_template('modifymyaccount.html', form = form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            #get the user row
            usr = UserManager.get_user_by_id(current_user.id)
            #check current password
            old_mail = usr.email
            usr_authenticated = UserManager.authenticate_user(old_mail, form.password.data) #check the authentication with the old mail and psw
            if usr_authenticated.authenticated == True:    #to change data values current user need to insert the password
                #check for new password inserted in the apposit field
                new_psw = form.password.data
                if (form.newpassword.data ) and (form.newpassword.data == form.repeatnewpassword.data):
                    new_psw = form.newpassword.data
           
                #check that users changed this account email with another already used by another
                email_check = UserManager.get_user_by_email(form.email.data)
                if email_check is None or email_check.id == current_user.id:
                    new_email = form.email.data
                else:
                    return render_template('modifymyaccount.html', form = form, error = "This email is already used! Try with another one.")
                    
                date_to_change = form.date_of_birth.data.strftime('%d/%m/%Y')
                
                resp = UserManager.update_user(current_user.id, form.email.data, form.password.data , form.firstname.data, form.lastname.data, str(date_to_change), form.newpassword.data)
                response = resp.json()
                
                if response['status'] != 'success':
                    return render_template('modifymyaccount.html', form = form, error = 'Some error occurred')
                else:
                    return render_template('modifymyaccount.html', form = form, success = 'Your data has been updated!')
            else:
                return render_template('modifymyaccount.html', form = form, error = "Wrong password")


@users.route('/myaccount/set_content', methods=['PUT'])
@login_required
def set_content():
    #set content filter when button clicked into the GUI
    get_data = json.loads(request.data)
    if(get_data['filter']==True):
        #Setting to True the field in DB
        ret = UserManager.set_content_filter(current_user.id,True)
    else:
        #Setting to False the field in DB
        ret = UserManager.set_content_filter(current_user.id,False) 
    return '{"message":"OK"}'


@users.route('/blacklist',methods=['GET','DELETE'])
@login_required
def get_blacklist():
    if request.method == 'GET':

        #get blacklist of current user
        data = UserManager.get_blacklist(current_user.id)
        return render_template('black_list.html',action="This is your blacklist",black_list=data)

    elif request.method == 'DELETE':
        #Clear the whole blacklist
        data = UserManager.delete_blacklist(current_user.id)
        return render_template('black_list.html',action="Your blacklist is now empty",black_list=data)
    
        
@users.route('/blacklist/<target>', methods=['POST', 'DELETE'])
@login_required
def add_to_black_list(target):
   #route that add target to the blacklist of user.
       #add target into the user's blacklist
       if request.method == 'POST':
            ta = int(target)
            UserManager.insert_blacklist(current_user.id, ta)
            return render_template('black_list.html',action="User "+target+" added to the black list.",black_list = [])
       elif request.method == 'DELETE':
            ta = int(target)
            l = UserManager.delete_blacklist_target(current_user.id, ta)
           
            return render_template('black_list.html',action="User "+target+" removed from your black list",black_list = [])


#report a user: a user can report an other user based on a message that the target user send to him.

@users.route('/report_user/<msg_target_id>', methods = ['POST'])
@login_required
def report_user(msg_target_id):
    threshold_ban = 3 #the threshold of reports to ban the user
    days_of_ban = 3 #the number of days of ban

        
    if request.method == 'POST': 
        #0. check the existence of usr and usr_to_report
        user_status_ = {'message':''}
        report_message_status = MessageManager.report_message(msg_target_id,current_user.id) #tries to report a user
        if report_message_status['message'] == 'This message has been correctly reported':
            report_user_status = UserManager.report_user(report_message_status['id'])
            user_status_['message'] = report_user_status['message']
        list_msg = MessageManager.get_msglist(msg_target_id,current_user.id)
        render_template('get_msg.html',messages = list_msg, message_status = report_message_status['message'],user_status = user_status_)
        
    
    
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
