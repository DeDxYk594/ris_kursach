from database import SQLProvider, SQLContextManager
from dataclasses import dataclass
import math
from flask import g

provider = SQLProvider("goods_blueprint/sql")


def try_to_int(data: str | None, default: int = 0) -> int:
    if data is None:
        return default
    try:
        return int(data)
    except Exception:
        return default


def to_int(data: str | None, default: int | None = None) -> int | None:
    if data is None:
        return default
    try:
        return int(data)
    except Exception:
        return default


def to_str(data: str | None):
    return data if data is not None else ""


@dataclass
class Category:
    category_id: int
    category_name: str
    goodtypes_count: int


@dataclass
class GoodType:
    goodtype_id: int
    article: int
    name: str
    category_id: int
    measure_unit: str
    available_units: int
    sell_price: int


@dataclass
class SearchResults:
    page: int
    pages: list[int]
    total_goods: int
    goods: list[GoodType]

    request_min_price: str
    request_max_price: str
    request_name: str
    request_cat: int


def get_all_categories() -> list[Category]:
    ret: list[Category] = []
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_all_categories.sql"))
        rows = cur.fetchall()
        for row in rows:
            ret.append(Category(row[0], row[1], row[2]))

    return ret


def search_goods(
    request_name: str | None,
    category_id: str | None,
    min_price: str | None,
    max_price: str | None,
    page: str | None,
) -> SearchResults:
    if page is None:
        page = "1"
    if request_name is None:
        request_name = ""
    ret = SearchResults(
        page=try_to_int(page, 1),
        pages=[],
        total_goods=0,
        goods=[],
        request_max_price=to_str(max_price),
        request_min_price=to_str(min_price),
        request_cat=try_to_int(category_id),
        request_name=request_name,
    )
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("estimate_search_result.sql"),
            [
                "%" + request_name.lower() + "%",
                to_int(category_id),
                to_int(category_id),
                to_int(max_price),
                to_int(max_price),
                to_int(min_price),
                to_int(min_price),
            ],
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError()
        ret.total_goods = row[0]
        ret.pages = list(range(1, 1 + math.ceil(ret.total_goods / 20)))
        cur.execute(
            provider.get("search_goods.sql"),
            [
                "%" + request_name.lower() + "%",
                to_int(category_id),
                to_int(category_id),
                to_int(max_price),
                to_int(max_price),
                to_int(min_price),
                to_int(min_price),
                (try_to_int(page, 1) - 1) * 20,
            ],
        )
        rows = cur.fetchall()
        for row in rows:
            ret.goods.append(GoodType(*row))
    return ret


def get_customer_orders() -> list[int]:
    user = g.get("user", None)
    if user is None:
        return []
    if user.role != "customer":
        return []

    with SQLContextManager() as cur:
        cur.execute(provider.get("get_orders_for_customer.sql"), [user.u_id])
        rows = cur.fetchall()
        if rows is None:
            return []
        ret = []
        for row in rows:
            ret.append(row[0])
        return ret
