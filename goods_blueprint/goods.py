from flask import Blueprint, render_template, request, g
from auth_blueprint import login_optional
from auth_blueprint.auth import login_required
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
@login_optional
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
        return render_template(
            "search.html", all_categories=all_categories, goods=goods, result=True
        )

    return render_template("search.html", all_categories=all_categories)

@goods_blueprint.route("/goods/add_to_order", methods=["POST"])
@login_required(["customer"])
def add_to_order():
    return render_template("add_checkout.html")
