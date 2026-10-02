"""Email and Google sign-in, plus the signed-in user's favorites."""

from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password, verify_password
from app.auth.sessions import (
    clear_session_cookie,
    end_session,
    set_session_cookie,
    start_session,
    user_from_token,
    COOKIE,
)
from app.config import settings
from app.database import get_db
from app.models.account import User, UserFavorite
from app.models.catalog import Department, Program, University
from app.schemas.auth import AuthIn, FavoritesIn, FavoritesOut, MeOut, ProvidersOut, UserOut

router = APIRouter(tags=["auth"])

_EMAIL_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789._%+-@")


def _normalize_email(value: str) -> str:
    email = value.strip().lower()
    if email.count("@") != 1 or ".." in email or any(ch not in _EMAIL_CHARS for ch in email):
        raise HTTPException(status_code=422, detail="邮箱格式不正确")
    local, domain = email.split("@")
    if not local or "." not in domain:
        raise HTTPException(status_code=422, detail="邮箱格式不正确")
    return email


def _user_out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, name=user.name, google=bool(user.google_sub))


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    return user_from_token(db, request.cookies.get(COOKIE))


def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


def _https(request: Request) -> bool:
    proto = (request.headers.get("x-forwarded-proto") or request.url.scheme).split(",")[0].strip().lower()
    return proto == "https"


def _issue(response: Response, db: Session, user: User, request: Request) -> UserOut:
    set_session_cookie(response, start_session(db, user), secure=_https(request))
    db.commit()
    return _user_out(user)


@router.get("/auth/providers", response_model=ProvidersOut)
def providers() -> ProvidersOut:
    ready = bool(settings.google_client_id.strip() and settings.google_client_secret.strip())
    return ProvidersOut(google=ready)


@router.get("/auth/me", response_model=MeOut)
def me(user: User | None = Depends(current_user)) -> MeOut:
    return MeOut(user=_user_out(user) if user else None)


@router.post("/auth/register", response_model=UserOut)
def register(body: AuthIn, request: Request, response: Response, db: Session = Depends(get_db)) -> UserOut:
    email = _normalize_email(body.email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="这个邮箱已经注册")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.flush()
    return _issue(response, db, user, request)


@router.post("/auth/login", response_model=UserOut)
def login(body: AuthIn, request: Request, response: Response, db: Session = Depends(get_db)) -> UserOut:
    email = _normalize_email(body.email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.password_hash:
        if user is not None and user.google_sub and not user.password_hash:
            raise HTTPException(status_code=401, detail="这个邮箱是用谷歌注册的，请使用谷歌登录")
        raise HTTPException(status_code=401, detail="邮箱或密码不正确")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码不正确")
    return _issue(response, db, user, request)


@router.post("/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, bool]:
    end_session(db, request.cookies.get(COOKIE))
    clear_session_cookie(response, secure=_https(request))
    return {"ok": True}


def _google_redirect(request: Request) -> str:
    configured = settings.google_redirect_uri.strip()
    if configured:
        return configured
    return str(request.base_url).rstrip("/") + "/auth/google/callback"


@router.get("/auth/google/start")
def google_start(request: Request) -> Response:
    if not settings.google_client_id.strip() or not settings.google_client_secret.strip():
        return HTMLResponse(
            "谷歌登录还没有配置。请在后端环境变量里设置 GOOGLE_CLIENT_ID 和 GOOGLE_CLIENT_SECRET，"
            "并把回调地址登记为 /auth/google/callback。",
            status_code=503,
        )
    state = secrets.token_urlsafe(24)
    query = urllib.parse.urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": _google_redirect(request),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account",
        }
    )
    response = RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + query)
    response.set_cookie(
        "gradatlas_oauth_state",
        state,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=_https(request),
        path="/",
    )
    return response


def _google_post(url: str, data: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(request, timeout=20) as payload:
        return json.loads(payload.read().decode())


@router.get("/auth/google/callback")
def google_callback(
    request: Request,
    code: str = "",
    state: str = "",
    db: Session = Depends(get_db),
) -> Response:
    expected = request.cookies.get("gradatlas_oauth_state")
    if not code or not state or not expected or state != expected:
        raise HTTPException(status_code=400, detail="谷歌登录状态无效，请重新开始")
    try:
        token = _google_post(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": _google_redirect(request),
                "grant_type": "authorization_code",
            },
        )
        info_request = urllib.request.Request(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        with urllib.request.urlopen(info_request, timeout=20) as payload:
            info = json.loads(payload.read().decode())
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="谷歌登录没有完成") from exc
    email = str(info.get("email") or "").strip().lower()
    sub = str(info.get("sub") or "")
    if not email or not sub or not info.get("email_verified"):
        raise HTTPException(status_code=400, detail="谷歌账号没有提供已验证的邮箱")
    user = db.scalar(select(User).where(User.google_sub == sub))
    if user is None:
        user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, google_sub=sub, name=(info.get("name") or None))
        db.add(user)
        db.flush()
    else:
        if user.google_sub and user.google_sub != sub:
            raise HTTPException(status_code=409, detail="这个邮箱已经绑定了另一个谷歌账号")
        user.google_sub = sub
        if not user.name and info.get("name"):
            user.name = str(info["name"])[:255]
    response = RedirectResponse("/browse", status_code=303)
    set_session_cookie(response, start_session(db, user), secure=_https(request))
    response.delete_cookie("gradatlas_oauth_state", path="/", samesite="lax", secure=_https(request))
    db.commit()
    return response


def _program_for_key(db: Session, key: str) -> Program | None:
    country, separator, rest = key.partition("\0")
    name, separator2, slug = rest.partition("\0")
    if separator != "\0" or separator2 != "\0" or not country or not name or not slug or "\0" in slug:
        return None
    return db.scalar(
        select(Program)
        .join(Department, Program.department_id == Department.id)
        .join(University, Department.university_id == University.id)
        .where(
            University.country_code == country,
            University.name_en == name,
            Program.slug == slug,
            Program.is_active.is_(True),
        )
    )


def _favorite_keys(db: Session, user: User) -> list[str]:
    rows = db.execute(
        select(University.country_code, University.name_en, Program.slug)
        .join(Department, Department.university_id == University.id)
        .join(Program, Program.department_id == Department.id)
        .join(UserFavorite, UserFavorite.program_id == Program.id)
        .where(UserFavorite.user_id == user.id)
        .order_by(UserFavorite.id)
    ).all()
    return [f"{country}\0{name}\0{slug}" for country, name, slug in rows]


@router.get("/me/favorites", response_model=FavoritesOut)
def list_favorites(user: User = Depends(require_user), db: Session = Depends(get_db)) -> FavoritesOut:
    return FavoritesOut(keys=_favorite_keys(db, user))


@router.put("/me/favorites", response_model=FavoritesOut)
def replace_favorites(
    body: FavoritesIn,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> FavoritesOut:
    program_ids: list[int] = []
    seen: set[int] = set()
    for key in body.keys:
        program = _program_for_key(db, key)
        if program is None or program.id in seen:
            continue
        seen.add(program.id)
        program_ids.append(program.id)
    db.execute(delete(UserFavorite).where(UserFavorite.user_id == user.id))
    now = datetime.now(timezone.utc)
    db.add_all(
        UserFavorite(user_id=user.id, program_id=program_id, created_at=now) for program_id in program_ids
    )
    db.commit()
    return FavoritesOut(keys=_favorite_keys(db, user))
