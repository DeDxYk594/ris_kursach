from flask import Blueprint, render_template, g, request, redirect
from auth_blueprint.auth import login_optional, login_required
from . import model
from classes import UserRole

order_blueprint = Blueprint("order", __name__)


@order_blueprint.route("/my_orders", methods=["GET", "POST"])
@login_required([UserRole.CUSTOMER])
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
    order_count = model.estimate_customer_orders(g.user.u_id)

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


@order_blueprint.route("/active_orders", methods=["GET"])
@login_required([UserRole.SALES_MANAGER])
def active_orders():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Список активных заказов",
            "link": "/active_orders",
            "icon": "bi-cart-plus",
        },
    ]

    page = int(request.args.get("page", 1))
    orders = model.get_active_orders(page)
    order_count = model.estimate_active_orders()

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


@order_blueprint.route("/kassa", methods=["GET", "POST"])
@login_required([UserRole.SALES_MANAGER])
def kassa():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Касса",
            "link": "/kassa",
            "icon": "bi-safe",
        },
    ]
    order_id = request.form.get("order_id")
    if order_id is None:
        return render_template("kassa.html")

    order = model.get_unpaid_order(order_id)
    if order is None:
        return render_template(
            "success.html",
            is_success=False,
            message=f"Заказ с номером {order_id} не найден или имеет другой статус",
        )
    return render_template("kassa.html", order=order)


@order_blueprint.route("/orders/delete/<int:order_id>", methods=["POST"])
@login_required([UserRole.CUSTOMER, UserRole.SALES_MANAGER])
def cancel_order(order_id: int):
    if g.user.role == UserRole.SALES_MANAGER:
        is_success = model.annulate_order(order_id)
    else:
        is_success = model.annulate_my_order(g.user.u_id, order_id)

    return render_template(
        "success.html",
        is_success=is_success,
    )


@order_blueprint.route("/orders/add_to_order", methods=["POST"])
@login_required([UserRole.CUSTOMER])
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


@order_blueprint.route("/orders/pay_order", methods=["POST"])
@login_required([UserRole.SALES_MANAGER])
def pay_order():
    order = model.pay_order()

    if isinstance(order, str):
        return render_template("success.html", is_success=False, message=order)

    return render_template(
        "success.html", is_success=True, message=f"Заказ {order.order_id} оплачен!"
    )
