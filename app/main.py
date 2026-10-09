import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import Base, engine, SessionLocal
from . import models
from .models import User
from .security import hash_pw
from .billing import seed_plans
from . import routes_auth, routes_data, routes_billing

log = logging.getLogger("ritsone")
STATIC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_plans(db)
        if settings.SUPERADMIN_EMAIL and settings.SUPERADMIN_PASSWORD and not db.query(User).filter_by(email=settings.SUPERADMIN_EMAIL).first():
            db.add(User(email=settings.SUPERADMIN_EMAIL, name="Platform Admin", password_hash=hash_pw(settings.SUPERADMIN_PASSWORD), role="owner", is_superadmin=True)); db.commit()
            log.info("Platform admin created: %s", settings.SUPERADMIN_EMAIL)
    finally: db.close()
    yield

app = FastAPI(title="RITS One", docs_url=None if settings.ENV == "production" else "/api/docs", redoc_url=None, openapi_url=None if settings.ENV == "production" else "/api/openapi.json", lifespan=lifespan)

@app.middleware("http")
async def guard(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH") and request.url.path.startswith("/api/") and request.url.path != "/api/billing/webhook":
        if request.headers.get("x-requested-with") != "RITS": return JSONResponse({"detail": "Bad request origin"}, status_code=403)
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff"); resp.headers.setdefault("X-Frame-Options", "DENY"); resp.headers.setdefault("Referrer-Policy", "same-origin")
    if not request.url.path.startswith("/api/docs"):
        resp.headers.setdefault("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self'; connect-src 'self'; frame-ancestors 'none'")
    if request.url.path.startswith("/api/"): resp.headers["Cache-Control"] = "no-store"
    return resp

app.include_router(routes_auth.router); app.include_router(routes_data.router); app.include_router(routes_billing.router)

@app.get("/health")
def health(): return {"ok": True}

@app.get("/sw.js")
def sw(): return FileResponse(os.path.join(STATIC, "sw.js"), media_type="application/javascript", headers={"Cache-Control": "no-cache"})

app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.get("/{path:path}")
def spa(path: str):
    if path.startswith("api/"): return JSONResponse({"detail": "Not found"}, status_code=404)
    return FileResponse(os.path.join(STATIC, "index.html"), headers={"Cache-Control": "no-cache"})
