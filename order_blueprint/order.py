from flask import Blueprint, render_template, g, request, redirect
from auth_blueprint.auth import login_optional, login_required
from . import model

order_blueprint = Blueprint("order", __name__)


@order_blueprint.route("/my_orders", methods=["GET", "POST"])
@login_required(["customer"])
def create_order():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Мои заказы", "link": "/my_orders", "icon": "bi-cart-plus"},
    ]

    if request.method == "POST":
        model.create_order(g.user.u_id)
        return redirect("/my_orders")

    page = int(request.args.get("page", 1))
    orders = model.get_customer_orders(g.user.u_id, page)
    order_count = model.estimate_orders(g.user.u_id)

    pages = list(range(1, (order_count + 19) // 20 + 1))

    query_dict = request.args.to_dict()
    if query_dict.get("page"):
        del query_dict["page"]

    return render_template(
        "my_orders.html",
        orders=orders,
        pages=pages,
        page=page,
        query_dict=query_dict,
    )


@order_blueprint.route("/orders/delete/<int:order_id>", methods=["POST"])
@login_required(["customer"])
def cancel_order(order_id: int):
    is_success = model.annulate_order(g.user.u_id, order_id)

    # TODO навести суету

    return render_template(
        "success.html",
        is_success=True,
    )


@order_blueprint.route("/orders/add_to_order", methods=["POST"])
@login_required(["customer"])
def add_to_order():
    good = model.add_to_order(
        g.user.u_id,
        int(request.form["order_id"]),
        int(request.form["goodtype_id"]),
        int(request.form["quantity"]),
    )
    if isinstance(good, str):
        return render_template("success.html", is_success=False, message=good)
    return render_template(
        "add_checkout.html",
        good=good,
        order_id=request.form["order_id"],
        quantity=request.form["quantity"],
    )
