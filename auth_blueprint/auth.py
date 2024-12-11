from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    g,
    session,
    abort,
)
import bcrypt
from typing import Callable
from . import model
from classes import User, UserRole
import json
import requests

SESSION_COOKIE_NAME = "session_id"

auth_blueprint = Blueprint("auth", __name__, template_folder="templates")


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(old_password_hash: str, password_candidate: str) -> bool:
    return bcrypt.checkpw(
        password_candidate.encode(), hashed_password=old_password_hash.encode()
    )


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        account_type = request.form["account_type"]
        if account_type not in ["internal", "external"]:
            abort(400)

        if account_type == "internal":
            user = model.get_internal_user(username)
            if user is None:
                return render_template(
                    "login.html",
                    errors={"username": "Такого пользователя не существует"},
                    username=username,
                )
            if not check_password(user.password_hash, password):
                return render_template(
                    "login.html",
                    errors={"password": "Неправильный пароль"},
                    username=username,
                )
            user_id = user.u_id
            is_internal = True
        else:
            user = requests.post(
                "http://127.0.0.1:5002/login_external",
                data=json.dumps({"username": username, "password": password}),
                headers={"Content-Type": "application/json"},
            ).json()
            if not user["success"]:
                return render_template(
                    "login.html",
                    errors={"username": "Неправильный логин или пароль"},
                    username=username,
                )
            user_id = user["u_id"]
            is_internal = False

        session_id = model.insert_session(user_id, is_internal)
        resp = make_response(redirect(request.args.get("next", "/")))
        resp.set_cookie(SESSION_COOKIE_NAME, session_id)
        return resp
    return render_template("login.html", errors={})


@auth_blueprint.route("/logout")
def logout():
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return redirect(url_for("auth.login", next="main_menu"))

    model.delete_session(session_id)

    resp = make_response(redirect(request.args.get("next", "/login")))
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp


def authenticate_user() -> User | None:
    got_user = g.get("user", 0)
    if got_user is None:
        return None
    if got_user == 0:
        session_id = get_session_id_from_request()
        user = model.check_session(session_id)
        if user is None:
            g.user = None
            return None
        else:
            g.user = user
        if g.user.role == UserRole.CUSTOMER:
            g.cart = session.get("cart", [])
            g.cart_sum = sum([i[4] * i[3] for i in g.cart])
            g.cart_quantity = len(g.cart)
        return user
    return g.user


def get_session_id_from_request():
    return request.cookies.get(SESSION_COOKIE_NAME, None)


def login_required(allowed_roles: list[UserRole] = []) -> Callable:
    """
    Декоратор для проверки роли пользователя.
    Проверяет логин и дополнительно проверяет роль, если указана.
    Добавляет `g.user` в контекст запроса.
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
                return render_template(
                    "success.html",
                    is_success=False,
                    message=f"Вы не авторизованы на это действие. На него авторизованы только: {', '.join([
                        UserRole.to_name(r) for r in allowed_roles
                    ])}",
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def login_optional(f: Callable) -> Callable:
    """
    Декоратор для получения данных о пользователе.
    Нужен, чтобы в навбаре отображалось имя пользователя.
    Если пользователь не вошёл, `g.user` устанавливается в None
    """

    def wrapped(*args, **kwargs) -> Callable:
        authenticate_user()
        return f(*args, **kwargs)

    return wrapped
