from classes import GoodType, Order, OrderLine
from database import SQLContextManager, SQLProvider, SQLTransactionContextManager

provider = SQLProvider("order_blueprint/sql")


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
                ord = Order(order_id, row[2], row[1], [], 0)
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


def create_order(ext_u_id: int):
    with SQLContextManager() as cur:
        cur.execute(provider.get("create_order.sql"), [ext_u_id])


def estimate_orders(ext_u_id: int) -> int:
    with SQLContextManager() as cur:
        cur.execute(provider.get("estimate_orders.sql"), [ext_u_id])
        row = cur.fetchone()
        if row is None:
            raise ValueError("Error sql query")
        return row[0]


def annulate_order(ext_u_id: int, order_id: int) -> bool:
    with SQLContextManager() as cur:
        cur.execute(provider.get("annulate_order.sql"), [order_id, ext_u_id])
        row = cur.fetchone()
        if row is None:
            return False

    return True


def add_to_order(
    ext_u_id: int, order_id: int, goodtype_id: int, quantity: int
) -> GoodType | str:
    """Добавляет товар в заказ. Возвращает строку с сообщением об ошибке в случае ошибки"""
    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(provider.get("get_goodtype_by_id.sql"), [goodtype_id])
        row = cur.fetchone()
        if row is None:
            conn.rollback()
            return "Товар не найден"
        gt = GoodType(*row)

        if gt.available_units < quantity:
            conn.rollback()
            return "Попытка заказать товаров больше, чем доступно к заказу"

        cur.execute(
            provider.get("book_good.sql"),
            [quantity, quantity, gt.goodtype_id],
        )
        cur.execute(provider.get("check_order.sql"), [ext_u_id, order_id])
        row = cur.fetchone()
        if row is None:
            conn.rollback()
            return "Заказ имеет неподходящий статус или вы не имеете прав на добавление в этот заказ"

        cur.execute(provider.get("add_to_order.sql"), [order_id, goodtype_id, quantity])
        conn.commit()
        return gt
