from flask import Blueprint, redirect, render_template, url_for, flash, request, abort
from flask_login import (login_user, login_required, current_user)

from mib.forms import UserForm, UserModifyForm
from mib.auth.user import User
from mib.rao.user_manager import UserManager

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
        form.date_of_birth.data = usr_birth#.strftime('%d/%m/%Y')
    
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
            print("----")
            print(l)
            return render_template('black_list.html',action="User "+target+" removed from your black list",black_list = [])


# '''
#     form = UserForm()
#     if request.method == 'POST':
#         if form.validate_on_submit() == True:
#             new_user = User()
#             form.populate_obj(new_user)
#             if db.session.query(User).filter(User.email == form.email.data).first() is not None:
#                 #email already used so we have to ask to fill again the fields
#                 return render_template('create_user.html',form=form,error="Email already used!")
#             """
#             Password should be hashed with some salt. For example if you choose a hash function x, 
#             where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
#             s is a secret key.
#             """           
#             #Check the correct fromat for date of birth
#             date_string = form.date_of_birth.data
#             format = '%d/%m/%Y'
#             try:
#                 dt_.strptime(date_string, format)
#             except ValueError: #the format of date inserted is not correct
#                 return render_template('create_user.html',form=form,error="Please enter a valid date of birth in the format dd/mm/yyyy!")
#             #Check the validity of date of birth (no dates less than 1900, no dates higher than last year
#             datetime_object = dt_.strptime(form.date_of_birth.data, '%d/%m/%Y')
#             my_1_year_ago = dt_.now() - timedelta(days=365)
#             if datetime_object > my_1_year_ago or datetime_object < dt_(1900,1,1):
#                 return render_template('create_user.html',form=form,error="Please enter a valid date of birth!")            
#             # Setting the user fields and add user to DB
#             new_user.set_password(form.password.data)
#             new_user.set_dateOfBirth(datetime_object) #setting the date correctly
#             db.session.add(new_user)
#             db.session.commit()
#             return redirect('/')
#     elif request.method == 'GET':
#         return render_template('create_user.html', form=form)
# '''



#report a user: a user can report an other user based on a message that the target user send to him.
#@users.route('/report_user/<msg_target_id>', methods = ['POST'])
#def report_user(msg_target_id):
#    threshold_ban = 3 #the threshold of reports to ban the user
#    days_of_ban = 3 #the number of days of ban
#
#    if current_user is not None and hasattr(current_user, 'id'):
#        
#        if request.method == 'POST': #GET IS ONLY FOR TESTING, THE METHOD SHOULD ALLOWS ONLY POST
#            #0. check the existence of usr and usr_to_report
#            existTarget = db.session.query(Messages).filter(Messages.id==msg_target_id).first() #check i fthe msg exist
#
#            if existTarget is not None: 
#                #1. Create the report against the user of msg_target_id:
#                    my_row = db.session.query(Messages.number_bad,msglist.c.hasReported,Messages.sender).filter(and_(Messages.id == msg_target_id, msglist.c.user_id == current_user.id, Messages.id == msglist.c.msg_id)).first()  
#
#                    if my_row.hasReported == False: #check that user has not already reported the msg
#                        if my_row.number_bad > 0: #check if the message has really bad words
#                            #In this case the report has to be effective -->> the report count on user "sender"        
#                            my_row2 = db.session.query(User.n_report, User.ban_expired_date).filter(User.id == my_row[2]).first()
#                            if my_row2[1] is None: #check if user is already banned (my_row2[1] is the field ban_expired_date)
#                                target_user = db.session.query(User).filter(User.id == my_row.sender).one()
#                                if (my_row2[0] + 1) > threshold_ban: #The user has to be ban from app (my_row2[0] is the field n_report)
#                                    today = date.today()
#                                    ban_date = today + datetime.timedelta(days=3)
#                                    target_user.ban_expired_date = ban_date
#                                    target_user.n_report = 0
#                                    target_user.n_report = 0 #The user is banned, so we reset the report count
#                                    db.session.commit()
#                                    return render_template('report_user.html', action = "The user reported has been banned")
#                                else:
#                                    #increment the report count for user, and setting the hasReported field to True
#                                    target_user.n_report += 1
#                                    stm = msglist.update().where(msglist.c.msg_id == msg_target_id).values(hasReported = True)
#                                    db.session.execute(stm)
#                                    db.session.commit()
#                                    return render_template('report_user.html', action = "The user has its reported counter incremented")
#                                    
#                            else:
#                                #already banned
#                                return render_template('report_user.html', action = "The user is already banned", code = 304)
#
#                        else:
#                            #sender is not guilty
#                            return render_template('report_user.html', action = "This user does not violate our policies, so we cannot handle your report.", code = 304)
#
#                    else:
#                        #the actual user has already reported this message (max one report for message for user)
#                        return render_template('report_user.html', action = "You have already reported this message!", code = 304)
#            else:
#                return render_template('report_user.html', action = "Invalid message to report!", code = 404)
#    else:
#        return redirect("/")

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
