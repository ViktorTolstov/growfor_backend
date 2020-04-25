import re

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from database import Database

add_grow_bp = Blueprint('add_grow', __name__)


@add_grow_bp.route('/grow', methods=['GET', 'POST'])
def add_grow():
    """Grow"""
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

    # Получение существующих юнитов
    if request.method == 'GET':
        vozvrat = get_units(database,user.get_id())
        return jsonify(vozvrat)
    # Добавление новой карточки товара
    elif request.method == 'POST':
        file = request.get_json(silent=True)
        if file != None:
            product = {
                "user_id": user.get_id(),
                "method": file.get("method"),
                "name": file.get("name"),
                "type": file.get("type"),
                "photo": file.get("photo"),
                "price": file.get("price"),
                "currency_id": file.get("currency_id"),
                "weight": file.get("weight"),
                "unit_id": file.get("unit_id"),
                "sale": file.get("sale"),
            }
            result = execute_to_base(database, product)

            if result == True:
                vozvrat["messageSuccess"] = "Карточка успешно добавлена"
            else:
                vozvrat["messageError"] = result
        else:
            vozvrat["messageError"] = "JSON отсутсвует"
        return jsonify(vozvrat)


def execute_to_base(database, product):
    values_data = {}
    columns = {}
    for col in product:
        columns[col] = sql.Identifier(col)
        values_data[col] = sql.Literal(product[col])

    query = sql.SQL("INSERT INTO {table}({column}) VALUES({value})").format(
        table=sql.Identifier("public", "users_product"),
        column=sql.SQL(',').join(
            columns[col] for col in columns),
        value=sql.SQL(',').join(
            values_data[val] for val in values_data),
    )
    vozvrat = database.insert_data(query)
    return vozvrat


def get_units(database,id):
    vozvrat = {}
    query = sql.SQL("SELECT * FROM public.currencys")
    vozvrat["currency"] = database.select_data(query)
    query = sql.SQL("SELECT * FROM public.units")
    vozvrat["units"] = database.select_data(query)
    query = sql.SQL("SELECT * FROM public.address WHERE user_id="+str(id))
    vozvrat["address"] = database.select_data(query)
    return vozvrat
