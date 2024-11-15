from flask import Blueprint, render_template, request, make_response, redirect, url_for
import hashlib
from datetime import datetime, timedelta
from database import SQLContextManager, SQLProvider

provider = SQLProvider("sql")


authBlueprint = Blueprint("auth", __name__, template_folder="templates")


def hash_password(password):
    ret = hashlib.sha256(password.encode()).hexdigest()
    print(f"Hash for password '{password}': '{ret}'")
    return ret


def check_password(old_password_hash, password_candidate) -> bool:
    pass


@authBlueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        hashed_password = hash_password(password)

        with SQLContextManager() as cur:
            print(login, hashed_password)
            cur.execute(
                provider.get("get_user_by_creds.sql"),
                (login, hashed_password),
            )
            user = cur.fetchone()

            if user:
                session_id = str(
                    eval(
                        "0x"
                        + hashlib.sha256(
                            f"{login}{datetime.now()}".encode()
                        ).hexdigest()
                    )
                    % (1 << 31)
                )
                expiry_date = datetime.now() + timedelta(days=1)
                cur.execute(
                    provider.get("insert_session.sql"),
                    (
                        session_id,
                        expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
                        str(user[0]),
                    ),
                )

                resp = make_response(
                    redirect(url_for(request.args.get("next", "app.glavn_menu")))
                )
                resp.set_cookie(
                    "sessionId", session_id, samesite="Lax", httponly=True, secure=True
                )
                return resp
            else:
                return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@authBlueprint.route("/logout")
def logout():
    session_id = request.cookies.get("sessionId")
    if not session_id:
        return redirect(url_for("auth.login", next=url_for("glavn_menu")))

    with SQLContextManager() as cur:
        cur.execute(
            provider.get("delete_session.sql"),
            (str(session_id),),
        )

    resp = make_response(redirect(url_for("glavn_menu")))
    resp.delete_cookie("sessionId")
    return resp


def authenticate_user():
    session_id = get_session_id_from_request()

    if session_id is None:
        request.user_id = None
    else:
        with SQLContextManager() as cur:
            cur.execute(
                provider.get("get_user_id_from_session.sql"),
                (str(session_id),),
            )
            user = cur.fetchone()

            if not user:
                request.user_id = None
            else:
                request.user_id = user[0]


def get_session_id_from_request():
    return request.cookies.get("sessionId", None)
