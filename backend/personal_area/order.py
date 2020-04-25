import re

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from database import Database

order_bp = Blueprint('order', __name__)


@order_bp.route('/create_order', methods=['POST'])
def order():
    """Order"""
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

    file = request.get_json(silent=True)
    if file != None:
        # Получение корзины
        cart = get_cart()
        # Отправка order в базу данных
        order = {
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

def get_cart():
    query = sql.SQL("SELECT * FROM public.address WHERE user_id="+str(id))
    vozvrat = database.select_data(query)