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
            response = requests.get("%s/user/%s" % (cls.LOTTERY_ENDPOINT,str(id_)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                print("PAYLOAAAAAAD----"+json_payload)
                return json_payload
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return 'user'
    
