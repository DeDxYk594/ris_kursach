from flask import Blueprint, render_template
from auth_blueprint.auth import login_optional, login_required
import json
from classes import ReportType, UserRole

report_blueprint = Blueprint("report", __name__)

with open("report_config.json", "r", encoding="utf-8") as f:
    _config = json.load(f)
    report_types = [
        ReportType(
            idx,
            i["name"],
            [(j["name"], j["type"]) for j in i["params"]],
            i["values"],
            i["procedure_name"],
            i["get_sql"],
        )
        for idx, i in enumerate(_config)
    ]


@report_blueprint.route("/report_list")
@login_required([UserRole.SUPPLY_MANAGER, UserRole.BOSS_OF_THE_GYM])
def get_report_types():
    return render_template("report_list.html", report_types=report_types)
