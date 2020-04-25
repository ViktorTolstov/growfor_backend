import re
import time

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from personal_area.registration import valid_email, valid_password
from database import Database

personal_area_bp = Blueprint('personal_area', __name__)


@personal_area_bp.route('/personal_area', methods=['GET', 'POST'])
def personal_area():
    """Personal area user`s"""

    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))

    vozvrat = {}
    try:
        database = Database(config)
    except TypeError:
        vozvrat["messageError"] = "Нет подключения к БД"
        return jsonify(vozvrat)

    if request.method == "GET":
        # Выдача текущих данных о пользователе
        user_data = {
            "email": user.get_email()
        }
        columns = [
            "firstname",
            "lastname",
            "patronymic",
            "number_phone",
            "role",
            "inn",
            "certificate",
            "intresting",
            "url_instagram",
            "url_vk",
            "equipment_id",
            "fertilizer",
            "saleform"
        ]
        query = sql.SQL("SELECT {fields} FROM {table} WHERE {condition}").format(
            fields=sql.SQL(",").join(sql.Identifier(i) for i in columns),
            table=sql.Identifier("public", "users"),
            condition=sql.SQL("id={}").format(
                sql.Literal(user.get_id()))
        )
        execute = database.select_data(query)
        if len(execute) == 0:
            return jsonify({"messageError": "Пользователь отсутсвует"})
        execute = execute[0]
        for i in range(len(execute)):
            user_data[columns[i]] = execute[i]

        # Получения адреса пользователя
        columns = [
            "country",
            "city",
            "address",
            "lat",
            "lng"
        ]

        query = sql.SQL("SELECT {fields} FROM {table} WHERE {condition}").format(
            fields=sql.SQL(",").join(sql.Identifier(i) for i in columns),
            table=sql.Identifier("public", "address"),
            condition=sql.SQL("user_id={}").format(
                sql.Literal(user.get_id()))
        )
        execute = database.select_data(query)
        user_data["addressData"] = {}
        if len(execute) == 0:
            for i in range(len(columns)):
                user_data["addressData"][columns[i]] = None
        else:
            execute = execute[0]
            for i in range(len(execute)):
                user_data["addressData"][columns[i]] = execute[i]

        return jsonify(user_data)

    # Изменение данных о пользователе
    file = request.get_json(silent=True)
    if file != None and request.method == "POST":
        is_farmer = True if file.get("farmer") == True else False
        user_data = {
            "email": file.get("email"),
            "password": file.get("password"),
            "confirm_password": file.get("confirm_password"),
            "firstname": file.get("firstname"),
            "lastname": file.get("lastname"),
            "patronymic": file.get("patronymic"),
            "number_phone": file.get("number_phone"),
            "role": 1 if is_farmer else 2,
            "inn": file.get("inn"),
            "certificate": file.get("certificate"),
            "intresting": file.get("intresting"),
            "url_instagram": file.get("url_instagram"),
            "url_vk": file.get("url_vk"),
            "equipment_id": file.get("equipment_id"),
            "fertilizer": file.get("fertilizer"),
            "saleform": file.get("saleform"),
            "country": file.get("addressData").get("country") if is_farmer else None,
            "city": file.get("addressData").get("city") if is_farmer else None,
            "address": file.get("addressData").get("address") if is_farmer else None,
            "lat": file.get("addressData").get("lat") if is_farmer else None,
            "lng": file.get("addressData").get("lng") if is_farmer else None
        }

        # Проверка введённых данных
        valid = valid_data(user_data)
        if valid != True:
            vozvrat["messageError"] = valid
            return jsonify(vozvrat)

        user_data["id"] = user.get_id()
        if not user_data['password'] in [None, '']:
            user_data['password'] = generate_password_hash(
                user_data['password'], method='sha256')
        result = execute_to_base(database, user_data)

        if result == True:
            vozvrat["messageSuccess"] = "Данные обновлены"
        else:
            vozvrat["messageError"] = result
    else:
        vozvrat["messageError"] = "JSON отсутсвует"
    return jsonify(vozvrat)


def valid_data(user_data):
    if user_data['password'] != None:
        valid = valid_password(
            user_data['password'], user_data['confirm_password'])
        if valid != True:
            return valid

    valid = valid_email(user_data['email'])
    if valid != True:
        return valid

    if user_data['role'] == 1:
        for col in ["inn", "country", "city", "address", "lat", "lng"]:
            if user_data[col] == None:
                return "Не заполненны обязательные поля для фермера"
    return True


def execute_to_base(database, user_data):
    execute = database.select_data(sql.SQL(
        "SELECT email, last_change FROM public.users WHERE id={}").format(sql.Literal(user_data['id'])))

    if (time.time() - time.mktime(execute[0][1].timetuple())) <= 3600:
        return "Нельзя так часто обновлять данные"
    if user_data['email'] == execute[0][0]:
        user_data['email'] = True
    if user_data['password'] in [None, '']:
        user_data['password'] = True

    values_data = {}
    columns = {}
    values_data_adress = {}
    columns_address = {}
    for col in user_data:
        if col == 'email' and user_data['email'] == True:
            continue
        if col == 'password' and user_data['password'] == True:
            continue

        if not col in ["confirm_password", "country", "city", "address", "lat", "lng"]:
            columns[col] = sql.Identifier(col)
            values_data[col] = sql.Literal(user_data[col])
        elif not col in ["confirm_password"]:
            columns_address[col] = sql.Identifier(col)
            values_data_adress[col] = sql.Literal(user_data[col])

    columns['last_change'] = sql.Identifier("last_change")
    values_data['last_change'] = sql.SQL("now()")

    query = sql.SQL("UPDATE {table} SET ({column})=({value}) WHERE {condition}").format(
        table=sql.Identifier("public", "users"),
        column=sql.SQL(',').join(
            columns[col] for col in columns),
        value=sql.SQL(',').join(
            values_data[val] for val in values_data),
        condition=sql.SQL("id={}").format(sql.Literal(user_data['id']))
    )
    vozvrat = database.insert_data(query)
    if vozvrat != True:
        return vozvrat

    if user_data["role"] == 1:
        query_address = sql.SQL("UPDATE {table} SET ({column})=({value}) WHERE {condition}").format(
            table=sql.Identifier("public", "address"),
            column=sql.SQL(',').join(
                columns_address[col] for col in columns_address),
            value=sql.SQL(',').join(
                values_data_adress[val] for val in values_data_adress),
            condition=sql.SQL("id={}").format(
                sql.Literal(user_data['id']))
        )
        vozvrat = database.insert_data(query_address)

    database.close()
    return vozvrat
