import base64
from flask import Blueprint, blueprints, render_template, request,abort
from werkzeug.utils import redirect 
from datetime import date, datetime, timedelta
from flask_login import (login_user, login_required, current_user)
from mib.rao.message_manager import MessageManager
from mib.rao.user_manager import UserManager
from mib.rao.lottery_manager import LotteryManager

import json

import json

message = Blueprint('message', __name__)

#route to withdrow a message (using points earned from lottery)
@message.route('/message_withdrow/<msg_id>',methods = ['DELETE'])
@login_required
def withdrow(msg_id):
    #route of regrets. Withdrow a message only if you selected a real message and you have enough points to do so
    _message = MessageManager.get_message_by_id(int(msg_id))
    all_messages = MessageManager.get_all_messages(current_user.id)
    if _message == None:
        return render_template('get_msg_send_draft.html',draft=list(all_messages.get("_draft")),send=list(all_messages.get("_sent")))
    
    _sender_user = UserManager.get_user_by_id(_message.sender)
    _send = list(all_messages.get("_sent"))
    _draft = list(all_messages.get("_draft"))

    if _message.extra_data['is_draft'] == False:
        
        _lottery = LotteryManager.retrieve_by_id(current_user.id)
        if _lottery['points'] >= 10:
            #10 points needed to withdrow a message
            response = LotteryManager.update_lottery_points(current_user.id, -10)
            if response['message'] == "error":
                return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Something went wrong, retry later")
            MessageManager.delete_message(msg_id)
            return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Your message has been deleted")
        else:
            #no enough points to withdrow
            return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "You need 10 points to withdrow a message. To gain points, try to play lottery!")
    else:
        #just delete the draft
        MessageManager.delete_message(msg_id)
        return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Your message has been deleted")

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
@message.route('/message/<_id>', methods=['GET', 'DELETE'])
@login_required
def select_message(_id):
    if request.method == 'GET':
        _message = MessageManager.get_message_by_id(int(_id))
        _pictures = MessageManager.get_images(int(_id))
        user = MessageManager.get_msglist(_id, current_user.id)
        sender = UserManager.get_user_by_id(_message.sender)
        #Getting images
        l = []
        image_ids = []
        if len(_pictures) > 0:
            for i in range(0,len(_pictures)):
                image = _pictures[str(i)]['image']
                l.append(image)
                image_ids.append( _pictures[str(i)]['id'])
        
        #If it is the first time that the message is read, then notify the sender and update the state
        if(user['read']==False):
            #notify with celery update read status
            
            #Try to notify the sender
            #QoS  TCP/IP one if the redis-queue, is down the notification is sent iff the user reopen the message after  and the service it's ok
            try:
                sender_id = _message.sender
                response = MessageManager.celery_notify(sender_id)
            except Exception as e:
                abort(404, description="Celery not available")
                
        return render_template('message_view.html',message = _message, pictures=json.dumps(l), sender=sender) 
    elif request.method == 'DELETE':
            #delete the current message
            MessageManager.delete_receiver(_id, current_user.id)
            return '{"delete":"OK"}'
    

# Reply to one message
@message.route('/message/reply/<_id>', methods=['GET'])
def reply(_id):
    _message = MessageManager.get_message_by_id(int(_id))
    _user = UserManager.get_user_by_id(_message.sender)

    return render_template('replymessage.html',message=_message, user=_user)


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
    filter = _user.extra_data['filter_isactive']
    _messages = ""
    _blacklist = UserManager.get_blacklist(current_user.id)
    #checking the content
    if filter == False:
        # show message with bad content
        _messages = MessageManager.get_received_msg(current_user.id, datetime.now().strftime('%Y-%m-%d %H:%M'),filter=False)
    else:
        _messages = MessageManager.get_received_msg(current_user.id, datetime.now().strftime('%Y-%m-%d %H:%M'),filter=True)
    _filtered_messages = []
    blacklist_ids = []
    for elem in _blacklist:
        blacklist_ids.append(elem['id'])
    for elem in _messages:
        try:
            # if not except, then the sender is in the blacklist
            blacklist_ids.index(elem['sender'])
        except ValueError:
            # the sender is not in the blacklist, message needs to be added in the view
            _filtered_messages.append(elem)
    return render_template("get_msg.html", messages = _filtered_messages)
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