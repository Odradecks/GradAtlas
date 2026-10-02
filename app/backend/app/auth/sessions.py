import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import User, UserSession

COOKIE = "gradatlas_session"
_DAYS = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def start_session(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=_hash_token(token),
            expires_at=now + timedelta(days=_DAYS),
            created_at=now,
        )
    )
    db.flush()
    return token


def user_from_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    row = db.scalar(select(UserSession).where(UserSession.token_hash == _hash_token(token)))
    if row is None:
        return None
    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires <= datetime.now(timezone.utc):
        db.delete(row)
        db.commit()
        return None
    return db.get(User, row.user_id)


def end_session(db: Session, token: str | None) -> None:
    if not token:
        return
    row = db.scalar(select(UserSession).where(UserSession.token_hash == _hash_token(token)))
    if row is not None:
        db.delete(row)
        db.commit()


def set_session_cookie(response: Response, token: str, *, secure: bool = False) -> None:
    response.set_cookie(
        COOKIE,
        token,
        max_age=_DAYS * 24 * 3600,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def clear_session_cookie(response: Response, *, secure: bool = False) -> None:
    response.delete_cookie(COOKIE, path="/", samesite="lax", secure=secure)
