import secrets
import time
import configparser

from flask import jsonify

from database import Database

config = configparser.ConfigParser()


def config_init(path):
    config.read(path)


authorize = {}
PERMISSION_AUTHORIZATION = {
    # 0 - Admin
    # 1 - Farmer
    # 2 - User
    "logout": [0, 1, 2],
    "personal_area": [0, 1, 2],
    "favorit_product": [0, 1, 2],
    "get_label": [0, 1, 2],
    "add_grow": [0, 1, 2],
    "cart": [0, 1, 2]
}


def check_auth(headers, name):
    if headers.get('Token') != str(config['FLASK_APP']['SECRET_KEY']):
        return jsonify({'message': 'Не верный Token'}), 401, {'ContentType': 'application/json'}

    user = authorize.get(headers.get('UserToken'))
    if user == None:
        return jsonify({'message': 'Не верный UserToken'}), 401, {'ContentType': 'application/json'}

    allowed = user.allow(user, name.rsplit('.')[1])
    if allowed != True:
        return allowed

    return True


class User ():
    __id = None
    __email = None
    __role = None
    __last_login = None
    __user_token = None
    __time_auth = None

    @classmethod
    def set_user_id(self, id):
        self.__id = id

    @classmethod
    def set_email(self, email):
        self.__email = email

    @classmethod
    def set_role(self, role_):
        self.__role = role_

    @classmethod
    def set_last_login(self, last):
        self.__last_login = last

    @classmethod
    def get_last_login(self):
        return self.__last_login

    @classmethod
    def get_email(self):
        return self.__email

    @classmethod
    def get_id(self):
        return self.__id

    @classmethod
    def get_role(self):
        return self.__role

    @classmethod
    def get_token(self):
        return self.__user_token

    @classmethod
    def __generate_token(self):
        length = 256
        self.__user_token = secrets.token_urlsafe(length)

    @classmethod
    def token_check(self):
        return True if (time.time() - self.__time_auth) < self.__ttl else False

    @classmethod
    def auth(self, user_):
        self.__generate_token()
        self.__time_auth = int(time.time()) + 10800
        authorize[self.__user_token] = user_

    @classmethod
    def allow(self, user, name_func):
        if self.__time_auth < time.time():
            authorize.pop(self.__user_token)
            return jsonify({'message': 'UserToken больше не действителен'}), 401, {'ContentType': 'application/json'}
        permission_name = PERMISSION_AUTHORIZATION.get(name_func)
        if permission_name == None:
            return jsonify({'message': 'Нет доступа'}), 403, {'ContentType': 'application/json'}
        if not self.__role in permission_name:
            return jsonify({'message': 'Нет доступа'}), 403, {'ContentType': 'application/json'}

        return True
