from flask import Flask, request, jsonify
from database import init_mysql
import json
import bcrypt
from database import init_mysql, SQLContextManager

app = Flask(__name__)

with open("db_config.json") as f:
    app.config["db_config"] = json.load(f)

init_mysql(app)


@app.route("/login_external", methods=["POST"])
def login_external():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    with SQLContextManager() as cur:
        cur.execute(
            "SELECT ext_u_id, password_hash FROM external_user WHERE username=%s;",
            [username],
        )
        row = cur.fetchone()
        if row is None:
            return jsonify({"success": False})
        if bcrypt.checkpw(
            password.encode(encoding="utf-8"), row[1].encode(encoding="utf-8")
        ):
            return jsonify({"success": True, "u_id": row[0]})

    return jsonify({"success": False})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
