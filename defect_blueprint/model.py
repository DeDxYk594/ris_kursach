from flask import request
from database import SQLProvider, SQLTransactionContextManager

provider = SQLProvider("defect_blueprint/sql")


def writeoff():
    goodtype_id = int(request.form["goodtype_id"])
    quantity = int(request.form["quantity"])
    reason = request.form["reason"]
    with SQLTransactionContextManager() as (conn, cur):
        cur.execute(
            provider.get("create_defect.sql"),
            [goodtype_id, quantity, reason, quantity, goodtype_id],
        )
        cur.execute(provider.get("remove_from_good.sql"), [quantity, goodtype_id])
        conn.commit()
        return True
