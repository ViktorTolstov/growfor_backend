from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from database import Database

get_label_bp = Blueprint('get_label', __name__)


@get_label_bp.route('/get_label', methods=['GET'])
def get_label():
    """Add product in favorite for user"""

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

    vozvrat = []

    fields = [
        "u.firstname",
        "u.lastname",
        "up.id",
        "up.name",
        "up.photo",
        "up.type",
        "up.method",
        "up.sale",
        "up.price",
        "c.name",
        "up.weight",
        "u2.name",
        "fp.id",
        "a.country",
        "a.city",
        "a.address",
        "a.lat",
        "a.lng"
    ]

    query = sql.SQL("SELECT {} FROM users u \
        RIGHT JOIN users_product up on u.id = up.user_id\
        LEFT JOIN units u2 on up.unit_id = u2.id\
        LEFT JOIN currencys c on up.currency_id = c.id\
        LEFT JOIN favorit_products fp on u.id = fp.user_id\
        LEFT JOIN address a on up.address_id = a.id").format(
        sql.SQL(",").join(sql.Identifier(
            i.split('.')[0], i.split('.')[1]) for i in fields)
    )
    execute = database.select_data(query)
    if type(execute) != list:
        return execute

    data_append = {}
    for row in execute:
        for i in range(len(fields)):
            value = row[i]

            if fields[i] == "up.id":
                fields[i] = "up.users_product_id"
            if fields[i] == "c.name":
                fields[i] = "c.currency"
            if fields[i] == "u2.name":
                fields[i] = "u2.unit"
            if fields[i] == "fp.id":
                fields[i] = "fp.is_favorit"
                value = True if value != None else False

            data_append[fields[i].split('.')[1]] = value
        vozvrat.append(data_append)

    return jsonify(vozvrat)
