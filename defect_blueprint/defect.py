from flask import Blueprint, request, render_template, g
from auth_blueprint import login_required
from classes import UserRole

from . import model

defect_blueprint = Blueprint("defect", __name__)


@defect_blueprint.route("/defect", methods=["GET", "POST"])
@login_required([UserRole.SUPPLY_MANAGER])
def writeoff():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Списание товара",
            "link": "/defect",
            "icon": "bi-trash",
        },
    ]
    if request.method == "GET":
        return render_template("defect.html")

    model.writeoff()
    return render_template(
        "success.html", is_success=True, message="Успешно списан товар"
    )
