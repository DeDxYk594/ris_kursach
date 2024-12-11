from flask import Flask, current_app
from pymysql.cursors import Cursor
from pymysql import connect, Connection
import os


db_config: dict = {}


def init_mysql(app: Flask):
    global db_config
    db_config = app.config["db_config"]


class SQLProvider:
    def __init__(self, file_path):
        self._file_path = file_path
        self.scripts = {}
        for file in os.listdir(file_path):
            sql = open(f"{file_path}/{file}").read()
            self.scripts[file] = sql

    def get(self, file) -> str:
        if current_app.debug:
            with open(f"{self._file_path}/{file}") as f:
                return f.read()
        return self.scripts[file]


class SQLContextManager:
    """Контекстный менеджер без транзакционности"""

    def __init__(self):
        self.conn = connect(**db_config)
        self.cursor = self.conn.cursor()

    def __enter__(self) -> Cursor:
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.conn.commit()
            self.cursor.close()
        if exc_type:
            raise
        return True


class SQLTransactionContextManager:
    """Контекстный менеджер с транзакцией.
    Нужно явно вызвать conn.commit(), иначе транзакция будет откачена"""

    def __init__(self):
        self.conn = connect(**db_config)
        self.cursor = self.conn.cursor()

    def __enter__(self) -> tuple[Connection, Cursor]:
        self.conn.begin()
        return (self.conn, self.cursor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            # Если уже был вызов conn.commit(), rollback просто ничего не сделает
            self.conn.rollback()
            self.cursor.close()
        if exc_type:
            raise
        return True
