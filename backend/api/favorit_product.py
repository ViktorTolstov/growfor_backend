from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from psycopg2 import sql

from app.models import check_auth, authorize, config
from database import Database

favorit_product_bp = Blueprint('favorit_product', __name__)


@favorit_product_bp.route('/add_favorit_product', methods=['POST'])
def add_favorit_product():
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

    file = request.get_json(silent=True)
    if file != None:
        if file.get("users_product_id") == None or type(file.get("users_product_id")) != int:
            return jsonify({"messageError": "Выберете товар, который нужно добавить в избранное"})
        favorite = {
            "user_id": user.get_id(),
            "users_product_id": int(file.get("users_product_id"))
        }

        query = sql.SQL("SELECT {column} FROM {table} WHERE {condition}").format(
            table=sql.Identifier("public", "favorit_products"),
            column=sql.SQL(',').join(
                sql.Identifier(i) for i in ["id"]),
            condition=sql.SQL('user_id={user_id} and users_product_id={users_product_id}').format(
                user_id=sql.Literal(favorite['user_id']),
                users_product_id=sql.Literal(favorite['users_product_id'])
            )
        )

        vozvrat = database.select_data(query)

        if type(vozvrat) != list:
            return vozvrat

        if len(vozvrat) == 0:
            query = sql.SQL("INSERT INTO {table}({column}) VALUES({value})").format(
                table=sql.Identifier("public", "favorit_products"),
                column=sql.SQL(',').join(
                    sql.Identifier(i) for i in ["user_id", "users_product_id"]),
                value=sql.SQL(',').join(sql.Literal(i)
                                        for i in [user.get_id(), int(file.get("users_product_id"))])
            )

            vozvrat = database.insert_data(query)
            if vozvrat != True:
                return vozvrat
            vozvrat = {"is_favorit": True}
        else:
            query = sql.SQL("DELETE FROM {table} WHERE id={id}").format(
                table=sql.Identifier("public", "favorit_products"),
                id=sql.Literal(vozvrat[0][0])
            )

            vozvrat = database.insert_data(query)
            if vozvrat != True:
                return vozvrat
            vozvrat = {"is_favorit": False}
    else:
        vozvrat["messageError"] = "JSON отсутсвует"

    return jsonify(vozvrat)
