import re
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
    def save_draft(cls, request, sender_id):
        """
        This method contacts the message microservice
        and let creation of a new draft message.
        :param request: the flask request
        :return: message result
        """

        try:
            try: 
                # Get images previously uploaded that needs to be deleted
                image_id_to_delete = json.loads(request.form['delete_image_ids'])
            except KeyError:
                image_id_to_delete = []
            try:
                # Get users previously uploaded that needs to be deleted
                user_id_to_delete = json.loads(request.form['delete_user_ids'])
            except KeyError:
                user_id_to_delete = []
            try: 
                msg_id = request.form["message_id"]
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
            payload = str(_data)
            payload = payload.replace("\"","\'")
            #print(payload)
            #get_data = json.loads(request.form['payload'])
            #payload = str({"destinator": get_data["destinator"],
            #            "title":get_data["title"],"date_of_delivery":get_data["date_of_delivery"],
            #            "time_of_delivery":get_data["time_of_delivery"],"content":get_data["content"],"font":get_data["font"]})
            #
            #payload = payload.replace("\'","\"")
            userToDelete = user_id_to_delete
            imageToDelete = image_id_to_delete
            print(request.form['payload'])
            data = dict(payload=str(request.form['payload']),sender=sender_id,message_id=msg_id,delete_image_ids=imageToDelete,delete_user_ids=userToDelete)
            print(data)
            files = {}
            for image in request.files:
                files["file"+image] = request.files[image]
            #files = {'file1': open('report.xls', 'rb'), 'file2': open('otherthing.txt', 'rb')}
            #r = requests.post('http://httpbin.org/post', files=files)
            ##data = dict(payload=payload)
            #print(data)
            response = requests.post("%s/message/draft" % (cls.MESSAGES_ENDPOINT),
                                    json=_data,
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS,
                                    )
            print(response)
            json_payload = response.json()
            if response.status_code == 200 | response.status_code == 201:
                return '{"message":"OK"}'
            elif response.status_code == 400:
                return '{"message":"KO"}'
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    