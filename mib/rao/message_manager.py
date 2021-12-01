from mib import app
from flask_login import (logout_user)
from flask import abort
import requests


class MessageManager:
    MESSAGES_ENDPOINT = app.config['MESSAGES_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def save_draft(cls, request):
        """
        This method contacts the message microservice
        and let creation of a new draft message.
        :param request: the flask request
        :return: message result
        """
        try:
            response = requests.get("%s/message/draft" % (cls.MESSAGES_ENDPOINT),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            #if response.status_code == 200:
            #     # user is authenticated
            #     user = User.build_from_json(json_payload)
            # else:
            #     raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
            print(response)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return 'user'

    