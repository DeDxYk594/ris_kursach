from flask import Flask
from sqlalchemy import create_engine, Engine
import os


db_conn: Engine = None


def init_mysql(app: Flask):
    global db_conn
    db_conn = create_engine(
        app.config["db_config"]["dsn"],
        pool_size=app.config["db_config"].get("pool_size", 5),
        max_overflow=app.config["db_config"].get("max_overflow", 10),
        pool_timeout=app.config["db_config"].get("pool_timeout", 30),
        pool_recycle=app.config["db_config"].get("pool_recycle", 1800),
    )


class SQLProvider:
    def __init__(self, file_path):
        self.scripts = {}
        for file in os.listdir(file_path):
            sql = open(f"{file_path}/{file}").read()
            self.scripts[file] = sql

    def get(self, file):
        return self.scripts[file]


class DBContextManager:
    def __init__(self, db_config: dict):
        self.conn = None
        self.cursor = None
        self.db_config = db_config

    def __enter__(self):
        self.conn = db_conn.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # в параметрах метода лежат ошибки, которые передаёт sql сервер при ошибке
        if exc_type:
            print(exc_type)
        if self.cursor:
            if exc_type:
                # если на этапе выполнения произошли ошибки, но курсор при этом открыт, то скорее всего это транзакция и её надо откатить
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()
        return True
