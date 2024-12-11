from classes import Category, GoodType, UserRole
from database import SQLProvider, SQLContextManager, SQLTransactionContextManager
from dataclasses import dataclass
import math
from flask import g, request

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


def search_goods() -> SearchResults:
    request_name = request.args.get("good_name")
    category_id = request.args.get("category_id")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    page = request.args.get("page")
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
