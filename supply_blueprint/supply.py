from flask import Blueprint, render_template, g, request
from classes import UserRole
from auth_blueprint.auth import login_required
from . import model

supply_blueprint = Blueprint("supply", __name__)


@supply_blueprint.route("/add_goodtype", methods=["GET", "POST"])
@login_required([UserRole.SUPPLY_MANAGER])
def add_goodtype():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Добавить номенклатуру",
            "link": "/add_goodtype",
            "icon": "bi-node-plus",
        },
    ]
    g.all_categories = model.get_all_categories()
    if request.method == "GET":
        return render_template("new_goodtype.html")

    model.add_goodtype()

    return render_template(
        "success.html", is_success=True, message="SKU успешно добавлен!"
    )


@supply_blueprint.route("/add_batch", methods=["GET", "POST"])
@login_required([UserRole.SUPPLY_MANAGER])
def add_batch():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Добавить поступление",
            "link": "/add_goodtype",
            "icon": "bi-bag-plus",
        },
    ]
    if request.method == "GET":
        return render_template("add_batch.html")

    model.add_batch()

    return render_template(
        "success.html", is_success=True, message="SKU успешно добавлен!"
    )
