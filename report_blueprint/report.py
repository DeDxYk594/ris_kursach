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


@report_blueprint.route("/create_report")
@login_required([UserRole.SALES_MANAGER])
def create_reports():
    return render_template("report_list.html", report_types=report_types, create=True)


@report_blueprint.route("/create_report/<int:report_id>")
@login_required([UserRole.SALES_MANAGER])
def create_report(report_id: int):
    return render_template("create_report.html", report_type=report_types[report_id])


@report_blueprint.route("/view_report")
@login_required([UserRole.SUPPLY_MANAGER, UserRole.SALES_MANAGER])
def view_reports():
    return render_template("report_list.html", report_types=report_types, create=False)


@report_blueprint.route("/view_report/<int:report_id>")
@login_required([UserRole.SALES_MANAGER, UserRole.SALES_MANAGER])
def view_report(report_id: int):
    return render_template("view_report.html", report_type=report_types[report_id])
