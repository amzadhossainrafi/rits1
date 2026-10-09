import hashlib, json, re, secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User, Org, Plan, ResetToken, MODELS, next_code, Audit
from .schema import ROLES, ROLE_LABEL, PERM, can, public_entities, merged_settings, EDITABLE_LISTS, DEFAULT_SETTINGS
from .security import hash_pw, check_pw, make_token, current_user, current_org, rate_limit, rate_clear, COOKIE
from .billing import sub_state, plan_of, plan_dict, require_active, stripe_enabled
from .compute import org_settings
from .mailer import send_mail

router = APIRouter(prefix="/api")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _set_cookie(resp: Response, u):
    resp.set_cookie(COOKIE, make_token(u), httponly=True, samesite="lax", secure=settings.COOKIE_SECURE, max_age=7 * 86400, path="/")

def _pw_ok(pw):
    if not pw or len(pw) < 8: raise HTTPException(400, "Password must be at least 8 characters.")

@router.post("/auth/signup")
def signup(body: dict, resp: Response, request: Request, db: Session = Depends(get_db)):
    if not settings.ALLOW_SIGNUP: raise HTTPException(403, "Signups are closed.")
    rate_limit("signup:" + (request.client.host if request.client else "?"), 10, 3600)
    org_name, name, email, pw = [str(body.get(k) or "").strip() for k in ("org_name", "name", "email", "password")]
    email = email.lower()
    if not org_name or not name: raise HTTPException(400, "Business name and your name are required.")
    if not EMAIL.match(email): raise HTTPException(400, "Enter a valid email.")
    _pw_ok(pw)
    if db.query(User).filter_by(email=email).first(): raise HTTPException(409, "This email is already registered.")
    tpl = body.get("template") if body.get("template") in ("agency", "general") else "agency"
    org = Org(name=org_name, settings_json=json.dumps({"template": tpl}), plan_key="business", sub_status="trialing", trial_ends_at=datetime.utcnow() + timedelta(days=settings.TRIAL_DAYS))
    db.add(org); db.flush()
    code = next_code(db, org.id, "employee")
    db.add(MODELS["employee"](org_id=org.id, code=code, name=name, role="CEO", dept="Management", email=email, status="Active", etype="Full-time"))
    u = User(org_id=org.id, email=email, name=name, password_hash=hash_pw(pw), role="owner", employee_code=code, last_login=datetime.utcnow())
    db.add(u); db.commit()
    _set_cookie(resp, u)
    return {"ok": True}

@router.post("/auth/login")
def login(body: dict, resp: Response, request: Request, db: Session = Depends(get_db)):
    email = str(body.get("email") or "").strip().lower(); key = f"login:{email}:{request.client.host if request.client else '?'}"
    rate_limit(key, 8, 900)
    u = db.query(User).filter_by(email=email).first()
    if not u or not u.is_active or not check_pw(str(body.get("password") or ""), u.password_hash): raise HTTPException(401, "Wrong email or password.")
    rate_clear(key); u.last_login = datetime.utcnow(); db.commit(); _set_cookie(resp, u)
    return {"ok": True}

@router.post("/auth/logout")
def logout(resp: Response):
    resp.delete_cookie(COOKIE, path="/"); return {"ok": True}

@router.post("/auth/forgot")
def forgot(body: dict, bg: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    email = str(body.get("email") or "").strip().lower(); rate_limit("forgot:" + email, 5, 3600)
    u = db.query(User).filter_by(email=email).first()
    if u and u.is_active:
        raw = secrets.token_urlsafe(32)
        db.add(ResetToken(user_id=u.id, token_hash=hashlib.sha256(raw.encode()).hexdigest(), expires_at=datetime.utcnow() + timedelta(hours=2))); db.commit()
        bg.add_task(send_mail, u.email, "Reset your RITS One password", f"Open this link within 2 hours to set a new password:\n{settings.BASE_URL}/#/reset?token={raw}\n\nIf you did not ask for this, ignore this email.")
    return {"ok": True}

@router.post("/auth/reset")
def reset(body: dict, db: Session = Depends(get_db)):
    _pw_ok(body.get("password"))
    t = db.query(ResetToken).filter_by(token_hash=hashlib.sha256(str(body.get("token") or "").encode()).hexdigest()).first()
    if not t or t.used or t.expires_at < datetime.utcnow(): raise HTTPException(400, "This reset link is invalid or expired.")
    u = db.get(User, t.user_id); u.password_hash = hash_pw(body["password"]); u.token_version = (u.token_version or 0) + 1; t.used = True; db.commit()
    return {"ok": True}

@router.post("/auth/password")
def change_pw(body: dict, resp: Response, u: User = Depends(current_user), db: Session = Depends(get_db)):
    if not check_pw(str(body.get("old") or ""), u.password_hash): raise HTTPException(400, "Current password is wrong.")
    _pw_ok(body.get("new")); u.password_hash = hash_pw(body["new"]); u.token_version = (u.token_version or 0) + 1; db.commit(); _set_cookie(resp, u)
    return {"ok": True}

@router.get("/schema")
def schema_():
    return {"entities": public_entities(), "roles": [dict(key=r, label=ROLE_LABEL[r]) for r in ROLES], "perm": PERM}

@router.get("/me")
def me(u: User = Depends(current_user), db: Session = Depends(get_db)):
    out = {"user": dict(id=u.id, name=u.name, email=u.email, role=u.role, superadmin=bool(u.is_superadmin), employee_code=u.employee_code)}
    if u.is_superadmin and not u.org_id: return out
    org = db.get(Org, u.org_id); plan = plan_of(db, org)
    out["org"] = dict(name=org.name); out["subscription"] = dict(**sub_state(org), plan=plan_dict(plan), stripe=stripe_enabled(), plan_key=org.plan_key)
    out["perms"] = {r: dict(v=can(u.role, r, "v"), e=can(u.role, r, "e")) for r in PERM}
    s = org_settings(org); out["settings"] = s
    return out

# ---------------------------------------------------------------- workspace settings & team logins
@router.put("/org")
def update_org(body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Owner only")
    require_active(org)
    if body.get("name"): org.name = str(body["name"]).strip()[:160]
    s = json.loads(org.settings_json or "{}"); inc = body.get("settings") or {}
    for k in DEFAULT_SETTINGS:
        if k in inc and k != "template":
            if isinstance(DEFAULT_SETTINGS[k], (int, float)):
                try: s[k] = float(inc[k])
                except (TypeError, ValueError): raise HTTPException(400, f"{k} must be a number")
            else: s[k] = str(inc[k]).strip()[:60]
    if inc.get("rate") is not None and float(inc["rate"]) <= 0: raise HTTPException(400, "Rate must be above 0")
    if isinstance(inc.get("lists"), dict):
        s.setdefault("lists", {})
        for k, v in inc["lists"].items():
            if k in EDITABLE_LISTS and isinstance(v, list):
                clean = [str(x).strip()[:80] for x in v if str(x).strip()]
                if k in ("services", "channels", "contact") and not clean: raise HTTPException(400, f"{k} cannot be empty")
                s["lists"][k] = clean
    org.settings_json = json.dumps(s); db.commit()
    return {"ok": True, "settings": org_settings(org)}

def _user_json(x): return dict(id=x.id, name=x.name, email=x.email, role=x.role, active=x.is_active, employee_code=x.employee_code, last_login=x.last_login.isoformat() if x.last_login else None)

@router.get("/team/users")
def users_list(u: User = Depends(current_user), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Owner only")
    return {"users": [_user_json(x) for x in db.query(User).filter_by(org_id=u.org_id).order_by(User.id).all()]}

@router.post("/team/users")
def users_create(body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Owner only")
    require_active(org); plan = plan_of(db, org)
    if db.query(User).filter_by(org_id=org.id, is_active=True).count() >= plan.max_users:
        raise HTTPException(402, f"Your {plan.name} plan allows {plan.max_users} logins. Upgrade in Billing to add more.")
    email = str(body.get("email") or "").strip().lower(); name = str(body.get("name") or "").strip(); role = body.get("role")
    if not EMAIL.match(email) or not name: raise HTTPException(400, "Name and a valid email are required.")
    if role not in ROLES: raise HTTPException(400, "Choose a role.")
    _pw_ok(body.get("password"))
    if db.query(User).filter_by(email=email).first(): raise HTTPException(409, "This email is already registered.")
    ec = str(body.get("employee_code") or "")
    if ec and not db.query(MODELS["employee"]).filter_by(org_id=org.id, code=ec).first(): raise HTTPException(400, "Employee code not found.")
    x = User(org_id=org.id, email=email, name=name, password_hash=hash_pw(body["password"]), role=role, employee_code=ec); db.add(x); db.commit()
    return _user_json(x)

@router.put("/team/users/{uid}")
def users_update(uid: int, body: dict, u: User = Depends(current_user), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Owner only")
    x = db.get(User, uid)
    if not x or x.org_id != u.org_id: raise HTTPException(404, "User not found")
    if "role" in body:
        if body["role"] not in ROLES: raise HTTPException(400, "Bad role")
        if x.role == "owner" and body["role"] != "owner" and db.query(User).filter_by(org_id=u.org_id, role="owner", is_active=True).count() <= 1: raise HTTPException(400, "Keep at least one owner.")
        x.role = body["role"]
    if "active" in body:
        if x.id == u.id and not body["active"]: raise HTTPException(400, "You cannot deactivate yourself.")
        x.is_active = bool(body["active"]); x.token_version = (x.token_version or 0) + 1
    if body.get("name"): x.name = str(body["name"]).strip()
    if "employee_code" in body: x.employee_code = str(body["employee_code"] or "")
    if body.get("password"): _pw_ok(body["password"]); x.password_hash = hash_pw(body["password"]); x.token_version = (x.token_version or 0) + 1
    db.commit(); return _user_json(x)
