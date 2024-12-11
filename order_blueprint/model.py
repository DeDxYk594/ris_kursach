from classes import GoodType, Order, OrderLine, OrderStatus
from database import SQLContextManager, SQLProvider, SQLTransactionContextManager
from flask import g, request, session
import bcrypt
from datetime import datetime


provider = SQLProvider("order_blueprint/sql")


def get_goodtype_by_id(goodtype_id: int) -> GoodType | None:
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_goodtype_by_id.sql"), [goodtype_id])
        row = cur.fetchone()
        if row is None:
            return None
        return GoodType(*row)


def get_customer_orders(ext_u_id: int, page: int) -> list[Order]:
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("get_customer_orders.sql"), [ext_u_id, (page - 1) * 20]
        )
        rows = cur.fetchall()
        group: dict[int, Order] = {}
        ret: list[Order] = []
        for row in rows:
            order_id: int = row[0]
            if group.get(order_id, None) is None:
                ord = Order(order_id, row[2], OrderStatus(row[1]), [], 0, "")
                group[order_id] = ord
                ret.append(ord)

            if row[6] is None:
                continue

            group[order_id].lines.append(
                OrderLine(
                    row[3],
                    GoodType(0, row[6], row[7], "", row[8], 0, 0, 0),
                    row[4],
                    row[5],
                )
            )
            group[order_id].total_price += row[5] if row[5] is not None else 0

        return ret


def create_order() -> tuple[bool, int]:
    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(provider.get("create_order.sql"), [g.user.u_id])
        cur.execute("SELECT LAST_INSERT_ID();")
        row = cur.fetchone()
        if row is None:
            return (False, 0)
        order_id = row[0]
        cart = session["cart"]
        if cart is None:
            return (False, 0)

        for i in cart:
            cur.execute(provider.get("add_order_line.sql"), [order_id, i[0], i[3]])
            cur.execute(provider.get("set_goodtype_booked.sql"), [i[3], i[0]])

        conn.commit()
        session["cart"] = []
        return True, order_id


def estimate_customer_orders(ext_u_id: int) -> int:
    with SQLContextManager() as cur:
        cur.execute(provider.get("estimate_customer_orders.sql"), [ext_u_id])
        row = cur.fetchone()
        if row is None:
            raise ValueError("Error sql query")
        return row[0]


def estimate_active_orders() -> int:
    with SQLContextManager() as cur:
        cur.execute(provider.get("estimate_active_orders.sql"), [])
        row = cur.fetchone()

        if row is None:
            raise ValueError("Error sql query")

        return row[0]


def estimate_paid_orders() -> int:
    with SQLContextManager() as cur:
        cur.execute(provider.get("estimate_paid_orders.sql"), [])
        row = cur.fetchone()

        if row is None:
            raise ValueError("Error sql query")

        return row[0]


def annulate_order(order_id: int) -> bool:
    with SQLTransactionContextManager() as (conn,cur):
        cur.execute(provider.get("annulate_order.sql"), [order_id])
        cur.execute(provider.get("annulate_lines.sql"), [order_id])

        if cur.rowcount == 0:
            return False

        conn.commit()
        return True


def get_active_orders(page: int) -> list[Order]:
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_active_orders.sql"), [(page - 1) * 20])
        rows = cur.fetchall()
        group: dict[int, Order] = {}
        ret: list[Order] = []
        for row in rows:
            order_id: int = row[0]
            if group.get(order_id, None) is None:
                ord = Order(order_id, row[2], OrderStatus(row[1]), [], 0, row[9])
                group[order_id] = ord
                ret.append(ord)

            if row[6] is None:
                continue

            group[order_id].lines.append(
                OrderLine(
                    row[3],
                    GoodType(0, row[6], row[7], "", row[8], 0, 0, 0),
                    row[4],
                    row[5],
                )
            )
            group[order_id].total_price += row[5] if row[5] is not None else 0

        return ret


def get_paid_orders(page: int) -> list[Order]:
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_active_orders.sql"), [(page - 1) * 20])
        rows = cur.fetchall()
        group: dict[int, Order] = {}
        ret: list[Order] = []
        for row in rows:
            order_id: int = row[0]

            if group.get(order_id, None) is None:
                ord = Order(order_id, row[2], OrderStatus(row[1]), [], 0, row[9])
                group[order_id] = ord
                ret.append(ord)

            if row[6] is None:
                continue

            group[order_id].lines.append(
                OrderLine(
                    row[3],
                    GoodType(0, row[6], row[7], "", row[8], 0, 0, 0),
                    row[4],
                    row[5],
                )
            )
            group[order_id].total_price += row[5] if row[5] is not None else 0

        return ret


def get_unpaid_order(order_id: int) -> Order | None:
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_unpaid_order.sql"), [order_id])

        rows = cur.fetchall()
        if not rows:
            return None
        row0 = rows[0]

        ret: Order = Order(
            order_id=order_id,
            created_at=row0[2],
            status=OrderStatus(row0[1]),
            lines=[],
            total_price=sum([i[5] for i in rows]),
            customer_name=row0[9],
        )

        return ret


def pay_order() -> Order | str:
    order_id = int(request.form["order_id"])
    password: str = request.form["password"]
    user_id = g.user.u_id

    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(provider.get("get_password_hash.sql"), [user_id])
        row = cur.fetchone()
        if row is None:
            return "Неизвестная ошибка"

        if not bcrypt.checkpw(
            password.encode(encoding="utf-8"), row[0].encode(encoding="utf-8")
        ):
            return "Неправильный пароль"

        cur.execute(provider.get("get_unpaid_order.sql"), [order_id])
        if not cur.fetchone():
            return "Не найден заказ или заказ имеет не тот статус"

        cur.execute(provider.get("pay_lines.sql"), [order_id])
        cur.execute(provider.get("pay_order.sql"), [order_id])

        conn.commit()
        return Order(order_id, datetime.now(), OrderStatus("paid"), [], 0, "")


def ship_order(order_id: int):
    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(provider.get("ship_order.sql"), [order_id])
        cur.execute(provider.get("ship_lines.sql"), [order_id])

        conn.commit()
