from database import SQLContextManager, SQLProvider
from flask import g

provider = SQLProvider("main_menu_blueprint/sql")


def get_personal():
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_personal.sql"), [g.user.u_id])
        return cur.fetchone()
