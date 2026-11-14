"""Private deck storage and sessions, backed by PostgreSQL in production."""
from contextlib import contextmanager
import hashlib
import json
import os
import secrets
import time

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/deck-account")
USERS = ("SF", "HY", "Alex", "Jason")
COOKIE = "xlw_deck_session"
SESSION_SECONDS = 30 * 86400


def database_url(*, direct=False):
    if direct:
        url = os.environ.get("XLW_DECK_DATABASE_URL_UNPOOLED") or os.environ.get("DATABASE_URL_UNPOOLED")
        if url:
            return url
    return os.environ.get("XLW_DECK_DATABASE_URL") or os.environ.get("DATABASE_URL")


@contextmanager
def connection(*, direct=False):
    url = database_url(direct=direct)
    if not url:
        raise HTTPException(503, "雲端牌組尚未設定。")
    import psycopg
    try:
        with psycopg.connect(url, connect_timeout=8, prepare_threshold=None) as db:
            yield db
    except psycopg.Error as error:
        raise HTTPException(503, "雲端牌組暫時無法連線。") from error


def init(db):
    db.execute("SELECT pg_advisory_xact_lock(79204183)")
    db.execute("""CREATE TABLE IF NOT EXISTS xlw_deck_users (
        name TEXT PRIMARY KEY, decks TEXT NOT NULL DEFAULT '{}'
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS xlw_deck_sessions (
        token TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES xlw_deck_users(name),
        expires BIGINT NOT NULL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS xlw_deck_passwords (
        owner TEXT PRIMARY KEY REFERENCES xlw_deck_users(name),
        password_hash TEXT NOT NULL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS xlw_deck_login_limits (
        owner TEXT PRIMARY KEY, attempts INTEGER NOT NULL, retry_at BIGINT NOT NULL
    )""")
    db.commit()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def account(request):
    token = request.cookies.get(COOKIE, "")
    if not token:
        return None
    with connection() as db:
        init(db)
        row = db.execute("SELECT owner FROM xlw_deck_sessions WHERE token=%s AND expires>%s",
                         (digest(token), int(time.time()))).fetchone()
    return row[0] if row else None


def require_account(request):
    name = account(request)
    if not name:
        raise HTTPException(401, "請先登入個人牌組帳戶。")
    if request.method != "GET" and request.headers.get("X-Deck-Account") != name:
        raise HTTPException(409, "登入帳戶已切換，請重新整理牌組編輯器。")
    return name


class Login(BaseModel):
    name: str = Field(max_length=24)
    key: str = Field(max_length=128)


@router.get("")
def status(request: Request):
    return {"enabled": bool(database_url()), "name": account(request)}


def password_hash(password, salt=None):
    salt = salt if salt is not None else secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode(), salt=salt, n=65536, r=8, p=2, maxmem=96 * 1024**2)
    return salt.hex() + ":" + value.hex()


def password_matches(name, password, stored):
    if stored:
        salt = bytes.fromhex(stored.split(":", 1)[0])
        return secrets.compare_digest(password_hash(password, salt), stored)
    key = os.environ.get("XLW_DECK_KEY_" + name.upper(), "")
    return len(key) >= 32 and secrets.compare_digest(digest(key), digest(password))


def issue_cookie(request, response, token):
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
                        secure=bool(os.environ.get("RENDER")) or request.url.scheme == "https", samesite="strict")


@router.post("/login")
def login(data: Login, request: Request, response: Response):
    error = HTTPException(401, "帳戶或密碼不正確。")
    if data.name not in USERS:
        raise error
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with connection() as db:
        init(db)
        db.execute("INSERT INTO xlw_deck_login_limits VALUES (%s,0,0) ON CONFLICT DO NOTHING", (data.name,))
        attempts, retry_at = db.execute("SELECT attempts,retry_at FROM xlw_deck_login_limits WHERE owner=%s FOR UPDATE",
                                        (data.name,)).fetchone()
        if attempts >= 8 and now < retry_at:
            raise HTTPException(429, "登入嘗試過多，請約五分鐘後再試。", headers={"Retry-After": str(retry_at-now)})
        db.execute("INSERT INTO xlw_deck_users(name) VALUES (%s) ON CONFLICT DO NOTHING", (data.name,))
        db.execute("SELECT name FROM xlw_deck_users WHERE name=%s FOR UPDATE", (data.name,))
        stored = db.execute("SELECT password_hash FROM xlw_deck_passwords WHERE owner=%s", (data.name,)).fetchone()
        if not password_matches(data.name, data.key, stored[0] if stored else None):
            db.execute("UPDATE xlw_deck_login_limits SET attempts=%s,retry_at=%s WHERE owner=%s",
                       (attempts + 1 if now < retry_at else 1, now + 300, data.name))
            db.commit()
            raise error
        db.execute("DELETE FROM xlw_deck_login_limits WHERE owner=%s", (data.name,))
        db.execute("DELETE FROM xlw_deck_sessions WHERE expires<=%s OR token=%s",
                   (now, digest(request.cookies.get(COOKIE, ""))))
        db.execute("INSERT INTO xlw_deck_sessions VALUES (%s,%s,%s)", (digest(token), data.name, now + SESSION_SECONDS))
    issue_cookie(request, response, token)
    return {"name": data.name}


class PasswordChange(BaseModel):
    current: str = Field(max_length=128)
    new: str = Field(min_length=12, max_length=128)


@router.post("/password")
def change_password(data: PasswordChange, request: Request, response: Response):
    name = require_account(request)
    if request.headers.get("X-Deck-Account") != name:
        raise HTTPException(409, "登入帳戶已切換，請重新整理。")
    if data.current == data.new or not data.new.strip():
        raise HTTPException(400, "請設定不同的新密碼。")
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with connection() as db:
        db.execute("SELECT name FROM xlw_deck_users WHERE name=%s FOR UPDATE", (name,))
        session = db.execute("SELECT 1 FROM xlw_deck_sessions WHERE token=%s AND owner=%s AND expires>%s",
                             (digest(request.cookies.get(COOKIE, "")), name, now)).fetchone()
        if not session:
            raise HTTPException(401, "請重新登入。")
        stored = db.execute("SELECT password_hash FROM xlw_deck_passwords WHERE owner=%s", (name,)).fetchone()
        if not password_matches(name, data.current, stored[0] if stored else None):
            # End this session after a failed confirmation. Further attempts must go through login limits.
            db.execute("DELETE FROM xlw_deck_sessions WHERE token=%s", (digest(request.cookies.get(COOKIE, "")),))
            db.commit()
            raise HTTPException(401, "目前的密碼錯誤，請重新登入後再試。")
        db.execute("""INSERT INTO xlw_deck_passwords VALUES (%s,%s)
                      ON CONFLICT (owner) DO UPDATE SET password_hash=EXCLUDED.password_hash""",
                   (name, password_hash(data.new)))
        db.execute("DELETE FROM xlw_deck_sessions WHERE owner=%s", (name,))
        db.execute("INSERT INTO xlw_deck_sessions VALUES (%s,%s,%s)", (digest(token), name, now + SESSION_SECONDS))
    issue_cookie(request, response, token)
    return {"name": name}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with connection() as db:
            init(db)
            db.execute("DELETE FROM xlw_deck_sessions WHERE token=%s", (digest(token),))
    response.delete_cookie(COOKIE, httponly=True, samesite="strict")
    return {"name": None}


@contextmanager
def deck_store(name, *, write=False):
    with connection() as db:
        init(db)
        sql = "SELECT decks FROM xlw_deck_users WHERE name=%s"
        if write:
            sql += " FOR UPDATE"
        row = db.execute(sql, (name,)).fetchone()
        if not row:
            raise HTTPException(401, "請重新登入。")
        decks = json.loads(row[0])
        yield decks
        if write:
            db.execute("UPDATE xlw_deck_users SET decks=%s WHERE name=%s",
                       (json.dumps(decks, ensure_ascii=False), name))


if __name__ == "__main__":
    with connection(direct=True) as db:
        init(db)
    print("Deck PostgreSQL schema ready.")
