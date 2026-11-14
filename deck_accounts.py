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


@contextmanager
def connection():
    url = os.environ.get("XLW_DECK_DATABASE_URL")
    if not url:
        raise HTTPException(503, "雲端牌組尚未設定。")
    import psycopg
    try:
        with psycopg.connect(url, connect_timeout=8) as db:
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
    return {"enabled": bool(os.environ.get("XLW_DECK_DATABASE_URL")), "name": account(request)}


@router.post("/login")
def login(data: Login, request: Request, response: Response):
    expected = os.environ.get("XLW_DECK_KEY_" + data.name.upper(), "") if data.name in USERS else ""
    # Provision independent cryptographically random access keys (32+ characters).
    if len(expected) < 32 or not secrets.compare_digest(digest(expected), digest(data.key)):
        raise HTTPException(401, "帳戶或登入金鑰不正確。")
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with connection() as db:
        init(db)
        db.execute("INSERT INTO xlw_deck_users(name) VALUES (%s) ON CONFLICT DO NOTHING", (data.name,))
        db.execute("DELETE FROM xlw_deck_sessions WHERE expires<=%s OR token=%s",
                   (now, digest(request.cookies.get(COOKIE, ""))))
        db.execute("INSERT INTO xlw_deck_sessions VALUES (%s,%s,%s)", (digest(token), data.name, now + SESSION_SECONDS))
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
                        secure=bool(os.environ.get("RENDER")) or request.url.scheme == "https", samesite="strict")
    return {"name": data.name}


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
