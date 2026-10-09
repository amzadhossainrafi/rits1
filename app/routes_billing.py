from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User, Org, Plan, PaymentRequest
from .security import current_user, current_org, superadmin, hash_pw
from .billing import sub_state, plan_dict, plan_of, activate, stripe_enabled, stripe_checkout, stripe_event, require_active

router = APIRouter(prefix="/api")

def _req(x):
    return dict(id=x.id, plan_key=x.plan_key, months=x.months, amount=x.amount, currency=x.currency, method=x.method, txn_id=x.txn_id, status=x.status, created_at=x.created_at.isoformat(timespec="minutes"), note=x.note)

@router.get("/billing")
def billing(u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    plans = db.query(Plan).filter_by(active=True).order_by(Plan.sort).all()
    reqs = db.query(PaymentRequest).filter_by(org_id=org.id).order_by(PaymentRequest.id.desc()).limit(20).all()
    return dict(plans=[plan_dict(p) for p in plans], state=sub_state(org), plan_key=org.plan_key, stripe=stripe_enabled(), instructions=settings.PAY_INSTRUCTIONS, requests=[_req(r) for r in reqs],
                users=db.query(User).filter_by(org_id=org.id, is_active=True).count())

@router.post("/billing/request")
def pay_request(body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Only the owner can pay for the subscription.")
    p = db.query(Plan).filter_by(key=body.get("plan_key"), active=True).first()
    months = int(body.get("months") or 1)
    if not p or months not in (1, 3, 6, 12): raise HTTPException(400, "Choose a plan and a period.")
    txn = str(body.get("txn_id") or "").strip()
    if len(txn) < 4: raise HTTPException(400, "Enter the transaction ID from your payment.")
    if db.query(PaymentRequest).filter_by(txn_id=txn).first(): raise HTTPException(409, "This transaction ID was already submitted.")
    amount = p.price_yearly if (months == 12 and p.price_yearly) else p.price_monthly * months
    db.add(PaymentRequest(org_id=org.id, plan_key=p.key, months=months, amount=amount, currency=p.currency, method=str(body.get("method") or "bKash")[:40], txn_id=txn[:120], note=str(body.get("note") or "")[:500]))
    db.commit(); return {"ok": True, "amount": amount}

@router.post("/billing/checkout")
def checkout(body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Only the owner can pay for the subscription.")
    if not stripe_enabled(): raise HTTPException(400, "Card payments are not enabled.")
    p = db.query(Plan).filter_by(key=body.get("plan_key"), active=True).first()
    if not p: raise HTTPException(400, "Unknown plan")
    return {"url": stripe_checkout(org, u, p, "yearly" if body.get("interval") == "yearly" else "monthly")}

@router.post("/billing/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    if not stripe_enabled() or not settings.STRIPE_WEBHOOK_SECRET: raise HTTPException(400, "Stripe is not configured")
    stripe_event(db, await request.body(), request.headers.get("stripe-signature", "")); return {"ok": True}

# ---------------------------------------------------------------- platform admin (you)
@router.get("/admin/overview")
def a_over(a: User = Depends(superadmin), db: Session = Depends(get_db)):
    orgs = db.query(Org).all(); st = [sub_state(o)["status"] for o in orgs]; plans = {p.key: p for p in db.query(Plan).all()}
    mrr = sum(plans[o.plan_key].price_monthly for o in orgs if o.sub_status == "active" and sub_state(o)["active"] and o.plan_key in plans)
    return dict(orgs=len(orgs), trialing=st.count("trialing"), active=st.count("active"), expired=st.count("expired"), suspended=st.count("suspended"),
                pending=db.query(PaymentRequest).filter_by(status="pending").count(), mrr=mrr, users=db.query(User).filter(User.org_id.isnot(None)).count())

@router.get("/admin/orgs")
def a_orgs(a: User = Depends(superadmin), db: Session = Depends(get_db)):
    out = []
    for o in db.query(Org).order_by(Org.id.desc()).all():
        owner = db.query(User).filter_by(org_id=o.id, role="owner").first()
        out.append(dict(id=o.id, name=o.name, created=o.created_at.date().isoformat(), plan=o.plan_key, state=sub_state(o), owner=owner.email if owner else "", users=db.query(User).filter_by(org_id=o.id).count()))
    return {"orgs": out}

@router.post("/admin/orgs/{oid}/action")
def a_action(oid: int, body: dict, a: User = Depends(superadmin), db: Session = Depends(get_db)):
    o = db.get(Org, oid)
    if not o: raise HTTPException(404, "Not found")
    act = body.get("action")
    if act == "extend":
        from datetime import timedelta
        d = int(body.get("days") or 0)
        if not 1 <= d <= 3650: raise HTTPException(400, "Days must be 1-3650")
        if o.sub_status == "trialing": o.trial_ends_at = max(o.trial_ends_at or datetime.utcnow(), datetime.utcnow()) + timedelta(days=d)
        else: o.period_end = max(o.period_end or datetime.utcnow(), datetime.utcnow()) + timedelta(days=d)
    elif act == "plan":
        if not db.query(Plan).filter_by(key=body.get("plan_key")).first(): raise HTTPException(400, "Unknown plan")
        o.plan_key = body["plan_key"]
    elif act in ("suspend", "unsuspend"): o.suspended = act == "suspend"
    else: raise HTTPException(400, "Unknown action")
    db.commit(); return {"ok": True}

@router.get("/admin/payments")
def a_pays(status: str = "pending", a: User = Depends(superadmin), db: Session = Depends(get_db)):
    q = db.query(PaymentRequest)
    if status != "all": q = q.filter_by(status=status)
    out = []
    for r in q.order_by(PaymentRequest.id.desc()).limit(100).all():
        o = db.get(Org, r.org_id); out.append(dict(_req(r), org=o.name if o else "?", org_id=r.org_id))
    return {"rows": out}

@router.post("/admin/payments/{pid}/decide")
def a_decide(pid: int, body: dict, a: User = Depends(superadmin), db: Session = Depends(get_db)):
    r = db.get(PaymentRequest, pid)
    if not r or r.status != "pending": raise HTTPException(400, "Already decided or not found")
    if body.get("approve"):
        o = db.get(Org, r.org_id); activate(o, r.plan_key, 365 if r.months == 12 else 30 * r.months); r.status = "approved"
    else: r.status = "rejected"
    r.decided_at = datetime.utcnow(); r.decided_by = a.id; db.commit(); return {"ok": True}

@router.get("/admin/plans")
def a_plans(a: User = Depends(superadmin), db: Session = Depends(get_db)):
    return {"plans": [plan_dict(p) for p in db.query(Plan).order_by(Plan.sort).all()]}

@router.put("/admin/plans/{key}")
def a_plan_put(key: str, body: dict, a: User = Depends(superadmin), db: Session = Depends(get_db)):
    p = db.query(Plan).filter_by(key=key).first()
    if not p: raise HTTPException(404, "Not found")
    for k in ("name", "currency", "stripe_price_monthly", "stripe_price_yearly"):
        if k in body: setattr(p, k, str(body[k]).strip())
    for k in ("price_monthly", "price_yearly"):
        if k in body: setattr(p, k, float(body[k]))
    for k in ("max_users", "max_leads", "sort"):
        if k in body: setattr(p, k, int(body[k]))
    if "features" in body: p.features = "|".join(body["features"]) if isinstance(body["features"], list) else str(body["features"])
    if "active" in body: p.active = bool(body["active"])
    db.commit(); return plan_dict(p)

@router.post("/admin/users/reset_password")
def a_reset(body: dict, a: User = Depends(superadmin), db: Session = Depends(get_db)):
    u = db.query(User).filter_by(email=str(body.get("email") or "").lower()).first()
    if not u or u.is_superadmin: raise HTTPException(404, "User not found")
    if len(str(body.get("password") or "")) < 8: raise HTTPException(400, "Password must be at least 8 characters.")
    u.password_hash = hash_pw(body["password"]); u.token_version = (u.token_version or 0) + 1; db.commit(); return {"ok": True}
