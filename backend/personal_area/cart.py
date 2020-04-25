from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from personal_area.registration import valid_email, valid_password
from database import Database

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart', methods=['GET', 'POST', 'DELETE'])
def cart():
    """Cart user`s"""

    user = check_auth(request.headers, __name__)
    if user != True:
        return user
    user = authorize.get(request.headers.get('UserToken'))

    try:
        database = Database(config)
    except TypeError:
        vozvrat["messageError"] = "Нет подключения к БД"
        return jsonify(vozvrat)

    vozvrat = None
    execute = None
    data_cart = {
        "user_id": user.get_id()
    }

    if request.method == 'GET':
        fields = [
            "up.id",
            "up.name",
            "up.photo",
            "c.sale",
            "up.weight",
            "c.weight_user",
            "c.price_for_user",
            "c.farmer_price",
            "c2.name",
            "u.name"
        ]

        query = sql.SQL("\
        SELECT\
            {column}\
        FROM public.cart c\
        LEFT JOIN users_product up on c.users_product_id = up.id\
        LEFT JOIN currencys c2 on up.currency_id = c2.id\
        LEFT JOIN units u on up.unit_id = u.id\
        WHERE {condition}").format(

            column=sql.SQL(',').join(
                sql.SQL(i) for i in fields),
            condition=sql.SQL('c.user_id={user_id}').format(
                user_id=sql.Literal(data_cart['user_id'])
            )
        )

        execute = database.select_data(query)

        if type(execute) != list:
            return jsonify(execute)

        if len(execute) == 0:
            return jsonify({'messageError': "Корзина пустая"})

        vozvrat = []
        data_append = {}
        for row in execute:
            for i in range(len(fields)):
                value = row[i]
                if fields[i] == "up.id":
                    fields[i] = "up.users_product_id"
                elif fields[i] == "c2.name":
                    fields[i] = "c2.currency"
                elif fields[i] == "u.name":
                    fields[i] = "u.unit"
                elif fields[i] == "up.weight":
                    fields[i] = "up.weight_farmer"

                data_append[fields[i].split('.')[1]] = value
            vozvrat.append(data_append)

        return jsonify(vozvrat)

    file = request.get_json(silent=True)
    if file != None:
        if file.get("users_product_id") == None or type(file.get("users_product_id")) != int:
            return jsonify({"messageError": "Выберете товар, который нужно добавить в корзину"})
        data_cart["users_product_id"] = int(file.get("users_product_id"))

        query = sql.SQL("SELECT {column} FROM {table} WHERE {condition}").format(
            table=sql.Identifier("public", "cart"),
            column=sql.SQL(',').join(
                sql.Identifier(i) for i in ["id"]),
            condition=sql.SQL('user_id={user_id} and users_product_id={users_product_id}').format(
                user_id=sql.Literal(data_cart['user_id']),
                users_product_id=sql.Literal(data_cart['users_product_id'])
            )
        )

        execute = database.select_data(query)

        if type(execute) != list:
            return execute
    else:
        vozvrat["messageError"] = "JSON отсутсвует"

    if request.method == 'DELETE' and len(execute) != 0:
        query = sql.SQL("DELETE FROM {table} WHERE {condition}").format(
            table=sql.Identifier("public", "cart"),
            condition=sql.SQL('user_id={user_id} and users_product_id={users_product_id}').format(
                user_id=sql.Literal(data_cart['user_id']),
                users_product_id=sql.Literal(data_cart['users_product_id'])
            )
        )

        execute = database.insert_data(query)
        if execute != True:
            return execute
        vozvrat = {"messageSuccess": "Товар удалён из корзины"}

    elif request.method == 'DELETE' and len(execute) == 0:
        return jsonify({'messageError': "Товар отсутствует в корзине"})

    if request.method == 'POST' and len(execute) == 0:
        data_cart["weight_user"] = float(file.get("weight"))
        if data_cart["weight_user"] == None:
            return jsonify({'messageError': "Укажите вес товара"})

        fields = [
            "weight",
            "sale",
            "price",
            "currency_id",
            "unit_id"
        ]

        query = sql.SQL("\
        SELECT\
            {column}\
        FROM public.users_product\
        WHERE {condition}").format(

            column=sql.SQL(',').join(
                sql.SQL(i) for i in fields),
            condition=sql.SQL('id={users_product_id}').format(
                users_product_id=sql.Literal(data_cart['users_product_id'])
            )
        )

        execute = database.select_data(query)

        if type(execute) != list:
            return jsonify(execute)

        if len(execute) == 0:
            return jsonify({'messageError': "Такого товара не существует"})

        execute = execute[0]

        data_cart["user_id"] = user.get_id()
        data_cart["farmer_price"] = float(execute[2])
        weight_farmer = float(execute[0])
        data_cart["sale"] = int(execute[1])
        data_cart["price_for_user"] = float(
            "{:.2f}".format(
                (data_cart['farmer_price'] / weight_farmer) *
                data_cart['weight_user'] * (1 + data_cart["sale"] / 100)
            )
        )

        list_value = [i[1] for i in data_cart.items()]

        query = sql.SQL("INSERT INTO {table}(adding_time, {column}) VALUES(now(), {value})").format(
            table=sql.Identifier("public", "cart"),
            column=sql.SQL(',').join(
                sql.Identifier(i) for i in data_cart),
            value=sql.SQL(',').join(sql.Literal(i) for i in list_value)
        )

        execute = database.insert_data(query)
        if execute != True:
            return execute
        vozvrat = {"messageSuccess": "Товар добавлен в корзину"}
    elif request.method == 'POST' and len(execute) != 0:
        return jsonify({'messageError': "Товар присутствует в корзине"})

    return jsonify(vozvrat)
