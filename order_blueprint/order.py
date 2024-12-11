from flask import Blueprint, render_template, g, request, redirect, session
from auth_blueprint.auth import login_optional, login_required
from . import model
from classes import UserRole

order_blueprint = Blueprint("order", __name__)


@order_blueprint.route("/my_orders", methods=["GET"])
@login_required([UserRole.CUSTOMER])
def get_my_orders():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Мои заказы", "link": "/my_orders", "icon": "bi-cart-plus"},
    ]

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
@login_required([UserRole.SALES_MANAGER, UserRole.WORKER])
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
    if g.user.role == UserRole.WORKER:
        orders = model.get_active_orders(page)
        order_count = model.estimate_active_orders()
    elif g.user.role == UserRole.SALES_MANAGER:
        orders = model.get_paid_orders(page)
        order_count = model.estimate_paid_orders()

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
    is_success = model.annulate_order(order_id)

    return render_template(
        "success.html",
        is_success=is_success,
    )


@order_blueprint.route("/orders/ship/<int:order_id>", methods=["POST"])
@login_required([UserRole.WORKER])
def ship_order(order_id: int):
    model.ship_order(order_id)

    return render_template(
        "success.html",
        is_success=True,
    )


@order_blueprint.route("/orders/add_to_cart", methods=["POST"])
@login_required([UserRole.CUSTOMER])
def add_to_cart():
    good = model.get_goodtype_by_id(int(request.form["goodtype_id"]))
    if good is None:
        return render_template(
            "success.html", is_success=False, message="Товар с таким ID не найден"
        )
    cart = session.get("cart", [])
    try:
        cart[next(idx for (idx, i) in enumerate(cart) if i[0] == good.goodtype_id)][
            3
        ] += int(request.form["quantity"])
    except StopIteration:
        cart.append(
            [
                good.goodtype_id,
                good.name,
                good.article,
                int(request.form["quantity"]),
                good.sell_price,
                good.measure_unit,
            ]
        )
    session["cart"] = cart
    return render_template(
        "add_checkout.html",
        good=good,
        quantity=request.form["quantity"],
    )


@order_blueprint.route("/orders/clear_cart", methods=["POST"])
@login_required([UserRole.CUSTOMER])
def clear_cart():
    session["cart"] = []
    return render_template(
        "success.html", is_success=True, message="Корзина теперь пустая"
    )


@order_blueprint.route("/orders/create_order", methods=["POST"])
@login_required([UserRole.CUSTOMER])
def create_order():
    try:
        is_success, order_id = model.create_order()

        if is_success:
            return render_template(
                "success.html", is_success=True, message=f"Заказ #{order_id} создан"
            )
        return render_template(
            "success.html",
            is_success=False,
            message="Заказ не создан, произошла ошибка",
        )
    except Exception as e:
        print(e)
        return render_template(
            "success.html",
            is_success=False,
            message="Заказ не создан, неизвестная ошибка",
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
