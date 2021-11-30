from mib.auth.user import User
from mib import app
from flask_login import (logout_user)
from flask import abort
import requests


class UserManager:
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

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
            url = "%s/create_user" % cls.USERS_ENDPOINT
            response = requests.post(url,
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

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def update_user(cls, user_id: int, email: str, password: str, phone: str):
        """
        This method contacts the users microservice
        to allow the users to update their profiles
        :param phone:
        :param password:
        :param email:
        :param user_id: the customer id
            email: the user email
            password: the user password
            phone: the user phone
        :return: User updated
        """
        try:
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.put(url,
                                    json={
                                        'email': email,
                                        'password': password,
                                        'phone': phone
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )
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
    def set_content_filter(cls, user_id: int, filter_v: bool):
        """
        This method contacts the users microservice
        to set the content filter of the user
        :param user_id: the user id
        :param filter_v: the value of the content filter
        :return: User updated
        """
        payload = dict(filter = filter_v)
        try:
            url = "%s/myaccount/set_content/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.put(url, json = payload, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response