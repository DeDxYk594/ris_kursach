from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    g,
    abort,
)
import hashlib
from datetime import datetime, timedelta
from database import SQLContextManager, SQLProvider
import bcrypt
from typing import Callable

from . import model
from .model import User

authBlueprint = Blueprint("auth", __name__, template_folder="templates")


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(old_password_hash: str, password_candidate: str) -> bool:
    return bcrypt.checkpw(
        password_candidate.encode(), hashed_password=old_password_hash.encode()
    )


@authBlueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)

        print(username, hashed_password)
        user = model.get_user(login)
        if user is None:
            return

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


def authenticate_user() -> User | None:
    got_user = g.get("user", None)
    if got_user == 0:
        return None
    if got_user is None:
        session_id = get_session_id_from_request()
        user = model.check_session(session_id)
        if user is None:
            g.user = 0
        else:
            g.user = user
        return user
    return g.user


def get_session_id_from_request():
    return request.cookies.get("sessionId", None)


def login_required(allowed_roles: list[str] = []) -> Callable:
    """
    Декоратор для проверки роли пользователя.
    Наследуется от `login_required` и дополнительно проверяет роль.
    Добавляет `g.user` и `g.role` в контекст запроса.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Используем login_required для проверки аутентификации
            session_id = get_session_id_from_request()
            if not session_id:
                abort(redirect("/login"))

            user = authenticate_user()
            if user is None:
                abort(redirect("/login"))

            if len(allowed_roles) != 0 and (user.role not in allowed_roles):
                abort(redirect("/no_access"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
