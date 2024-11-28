from flask import Blueprint, render_template, g

from auth_blueprint.auth import login_optional, login_required

main_menu_blueprint = Blueprint("main_menu", __name__)


@main_menu_blueprint.route("/")
@login_optional
def main_menu():
    breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
    ]

    return render_template("main_menu.html", breadcrumbs=breadcrumbs)


@main_menu_blueprint.route("/personal")
@login_required(["customer"])
def personal():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {"text": "Личный кабинет", "link": "/personal", "icon": "bi-person"},
    ]

    return render_template("personal.html")
