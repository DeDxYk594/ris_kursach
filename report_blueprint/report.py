from flask import Blueprint, render_template, request, g
from auth_blueprint.auth import login_optional, login_required
import json
from classes import ReportType, UserRole
from . import model

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
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Создание отчётов",
            "link": "/create_report",
            "icon": "bi-window-plus",
        },
    ]
    return render_template("report_list.html", report_types=report_types, create=True)


@report_blueprint.route("/create_report/<int:report_id>", methods=["GET", "POST"])
@login_required([UserRole.SALES_MANAGER])
def create_report(report_id: int):
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Создание отчётов",
            "link": "/create_report",
            "icon": "bi-window-plus",
        },
        {
            "text": f"Создание отчёта: {report_types[report_id].name}",
            "link": f"/create_report/{report_id}",
            "icon": "bi-window-plus",
        },
    ]
    if request.method == "GET":
        return render_template(
            "create_report.html", report_type=report_types[report_id]
        )
    err = model.create_report(report_types[report_id])
    if err == "":
        return render_template(
            "success.html", is_success=True, message="Успешно создан отчёт!"
        )
    return render_template("success.html", is_success=False, message=err)


@report_blueprint.route("/view_report")
@login_required([UserRole.SUPPLY_MANAGER, UserRole.SALES_MANAGER])
def view_reports():
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Просмотр отчётов",
            "link": "/kassa",
            "icon": "bi-card-checklist",
        },
    ]
    return render_template("report_list.html", report_types=report_types, create=False)


@report_blueprint.route("/view_report/<int:report_id>", methods=["POST", "GET"])
@login_required([UserRole.SUPPLY_MANAGER, UserRole.SALES_MANAGER])
def view_report(report_id: int):
    g.breadcrumbs = [
        {"text": "Главное меню", "link": "/", "icon": "bi-house"},
        {
            "text": "Просмотр отчётов",
            "link": "/view_report",
            "icon": "bi-card-checklist",
        },
        {
            "text": f"Просмотр отчёта: {report_types[report_id].name}",
            "link": f"/view_report/{report_id}",
            "icon": "bi-card-checklist",
        },
    ]
    if request.method == "GET":
        return render_template("view_report.html", report_type=report_types[report_id])

    report = model.get_report(report_types[report_id])
    if report is None:
        return render_template(
            "success.html", is_success=False, message="Отчёт не найден"
        )
    return render_template(
        "view_report.html", report_type=report_types[report_id], report=report
    )
