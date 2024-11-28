from flask import Blueprint, render_template

from auth_blueprint.auth import login_optional, login_required

report_blueprint = Blueprint("report", __name__)
