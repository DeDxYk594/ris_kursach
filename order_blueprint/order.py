from flask import Blueprint, render_template

from auth_blueprint.auth import login_optional, login_required

order_blueprint = Blueprint("order", __name__)
