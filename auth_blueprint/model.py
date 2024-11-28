from database import SQLProvider, SQLContextManager
from dataclasses import dataclass

import secrets

provider = SQLProvider("auth_blueprint/sql")


def generate_secure_id() -> str:
    return secrets.token_hex(32)


@dataclass
class User:
    u_id: int
    password_hash: str
    username: str
    real_name: str
    role: str


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
        print("ROW: ", row)
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


def delete_session(session_id: str):
    """Удалить сессию"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("delete_session.sql"), [session_id])


def delete_another_sessions(session_id: str):
    """Удалить все сессии этого пользователя, кроме одной (которая передана как session_id)"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("delete_another_sessions.sql"), [session_id])


def insert_session(u_id: str) -> str:
    print("INSERT SESSION")
    """Добавить сессию для данного пользователя. Возвращает ID новой сессии"""
    session_id = generate_secure_id()
    with SQLContextManager() as cur:
        cur.execute(provider.get("insert_session.sql"), [session_id, u_id])
    return session_id


def set_password(u_id: str, new_password_hash: str):
    """Установить новый хеш пароля этому пользователю"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("set_password.sql"), [new_password_hash, u_id])


def get_user(username: str) -> User | None:
    """Получить пользователя по username"""
    with SQLContextManager() as cur:
        cur.execute(provider.get("get_user.sql"), [username])
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
