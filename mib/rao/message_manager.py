import re

from flask.json import jsonify
from mib import app
from flask_login import (logout_user)
from flask import abort
from mib.auth.message import Message
import requests
import json
import base64

class MessageManager:
    MESSAGES_ENDPOINT = app.config['MESSAGES_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_message_by_id(cls, message_id: int) -> Message:
        """
        This method contacts the messages microservice
        and retrieves the message object by message id.
        :param message_id: the message id
        :return: Message obj with id=message_id
        """
        try:
            response = requests.get("%s/message/%d" % (cls.MESSAGES_ENDPOINT, message_id),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            print(json_payload)
            if response.status_code == 200:
                message = Message.build_from_json(json_payload)
            elif response.status_code == 404:
                return None
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return message

    @classmethod
    def get_all_messages(cls, user_id):
        try:
            response = requests.get("%s/messages/all/%d" % (cls.MESSAGES_ENDPOINT, user_id),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def get_images(cls, message_id):
        """
        This method contacts the message microservice
        and retrieves the images associated to the message
        """
        try:
            response = requests.get("%s/message/%d/images" % (cls.MESSAGES_ENDPOINT, message_id),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def create_message(cls, request, sender_id, isDraft):
        """
        This method contacts the message microservice
        and let creation of a new draft message.
        :param request: the flask request
        :param sender_id: id of the sender
        :return: message result
        """

        try:
            try: 
                # Get images previously uploaded that needs to be deleted
                image_id_to_delete = list(map(int, json.loads(request.form['delete_image_ids'])))
            except KeyError:
                image_id_to_delete = []
            try:
                # Get users previously uploaded that needs to be deleted
                user_id_to_delete = list(map(int, json.loads(request.form['delete_user_ids'])))
            except KeyError:
                user_id_to_delete = []
            try: 
                msg_id = int(request.form["message_id"])
            except KeyError:
                msg_id = 0

            raw_images = []
            mimetypes = []
            # converting images to base64
            for image in request.files:
                binary_file_data = request.files[image].read()
                base64_encoded_data = base64.b64encode(binary_file_data)
                base64_message = base64_encoded_data.decode('utf-8')
                raw_images.append(base64_message)
                mimetypes.append(request.files[image].mimetype)

            _data={
                'payload': json.loads(request.form['payload']),
                'delete_image_ids': image_id_to_delete,
                'delete_user_ids': user_id_to_delete,
                'message_id': msg_id,
                'sender': sender_id,
                'raw_images': raw_images,
                'mimetypes': mimetypes
            }
            
            if isDraft == True:
                response = requests.post("%s/message/draft" % (cls.MESSAGES_ENDPOINT),
                                json=_data,
                                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                            )
            else:
                response = requests.post("%s/message/send" % (cls.MESSAGES_ENDPOINT),
                                json=_data,
                                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                            )
            json_payload = response.json()
            print(json_payload)
            if response.status_code == 200 or response.status_code == 201:
                return '{"message":"OK"}'
            elif response.status_code == 400:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    
    @classmethod
    def delete_message(cls, message_id):
        """
            This method contacts the message microservice
            to delete a message.
            :param message_id: id of the message
            :return: delete result
        """
        try:
            response = requests.delete("%s/message/%d" % (cls.MESSAGES_ENDPOINT, int(message_id)),
                            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                        )
            json_payload = response.json()
            if response.status_code == 202:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    
    @classmethod
    def get_received_msg(cls, receiver_id, date, filter):
        """
            This method contacts the message microservice
            and retrieve the received messages.
            :param receiver_id: id of receiver
            :param date: date for retrive message
            :param filter: tells if the filter is active or not
            :return: list of messages
        """
        try:
            _data={
                'receiver': str(receiver_id),
                'date': str(date),
                'filter': filter
            }

            response = requests.post("%s/messages/received" % (cls.MESSAGES_ENDPOINT),
                            json=_data,
                            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                        )
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            elif response.status_code == 400:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    
    @classmethod
    def get_msglist(cls, message_id, user_id):
        """
            This method contacts the message microservice
            and retrieve the msglist associated to message_id.
            :param message_id: id of the message
            :param user_id: id of the receiver
            :return: msglist
        """
        try:

            response = requests.get("%s/message/list/%d/%d" % (cls.MESSAGES_ENDPOINT, int(message_id), int(user_id)),
                            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                        )
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    
    @classmethod
    def delete_receiver(cls, message_id, user_id):
        """
            This method contacts the message microservice
            to delete a message.
            :param message_id: id of the message
            :param user_id: id of the receiver to delete
            :return: delete result
        """
        try:
            response = requests.delete("%s/message/list/%d/%d" % (cls.MESSAGES_ENDPOINT, int(message_id), int(user_id)),
                            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                        )
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    @classmethod 
    def report_message(cls,msg_id,current_id):
        """
            This method contact the message ms in order to report a user
        """
        try:
            response = requests.post("%s/report/%d/%d" % (cls.MESSAGES_ENDPOINT,int(msg_id),int(current_id)),timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                return json_payload
            if response.status_code == 201:
                return json_payload
            if response.status_code == 404:
                return json_payload  
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
    @classmethod
    def celery_notify(cls, sender_id):
        """# TODO notify.delay(sender_id[0], current_user.id, _id)
                stmt = (
                update(msglist).where(msglist.c.msg_id==_id, msglist.c.user_id==current_user.id).values(read=True))

                db.session.execute(stmt)
                db.session.commit()"""
        return jsonify({'message': 'OK'})