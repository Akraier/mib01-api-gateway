from flask.json import jsonify
from mib.auth.user import User
from mib import app
from flask_login import (logout_user)
from flask import abort
import requests


class UserManager:
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']
    LOTTERY_ENDPOINT = app.config['LOTTERY_MS_URL']

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                # user is authenticated
                user = User.build_from_json(json_payload)
            elif response.status_code == 404:
                return None
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def get_user_by_email(cls, user_email: str):
        """
        This method contacts the users microservice
        and retrieves the user object by user email.
        :param user_email: the user email
        :return: User obj with email=user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (cls.USERS_ENDPOINT, user_email),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user


    @classmethod
    def create_user(cls,
                    email: str, password: str,
                    firstname: str, lastname: str,
                    birthdate, phone: str):
        try:
            # we need to initialize both the lottery and the user db
            print(cls.USERS_ENDPOINT)
            usr_url = "%s/create_user" % cls.USERS_ENDPOINT
            response_usr = requests.post(usr_url,
                                     json={
                                         'email': email,
                                         'password': password,
                                         'firstname': firstname,
                                         'lastname': lastname,
                                         'birthdate': str(birthdate),
                                         'phone': phone
                                     },
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )
            print("STAMPO LA RISPOSTAAAAAAAAAAAAAA")
            print(response_usr.json())
            id = response_usr.json()['user']['id'] #get the user id just created
            
            lottery_url = "%s/lottery/%s" % (cls.LOTTERY_ENDPOINT, str(id))
            response_lottery = requests.post(lottery_url,
                                     json = {'id': id},
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )

            print("STAMPO LA RISPOSTAA di LOTTERYYYYYYYYYYYYY")
            print(response_lottery.json())
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
        
        null_response = {
            'user': None,
            'status': 'error',
            'message': 'Some error occurred during the registration process',
        }
        print("LOTTERY     ",response_lottery)
        print("USR         ", response_usr)
        #check for errors
        if response_lottery.json()['status'] != 'success' or response_usr.json()['status'] != 'success':
            return null_response
        else:
            return response_usr

    @classmethod
    def update_user(cls, user_id: int, email: str, password: str, firstname: str, lastname: str, birthdate: str, newpassword: str):
        """
        This method contacts the users microservice
        to allow the users to update their profiles
        """
        try:
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.put(url,
                                    json={
                                        'email': email,
                                        'password': password,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'birthdate': birthdate,
                                        'newpassword': newpassword
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
            print(response)
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        raise RuntimeError('Error with searching for the user %s' % user_id)

    @classmethod
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: User updated
        """
        try:
            logout_user()
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response


    @classmethod
    def authenticate_user(cls, email: str, password: str) -> User:
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        try:
            print('trying response....')
            response = requests.post('%s/authenticate' % cls.USERS_ENDPOINT,
                                     json=payload,
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )
            print('received response....')
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        if response.status_code == 401:
            # user is not authenticated
            return None
        elif response.status_code == 200:
            user = User.build_from_json(json_response['user'])
            return user
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['error_message'])
            )


    #Method to retrieve all the active users in the database
    @classmethod
    def get_all_users(cls) -> User:
        """
        This method contacts the users microservice
        and retrieves all user object.
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/users" % (cls.USERS_ENDPOINT), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                #we have to build a list of User obj
                print(json_payload)
                list_user = json_payload['users_list']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return list_user
    @classmethod
    def get_user_by_first_letter(cls, first_letter: str ):
        """This method contact the user microservice asking the user with firstname starting with 'first_letter' """
        try:
            response = requests.get("%s/user_firstletter/%s" % (cls.USERS_ENDPOINT, first_letter),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user
    @classmethod
    def set_content_filter(cls, user_id: int, filter_v: bool):
        """
        This method contacts the users microservice
        to set the content filter of the user
        :param user_id: the user id
        :param filter_v: the value of the content filter
        :return: User updated
        """
        payload = dict(filter = filter_v, id = user_id)
        print("this is the payload: ", payload)
        try:
            url = "%s/myaccount/set_content" % (cls.USERS_ENDPOINT)
            response = requests.put(url, json = payload, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            print("this is the response: ", response)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    
     #Method to retrieve the blacklist from the database
    @classmethod
    def get_blacklist(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the blacklist.
        """
       
        try:
            response = requests.get("%s/user/blacklist/%d" % (cls.USERS_ENDPOINT,user_id), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            print(response)
            json_payload = response.json()
            if response.status_code == 200:
                #we have to build a list of User obj
                print(json_payload)
                black_user = json_payload['black_list']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return black_user
        
    @classmethod
    def delete_blacklist(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and delete the blacklist
        """
       
        try:
            response = requests.delete("%s/user/blacklist/%d" % (cls.USERS_ENDPOINT,user_id), timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            print(response)
            json_payload = response.json()
            if response.status_code == 200:
                #we have to build a list of User obj
                print(json_payload)
                black_user = json_payload['content']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return black_user

    #/user/blacklist/target
    @classmethod
    def insert_blacklist(cls, user_id: int, black_id: int) -> User:
        """
        This method contacts the users microservice
        and  adds a target to the blacklist
        """
       
        try:
            payload = {'user_id':user_id,'black_id':black_id}
            response = requests.post("%s/user/blacklist/target" % (cls.USERS_ENDPOINT),json=payload, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                #we have to build a list of User obj
                print(json_payload)
                black_user = json_payload['content']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return black_user

 #/user/blacklist/target
    @classmethod
    def delete_blacklist_target(cls, user_id: int, black_id: int) -> User:
        """
        This method contacts the users microservice
        and delete a target to the blacklist
        """
       
        try:
            payload = {'user_id':user_id,'black_id':black_id}
            response = requests.delete("%s/user/blacklist/target" % (cls.USERS_ENDPOINT),json=payload, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                #we have to build a list of User obj
                print(json_payload)
                black_user = json_payload['content']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return black_user


            