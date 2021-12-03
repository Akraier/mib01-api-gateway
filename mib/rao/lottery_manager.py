from mib import app
from flask_login import (logout_user)
from flask import abort
import requests
import json

class LotteryManager:
    LOTTERY_ENDPOINT = app.config['LOTTERY_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def retrieve_by_id(cls, id_:int):
        try:
            response = requests.get("%s/lottery/%s" % (cls.LOTTERY_ENDPOINT,str(id_)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            print("THE RESPONSE OF GET LOTTERY NUMBER:::::::", json_payload)
            if json_payload['status'] != 'success':
                return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return json_payload['lottery_row']
    
    
    @classmethod
    def update_lottery_number(cls, id_ : int, val_ : int):
        try:
            response = requests.post("%s/lottery/select_number/%s" % (cls.LOTTERY_ENDPOINT,str(id_)),
                                    json = {'number_selected': val_},
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            print("THE RESPONSE OF GET LOTTERY NUMBER:::::::", json_payload)
            if json_payload['status'] != 'success':
                return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        response = {'status': 'success'}
        return jsonify(response)
    
    
