from flask import Blueprint, render_template, g

from auth_blueprint.auth import login_optional, login_required

order_blueprint = Blueprint("order", __name__)


@login_required(["customer"])
@order_blueprint.route("/my_orders")
def create_order():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Создание заказа", "link": "/my_orders", "icon": "bi-cart-plus"},
    ]
    return render_template("my_orders.html")
