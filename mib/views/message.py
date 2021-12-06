import base64
from flask import Blueprint, render_template, request,abort
from werkzeug.utils import redirect 
from datetime import date, datetime, timedelta
from flask_login import (login_user, login_required, current_user)
from mib.rao.message_manager import MessageManager
from mib.rao.user_manager import UserManager

import json

import json

message = Blueprint('message', __name__)

##route to withdrow a message (using points earned from lottery)
#@message.route('/message_withdrow/<msg_id>',methods = ['DELETE'])
#def withdrow(msg_id):
#    #route of regrets. Withdrow a message only if you selected a real message and you have enough points to do so
#    if current_user is not None and hasattr(current_user, 'id'):
#        msg_exist = db.session.query(Messages.id, Messages.sender,Messages.is_draft , User.lottery_points).filter(Messages.id == msg_id).filter(Messages.sender == current_user.id).filter(User.id == Messages.sender).first()
#        _send = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery).filter(Messages.sender==current_user.id,Messages.is_draft==False).all()
#        _draft = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery).filter(Messages.sender==current_user.id,Messages.is_draft==True).all()
#        
#        if msg_exist is not None and msg_exist.is_draft == False:
#            
#            if msg_exist.lottery_points >= 10:
#                #this ensure that current_user is the owner of the message and that the message exist
#                #10 points needed to withdrow a message
#                msg_row = db.session.query(Messages).filter(Messages.id == msg_id).first()
#                usr_row = db.session.query(User).filter(User.id == msg_exist.sender).first()
#                usr_row.lottery_points -= 10
#                db.session.delete(msg_row)          #delete the whole message from the db 
#                db.session.commit()
#                return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Your message has been deleted")
#
#            else:
#                #no enough points to withdrow
#                return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "You need 10 points to withdrow a message. To gain points, try to play lottery!")
#        elif msg_exist.is_draft == True:
#            #just delete the draft
#            delete_ = db.session.query(Messages).filter(Messages.id == msg_id).first()
#            db.session.delete(delete_)
#            db.session.commit()
#            return render_template('get_msg_send_draft.html', draft=_draft, send=_send)
#        else:
#            return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Something went wrong...")
#
#    else:
#        return redirect('/')

#route used in sending new message
@message.route('/message/new',methods = ['GET','POST'])
@login_required
def message_new():
    if request.method == 'GET': #return the html page with form to send msg
        return render_template("newmessage.html")
    elif request.method =='POST': #get the values from msg form
        message = MessageManager.create_message(request,current_user.id,isDraft=False)
        return message

# Route to success send messages
@message.route('/message/send')
@login_required
def message_send():
    return render_template("message_send_response.html")

#route to have a draft msg
@message.route('/message/draft',methods = ['GET','POST'])
@login_required
def message_draft():
    """This method allows the creation of a new draft message
    """ 
    if request.method == 'GET':
        return render_template("message_draft_response.html")
    else:
        message = MessageManager.create_message(request,current_user.id,isDraft=True)
        return message


#select message to be read and access the reading panel or delete it from the list
#@message.route('/message/<_id>', methods=['GET', 'DELETE'])
#def select_message(_id):
#    if request.method == 'GET':
#        if current_user is not None and hasattr(current_user, 'id'):
#
#            _message = db.session.query(Messages.title, Messages.content,Messages.id,Messages.font).filter(Messages.id==_id).first()
#            _picture = db.session.query(Images).filter(Images.message==_id).all()
#            user = db.session.query(msglist.c.user_id).filter(msglist.c.msg_id==_id,msglist.c.user_id==current_user.id).first()
#
#            #check that the actual recipient of the id message is the current user to guarantee Confidentiality 
#            if current_user.id == user[0]:
#                #Convert Binary Large Object in Base64
#                l = []
#                
#                for row in _picture:
#                   
#                    image = base64.b64encode(row.image).decode('ascii')
#                    l.append(image)
#                
#                #If it is the first time that the message is read, then notify the sender and update the state
#                read = db.session.query(msglist.c.read).filter(msglist.c.user_id==current_user.id, msglist.c.msg_id==_id).first()
#
#                if(read[0]==False):
#                    #notify with celery update read status
#                   
#                   #Try to notify the sender
#                   #QoS  TCP/IP one if the redis-queue, is down the notification is sent iff the user reopen the message after  and the service it's ok
#                    try:
#                        sender_id = db.session.query(Messages.sender).filter(Messages.id==_id).first()
#                        notify.delay(sender_id[0], current_user.id, _id)
#                        stmt = (
#                        update(msglist).where(msglist.c.msg_id==_id, msglist.c.user_id==current_user.id).values(read=True))
#
#                        db.session.execute(stmt)
#                        db.session.commit()
#                    except Exception as e:
#                        abort(404, description="Celery not available")
#                       
#                    
#
#                return render_template('message_view.html',message = _message, pictures=json.dumps(l),new_msg=2) 
#            else:
#                abort(403) #the server is refusing action
#        else:
#            return redirect("/")
#
#    elif request.method == 'DELETE':
#        if current_user is not None and hasattr(current_user, 'id'):
#            
#            #delete the current message
#            stmt = (
#                delete(msglist).
#                where(msglist.c.msg_id==_id, msglist.c.user_id == current_user.id)
#                )
#            db.session.execute(stmt)
#            db.session.commit()
#
#            return '{"delete":"OK"}'
#        else:
#            return redirect("/")
#    
#
## Reply to one message
#@message.route('/message/reply/<_id>', methods=['GET'])
#def reply(_id):
#    _reply = db.session.query(Messages.sender,Messages.title,User.firstname,User.lastname).filter(Messages.id==_id).filter(User.id==Messages.sender).first()
#    return render_template('replymessage.html',new_msg=2,reply=_reply)
#
#
@message.route('/message/view_send/<int:id>',methods=['GET'])
@login_required
def message_view_send(id):
    _message = MessageManager.get_message_by_id(id)
    receiver_list = []
    for elem in _message.receivers:
        receiver_list.append(UserManager.get_user_by_id(elem))
    _pictures = MessageManager.get_images(id)
    if _message.sender == current_user.id:
        l = []
        image_ids = []
        if len(_pictures) > 0:
            for i in range(0,len(_pictures)):
                image = _pictures[str(i)]['image']
                l.append(image)
                image_ids.append( _pictures[str(i)]['id'])
        return render_template('message_view_send.html',message = _message,receivers=receiver_list, pictures=json.dumps(l)) 
    else:
        return redirect('/')


@message.route('/edit/<int:message_id>',methods=['GET'])
@login_required
def message_view_draft(message_id):
    _message = MessageManager.get_message_by_id(message_id)
    receiver_list = []
    for id in _message.receivers:
        receiver_list.append(UserManager.get_user_by_id(id))
    _pictures = MessageManager.get_images(message_id)
    if _message.sender == current_user.id:
        l = []
        image_ids = []
        if len(_pictures) > 0:
            for i in range(0,len(_pictures)):
                image = _pictures[str(i)]['image']
                l.append(image)
                image_ids.append( _pictures[str(i)]['id'])
        return render_template('message_view_edit_draft.html',message = _message, pictures=json.dumps(l),image_ids=image_ids,receivers=receiver_list) 
    else:
        return redirect('/')
                                           
@message.route('/messages/sent',methods=['GET'])
@login_required
def messages_send():
        
    response = MessageManager.get_all_messages(current_user.id)
    
    return render_template('get_msg_send_draft.html',draft=list(response.get("_draft")),send=list(response.get("_sent")))


# get the list of messages received until now
@message.route('/messages', methods=['GET'])
@login_required
def messages():
    _user = UserManager.get_user_by_id(current_user.id)
    print("USER: \n")
    print(_user)
    filter = _user.__getattr__('filter_isactive')
    print("FILTER: \n")
    print(filter)
    _messages = ""
    #if filter == False:
    #    blacklistSQ = db.session.query(blacklist.c.black_id).filter(blacklist.c.user_id == current_user.id).subquery()
    #    
    #    User1 = aliased(User)   #Receiver table   
    #    User2 = aliased(User)   #Sender table
    #    
    #    _messages = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery,Messages.sender,User2.firstname,msglist.c.user_id,User1.filter_isactive,Messages.bad_content)\
    #    .filter(msglist.c.user_id==User1.id,msglist.c.msg_id==Messages.id) \
    #    .filter(User1.id==current_user.id) \
    #    .filter(User2.id == Messages.sender)\
    #    .filter(Messages.date_of_delivery <= datetime.now(),Messages.is_draft==False) \
    #    .filter(Messages.sender.notin_(blacklistSQ))

    #else:
    #    
    #    blacklistSQ = db.session.query(blacklist.c.black_id).filter(blacklist.c.user_id == current_user.id).subquery()
    #    
    #    User1 = aliased(User)   #Receiver table   
    #    User2 = aliased(User)   #Sender table
    #    
    #    _messages = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery,Messages.sender,User2.firstname,msglist.c.user_id,User1.filter_isactive,Messages.bad_content)\
    #    .filter(msglist.c.user_id==User1.id,msglist.c.msg_id==Messages.id) \
    #    .filter(User1.id==current_user.id) \
    #    .filter(User2.id == Messages.sender)\
    #    .filter(Messages.date_of_delivery <= datetime.now(),Messages.is_draft==False) \
    #    .filter(Messages.sender.notin_(blacklistSQ)) \
    #    .filter(Messages.bad_content==False)


    return render_template("get_msg.html", messages = _messages)
#
##forward message to other user that are not already in the messagelist
#@message.route('/message/forward',methods=['POST'])
#def message_forward():
#     #check user exist and that is logged in
#    if current_user is not None and hasattr(current_user, 'id'):
#        get_data = json.loads(request.form['payload'])
#        #Add the users in msglist
#        l = get_data["destinators"]
#        for el in l:
#            #Insert Users in msglist
#            try:
#                stm = (
#                    insert(msglist).
#                    values(msg_id=get_data["messageid"],user_id=el)
#                )
#                db.session.execute(stm)
#                db.session.commit()
#            except IntegrityError as e:
#                print("The user is already insert")
#    else:
#         return redirect("/")
#
#    return '{"status":"OK"}'
#