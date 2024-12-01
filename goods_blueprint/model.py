from database import SQLProvider, SQLContextManager
from dataclasses import dataclass

provider = SQLProvider("goods_blueprint/sql")


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


def get_all_categories() -> list[Category]:
    ret: list[Category] = []
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_all_categories.sql"))
        rows = cur.fetchall()
        for row in rows:
            ret.append(Category(row[0], row[1], row[2]))

    return ret


def search_goods(
    like_filter: str,
    category_id: int | None,
    min_price: int | None,
    max_price: int | None,
    page: int | None,
) -> list[GoodType]:
    if page is None:
        page = 1
    ret: list[GoodType] = []
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("search_goods.sql"),
            [
                "%" + like_filter.lower() + "%",
                category_id,
                category_id,
                max_price,
                max_price,
                min_price,
                min_price,
                (page - 1) * 20,
            ],
        )
        rows = cur.fetchall()
        for row in rows:
            ret.append(GoodType(*row))
    return ret
