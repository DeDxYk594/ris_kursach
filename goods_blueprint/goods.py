from flask import Blueprint, render_template, request, g
from auth_blueprint import login_optional
from auth_blueprint.auth import login_required
from . import model

goods_blueprint = Blueprint("goods", __name__)


@goods_blueprint.route("/goods", methods=["GET"])
@login_optional
def search():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Поиск товара", "link": "/goods", "icon": "bi-search"},
    ]

    all_categories = model.get_all_categories()
    if request.args.get("search-filters"):
        search_result = model.search_goods()
        query_dict = request.args.to_dict()
        if query_dict.get("page"):
            del query_dict["page"]

        return render_template(
            "search.html",
            all_categories=all_categories,
            search_result=search_result,
            result=True,
            query_dict=query_dict,
        )

    return render_template("search.html", all_categories=all_categories)
