import time, bcrypt, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User, Org

COOKIE = "rits_session"

def hash_pw(pw): return bcrypt.hashpw(pw.encode()[:72], bcrypt.gensalt()).decode()
def check_pw(pw, h):
    try: return bcrypt.checkpw(pw.encode()[:72], h.encode())
    except ValueError: return False

def make_token(u, days=7):
    return jwt.encode({"sub": str(u.id), "tv": u.token_version or 0, "exp": datetime.utcnow() + timedelta(days=days)}, settings.SECRET_KEY, algorithm="HS256")

def current_user(request: Request, db: Session = Depends(get_db)):
    tok = request.cookies.get(COOKIE)
    if not tok: raise HTTPException(401, "Not signed in")
    try: data = jwt.decode(tok, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(401, "Session expired")
    u = db.get(User, int(data["sub"]))
    if not u or not u.is_active or (u.token_version or 0) != data.get("tv", 0): raise HTTPException(401, "Session expired")
    return u

def current_org(u: User = Depends(current_user), db: Session = Depends(get_db)):
    if u.is_superadmin and not u.org_id: raise HTTPException(403, "Platform admin has no business workspace")
    org = db.get(Org, u.org_id)
    if not org: raise HTTPException(403, "Workspace not found")
    return org

def superadmin(u: User = Depends(current_user)):
    if not u.is_superadmin: raise HTTPException(403, "Platform admin only")
    return u

_hits = {}
def rate_limit(key, limit=8, window=900):
    now = time.time(); hits = [t for t in _hits.get(key, []) if now - t < window]
    if len(hits) >= limit: raise HTTPException(429, "Too many attempts. Try again in a few minutes.")
    hits.append(now); _hits[key] = hits
def rate_clear(key): _hits.pop(key, None)
