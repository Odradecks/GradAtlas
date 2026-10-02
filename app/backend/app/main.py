from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.programs import router as programs_router
from app.database import check_db_connection

app = FastAPI(
    title="GradAtlas API",
    version="0.1.0",
)
app.include_router(programs_router)
app.include_router(auth_router)

_STATIC = Path(__file__).resolve().parent / "static"
_BROWSE_PAGE = _STATIC / "browse.html"
_CATALOG_PAGE = _STATIC / "catalog.html"
_INTAKE_PAGE = _STATIC / "intake.html"
_ACCOUNT_PAGE = _STATIC / "account.html"
_PRIVACY_PAGE = _STATIC / "privacy.html"
_TERMS_PAGE = _STATIC / "terms.html"
app.mount("/static", StaticFiles(directory=_STATIC), name="static")


@app.get("/")
def root():
    return RedirectResponse("/browse", status_code=302)


def _page(path: Path) -> HTMLResponse:
    return HTMLResponse(
        path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-store"},
    )


@app.get("/login", response_class=HTMLResponse)
@app.get("/register", response_class=HTMLResponse)
def account_page():
    return _page(_ACCOUNT_PAGE)


@app.get("/privacy", response_class=HTMLResponse)
def privacy_page():
    return _page(_PRIVACY_PAGE)


@app.get("/terms", response_class=HTMLResponse)
def terms_page():
    return _page(_TERMS_PAGE)


@app.get("/browse", response_class=HTMLResponse)
def browse():
    return _page(_BROWSE_PAGE)


@app.get("/browse/catalog", response_class=HTMLResponse)
def browse_catalog():
    return _page(_CATALOG_PAGE)


@app.get("/browse/intakes/{intake_id}", response_class=HTMLResponse)
def browse_intake(intake_id: int):
    return _page(_INTAKE_PAGE)


@app.get("/health")
def health():  # Check the health of the application and the database at the same time
    db_ok = False
    try:
        db_ok = check_db_connection()
    except Exception:
        db_ok = False

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "db": "ok" if db_ok else "error",
    }
