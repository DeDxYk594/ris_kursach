from flask import Blueprint, render_template, request, g
from . import model

goods_blueprint = Blueprint("goods", __name__)


def try_to_int(data: str | None) -> int | None:
    if data is None:
        return None
    try:
        return int(data)
    except Exception:
        return None


@goods_blueprint.route("/goods", methods=["GET"])
def search():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Поиск товара", "link": "/goods", "icon": "bi-search"},
    ]

    all_categories = model.get_all_categories()
    if request.args.get("search-filters"):
        goods = model.search_goods(
            request.args.get("good_name"),
            try_to_int(request.args.get("category_id")),
            try_to_int(request.args.get("min_price")),
            try_to_int(request.args.get("max_price")),
            try_to_int(request.args.get("page")),
        )
        print(goods)
        return render_template(
            "search.html",
            all_categories=all_categories,
            goods=goods,
        )

    return render_template("search.html", all_categories=all_categories)
