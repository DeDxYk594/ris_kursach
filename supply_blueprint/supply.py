from flask import Blueprint, render_template

from auth_blueprint.auth import login_optional, login_required

supply_blueprint = Blueprint("supply", __name__)
