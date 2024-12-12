from classes import ReportType
from database import SQLContextManager
from flask import request


def get_report(typ: ReportType) -> tuple | None:
    params = []
    for i in range(len(typ.params)):
        params.append(int(request.form[f"param{i}"]))
    with SQLContextManager() as cur:
        cur.execute(typ.get_sql, params)
        row = cur.fetchone()
        return row


def create_report(typ: ReportType) -> str:
    params = []
    for i in range(len(typ.params)):
        params.append(str(int(request.form[f"param{i}"])))
    with SQLContextManager() as cur:
        cur.execute("SET @error_msg = '';")
        cur.execute(f"CALL {typ.procedure_name}({', '.join(params)}, @error_msg);")
        cur.execute("SELECT @error_msg;")
        row = cur.fetchone()
        return row[0]
