from classes import Category
from database import SQLProvider, SQLContextManager, SQLTransactionContextManager
from flask import request

provider = SQLProvider("supply_blueprint/sql")


def get_all_categories() -> list[Category]:
    ret: list[Category] = []
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_all_categories.sql"))
        rows = cur.fetchall()
        for row in rows:
            ret.append(Category(row[0], row[1], row[2]))

    return ret


def add_goodtype():
    goodtype_id = int(request.form["goodtype_id"])
    name = request.form["name"]
    category_id = int(request.form["category_id"])
    measure_unit = request.form["measure_unit"]
    sell_price = int(request.form["sell_price"])
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("add_goodtype.sql"),
            [goodtype_id, name, category_id, measure_unit, sell_price],
        )


def add_batch():
    supply_unit_price = int(request.form["supply_unit_price"])
    supply_size = int(request.form["supply_size"])
    goodtype_id = int(request.form["goodtype_id"])
    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(
            provider.get("add_batch.sql"),
            [supply_unit_price, supply_size, goodtype_id],
        )
        cur.execute(
            provider.get("update_goodtype.sql"),
            [supply_size, goodtype_id],
        )

        conn.commit()
