from database import SQLProvider, SQLContextManager
from dataclasses import dataclass
import secrets
from classes import User, UserRole

provider = SQLProvider("auth_blueprint/sql")


def generate_secure_id() -> str:
    return secrets.token_hex(32)


def check_session(session_id: str) -> User | None:
    """Проверить сессию. Если сессия валидна, возвращает пользователя. Если невалидна, возвращает None"""
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("check_session.sql"),
            [
                session_id,
            ],
        )
        row = cur.fetchone()
        if row is None:
            return None
        ret = User(
            u_id=row[0] if row[0] is not None else row[1],
            role=UserRole(row[2]),
            password_hash=row[3],
            username=row[4],
            real_name=row[5],
        )

        return ret


def delete_session(session_id: str):
    """Удалить сессию"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("delete_session.sql"), [session_id])


def delete_another_sessions(session_id: str):
    """Удалить все сессии этого пользователя, кроме одной (которая передана как session_id)"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("delete_another_sessions.sql"), [session_id])


def insert_session(user_id: int, is_internal: bool) -> str:
    """Добавить сессию для данного пользователя. Возвращает ID новой сессии"""
    session_id = generate_secure_id()
    with SQLContextManager() as cur:
        cur.execute(
            provider.get("insert_session.sql"),
            [
                session_id,
                user_id if not is_internal else None,
                user_id if is_internal else None,
            ],
        )
    return session_id


def set_password(u_id: str, new_password_hash: str):
    """Установить новый хеш пароля этому пользователю"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("set_password.sql"), [new_password_hash, u_id])


def get_internal_user(username: str) -> User | None:
    """Получить пользователя по username"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_internal_user.sql"), [username])
        row = cur.fetchone()
        if row is None:
            return None
        ret = User(
            u_id=row[0],
            role=row[1],
            password_hash=row[2],
            username=row[3],
            real_name=row[4],
        )
        return ret


def get_external_user(username: str) -> User | None:
    """Получить пользователя по username"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_external_user.sql"), [username])
        row = cur.fetchone()
        if row is None:
            return None
        ret = User(
            u_id=row[0],
            role=row[1],
            password_hash=row[2],
            username=row[3],
            real_name=row[4],
        )
        return ret
