import datetime
import time

import psycopg2
from psycopg2 import sql


class Database():
    conn = None

    def __init__(self, config):
        self.conn = self.connect(config)

    def connect(self, config):
        """Connect to database PostgreSQL"""
        try:
            conn = psycopg2.connect(
                dbname=str(config['POSTGRES']['DATABASE']),
                user=str(config['POSTGRES']['USER']),
                password=str(config['POSTGRES']['PASSWORD']),
                host=str(config['POSTGRES']['HOST']),
                port=str(config['POSTGRES']['PORT']))
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError:
            return False

    def close(self):
        """Close connect with database"""
        self.conn.close()
        return True

    def select_data(self, execute):
        cursor = None

        # Инициализация курсора
        try:
            cursor = self.conn.cursor()
        except AttributeError:
            return "Нет подключения к БД"

        try:
            # Если присылаемым значение было error, то вызывается исключение
            if execute == "error":
                raise AttributeError

            cursor.execute(execute)
        except AttributeError:
            return "Подключение к БД разорвано"

        return cursor.fetchall()

    def insert_data(self, execute):
        cursor = None

        # Инициализация курсора
        try:
            cursor = self.conn.cursor()
        except AttributeError:
            return "Нет подключения к БД"

        try:
            # Если присылаемым значение было error, то вызывается исключение
            if execute == "error":
                raise AttributeError

            cursor.execute(execute)
        except AttributeError:
            return "Подключение к БД разорвано"
        except psycopg2.errors.UniqueViolation:
            return "Пользователь с такой почтой уже существует"

        return True

    def login(self, data):
        cursor = None

        # Инициализация курсора
        try:
            cursor = self.conn.cursor()
        except AttributeError:
            return "Нет подключения к БД"

        # Структура содержащая значения для отправки
        values_data = {
            "email": sql.Literal(data["email"])
        }
        # Структура содержащая поля для отправки
        columns = {
            "email": sql.Identifier("email")
        }

        # Формирование выражения для условия
        condition = []
        for key in data:
            condition.append(sql.SQL("=").join(
                val for val in [columns[key], values_data[key]]
            ))

        # Формирование структуры для подстановке к запросу
        values = {
            "field": sql.SQL(",").join(sql.Identifier(i) for i in ["id", "password", "role"]),
            "table": sql.Identifier("public", "users"),
            "condition": sql.SQL(" and ").join(cond for cond in condition)
        }

        query = "SELECT {field} FROM {table} WHERE {condition};"
        cursor.execute(sql.SQL(query).format(**values))
        psw = cursor.fetchone()
        return (psw if psw != None else False)
