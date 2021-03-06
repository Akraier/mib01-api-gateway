from mib import app
from flask_login import (logout_user)
from flask import abort
import requests
import json

class LotteryManager:
    LOTTERY_ENDPOINT = app.config['LOTTERY_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']
    @classmethod 
    def create_lottery_row(cls,id_:int):
        try:
            lottery_url = "%s/lottery/%s" % (cls.LOTTERY_ENDPOINT, str(id_)) 
            response_lottery = requests.post(lottery_url,
                                    json = {'id': id_},
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        
        return response_lottery

    @classmethod
    def retrieve_by_id(cls, id_:int):
        try:
            response = requests.get("%s/lottery/%s" % (cls.LOTTERY_ENDPOINT,str(id_)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if json_payload['status'] != 'success':
                return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return json_payload['lottery_row']
    
    
    @classmethod
    def update_lottery_number(cls, id_ : int, val_ : int):
        try:
            url = "%s/lottery/select_number/%s" % (cls.LOTTERY_ENDPOINT,str(id_))
            response = requests.post(url,
                                    json = {'val_': val_},
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if json_payload['status'] != 'success':
                return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        response = {'status': 'success'}
        return response
    
    @classmethod
    def update_lottery_points(cls, id_ : int, val_ : int):
        try:
            url = "%s/lottery/update_points" % (cls.LOTTERY_ENDPOINT)
            response = requests.post(url,
                                    json = {'userid': id_, 'value': val_},
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            return json_payload
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response


       
    
    
    
    
