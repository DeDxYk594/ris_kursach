from flask import Blueprint, render_template, g
from classes import UserRole
from auth_blueprint.auth import login_optional, login_required
from . import model

main_menu_blueprint = Blueprint("main_menu", __name__)


@main_menu_blueprint.route("/")
@login_optional
def main_menu():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
    ]

    return render_template("main_menu.html")


@main_menu_blueprint.route("/personal")
@login_required([UserRole.CUSTOMER])
def personal():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Личный кабинет", "link": "/personal", "icon": "bi-person"},
    ]

    data = model.get_personal()

    return render_template("personal.html", data=data)
