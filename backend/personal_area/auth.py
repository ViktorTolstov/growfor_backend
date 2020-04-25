import re
import configparser

from flask import Blueprint, request, make_response, jsonify
from werkzeug.security import check_password_hash

from app.models import User, authorize, config
from database import Database

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['POST'])
def auth_api():
    if request.headers.get('Token') != str(config['FLASK_APP']['SECRET_KEY']):
        return jsonify({'message': 'Не верный токен'}), 401, {'ContentType': 'application/json'}
    try:
        database = Database(config)
    except TypeError:
        return jsonify({"message": "Нет подключения к БД"})
    email = request.get_json(silent=True).get("email")
    password = request.get_json(silent=True).get("password")
    user_data = database.login({"email": email})

    if user_data:
        if check_password_hash(user_data[1], password):
            user = User()
            user.set_user_id(user_data[0])
            user.set_role(user_data[2])
            user.set_email(email)
            user.auth(user)
            user.set_last_login(database.select_data(
                "SELECT last_login FROM public.users WHERE id={}".format(user.get_id()))[0][0])
            database.insert_data("UPDATE users SET last_login=now() \
                                WHERE id='{id}'".format(
                id=user.get_id()
            ))
            return jsonify({"UserToken": user.get_token(), "role": user.get_role()})
    return jsonify({'message': 'Invalid email or password'}), 401, {'ContentType': 'application/json'}
