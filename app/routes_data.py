import csv, io
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .db import get_db
from .models import MODELS, User, Org, Audit, next_code
from .schema import ENT, can
from .security import current_user, current_org
from .billing import require_active, plan_of
from .compute import Ctx, dashboard, operations, finance, today_queue, cdisp

router = APIRouter(prefix="/api")

def jv(v):
    if isinstance(v, datetime): return v.isoformat(timespec="minutes")
    if isinstance(v, date): return v.isoformat()
    return v

def ser(kind, r, comp, role):
    d = {"code": r["code"]}
    for f in ENT[kind]["fields"]:
        if f.only and role not in f.only: continue
        d[f.name] = jv(r[f.name])
    for k, v in (comp or {}).items(): d["c_" + k] = jv(v)
    return d

def _need(u, kind, need):
    if not can(u.role, kind, need): raise HTTPException(403, "You don't have access to this.")

def _ent(kind):
    if kind not in ENT: raise HTTPException(404, "Unknown record type")
    return ENT[kind]

def _parse(f, v, ctx, current):
    if v is None or (isinstance(v, str) and not v.strip()): return None
    try:
        if f.type == "int": return int(float(v))
        if f.type == "float": return float(v)
        if f.type == "date": return date.fromisoformat(str(v)[:10])
        if f.type == "datetime":
            s = str(v).replace("Z", ""); return datetime.fromisoformat(s if "T" in s or " " in s else s + "T00:00")
    except (ValueError, TypeError): raise HTTPException(400, f"{f.label}: invalid value")
    v = str(v).strip()
    if f.type == "ref" and f.ref and v not in ctx.by(f.ref): raise HTTPException(400, f"{f.label}: '{v}' was not found")
    if f.type == "select" and f.opt and v != current and v not in ctx.s["lists"].get(f.opt, [v]): raise HTTPException(400, f"{f.label}: '{v}' is not an allowed value")
    return v[:255] if f.type in ("str", "select", "ref") else v[:5000]

def _coerce(kind, body, u, ctx, row=None):
    out = {}
    for f in ENT[kind]["fields"]:
        if f.only and u.role not in f.only: continue
        if f.name in body: out[f.name] = _parse(f, body[f.name], ctx, getattr(row, f.name) if row else None)
        elif row is None:
            d = f.default; out[f.name] = ctx.now.replace(second=0, microsecond=0) if d == "now" and f.type == "datetime" else ctx.today if d == "today" and f.type == "date" else (d if d not in ("now", "today") else None)
        if (f.req and (f.name in out or row is None) and out.get(f.name) in (None, "")): raise HTTPException(400, f"{f.label} is required")
    return out

def _audit(db, u, action, kind, code, detail=""):
    db.add(Audit(org_id=u.org_id, user_id=u.id, user_name=u.name, action=action, kind=kind, code=code, detail=detail[:300]))

def _one(db, org, u, kind, code):
    ctx = Ctx(db, org); r = ctx.by(kind).get(code)
    if not r: raise HTTPException(404, "Not found")
    return ser(kind, r, ctx.comp(kind)[code], u.role)

@router.get("/d/{kind}")
def list_(kind: str, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    e = _ent(kind); _need(u, kind, "v"); ctx = Ctx(db, org); comp = ctx.comp(kind)
    rows = [ser(kind, r, comp[r["code"]], u.role) for r in ctx.rows(kind)]
    refs = sorted({f.ref for f in e["fields"] if f.ref}); labels = ctx.labels(refs) if refs else {}
    return {"rows": rows, "labels": labels}

@router.get("/refs")
def refs(u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    ctx = Ctx(db, org); return ctx.labels(["lead", "client", "deal", "employee"])

@router.get("/d/{kind}/{code}")
def get_(kind: str, code: str, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _ent(kind); _need(u, kind, "v"); return _one(db, org, u, kind, code)

@router.post("/d/{kind}")
def create(kind: str, body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _ent(kind); _need(u, kind, "e"); require_active(org); ctx = Ctx(db, org)
    if kind == "lead":
        plan = plan_of(db, org)
        if db.query(MODELS["lead"]).filter_by(org_id=org.id).count() >= plan.max_leads: raise HTTPException(402, f"Your {plan.name} plan allows {plan.max_leads} leads. Upgrade in Billing.")
    vals = _coerce(kind, body, u, ctx); code = next_code(db, org.id, kind)
    if kind == "deal":  # freeze today's default rate/charge on the deal so later setting changes never rewrite old deals
        if vals.get("rate") is None: vals["rate"] = ctx.s["rate"]
        if vals.get("charge_pct") is None: vals["charge_pct"] = ctx.s["default_charge"]
    db.add(MODELS[kind](org_id=org.id, code=code, created_by=u.id, **vals)); _audit(db, u, "create", kind, code); db.commit()
    return _one(db, org, u, kind, code)

@router.put("/d/{kind}/{code}")
def update(kind: str, code: str, body: dict, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _ent(kind); _need(u, kind, "e"); require_active(org); M = MODELS[kind]
    row = db.query(M).filter_by(org_id=org.id, code=code).first()
    if not row: raise HTTPException(404, "Not found")
    vals = _coerce(kind, body, u, Ctx(db, org), row)
    for k, v in vals.items(): setattr(row, k, v)
    _audit(db, u, "update", kind, code, ", ".join(vals.keys())); db.commit()
    return _one(db, org, u, kind, code)

@router.delete("/d/{kind}/{code}")
def delete(kind: str, code: str, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _ent(kind); _need(u, kind, "e"); require_active(org); M = MODELS[kind]
    row = db.query(M).filter_by(org_id=org.id, code=code).first()
    if not row: raise HTTPException(404, "Not found")
    for k2, e2 in ENT.items():
        for f in e2["fields"]:
            if f.ref == kind:
                n = db.query(MODELS[k2]).filter(MODELS[k2].org_id == org.id, getattr(MODELS[k2], f.name) == code).count()
                if n: raise HTTPException(409, f"Cannot delete: {n} {e2['label'].lower()} still use {code}. Remove or reassign them first.")
    db.delete(row); _audit(db, u, "delete", kind, code); db.commit()
    return {"ok": True}

def _range(frm, to, ctx):
    try: a = date.fromisoformat(frm) if frm else date(ctx.today.year, 1, 1); b = date.fromisoformat(to) if to else date(ctx.today.year, 12, 31)
    except ValueError: raise HTTPException(400, "Bad date")
    return a, b

@router.get("/report/dashboard")
def r_dash(frm: str = Query(None, alias="from"), to: str = None, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _need(u, "dashboard", "v"); ctx = Ctx(db, org); a, b = _range(frm, to, ctx); return dashboard(ctx, a, b)

@router.get("/report/operations")
def r_ops(u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _need(u, "operations", "v"); return operations(Ctx(db, org))

@router.get("/report/finance")
def r_fin(year: int = None, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _need(u, "finance", "v"); ctx = Ctx(db, org); return finance(ctx, year or ctx.today.year, can(u.role, "payroll", "v"))

@router.get("/report/today")
def r_today(u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _need(u, "today", "v"); return {"rows": today_queue(Ctx(db, org))}

@router.get("/client360/{code}")
def c360(code: str, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _need(u, "client360", "v"); ctx = Ctx(db, org); cl = ctx.by("client").get(code)
    if not cl: raise HTTPException(404, "Client not found")
    S = lambda k, r: ser(k, r, ctx.comp(k)[r["code"]], u.role)
    deals = ctx.group("deal", "client_code").get(code, []); dcodes = {d["code"] for d in deals}
    out = dict(client=S("client", cl), lead=ctx.by("lead").get(cl["lead_code"]) and ser("lead", ctx.by("lead")[cl["lead_code"]], ctx.comp("lead")[cl["lead_code"]], u.role),
        deals=[S("deal", d) for d in deals], team=[S("assignment", a) for a in ctx.rows("assignment") if a["deal_code"] in dcodes],
        tasks=[S("task", t) for t in ctx.group("task", "client_code").get(code, [])],
        updates=[S("update", x) for x in sorted(ctx.group("update", "client_code").get(code, []), key=lambda x: x["at"] or datetime.min, reverse=True)][:15],
        ads=[S("clientad", x) for x in sorted(ctx.group("clientad", "client_code").get(code, []), key=lambda x: x["month"] or date.min, reverse=True)][:12],
        payments=[S("payment", p) for p in ctx.rows("payment") if p["deal_code"] in dcodes][::-1][:15], labels=ctx.labels(["employee", "deal"]))
    return out

@router.get("/export/{kind}.csv")
def export(kind: str, u: User = Depends(current_user), org: Org = Depends(current_org), db: Session = Depends(get_db)):
    _ent(kind); _need(u, kind, "v"); ctx = Ctx(db, org); comp = ctx.comp(kind); e = ENT[kind]
    s = io.StringIO(); w = csv.writer(s); keys = [f.name for f in e["fields"] if not (f.only and u.role not in f.only)]; ck = [c["key"] for c in e["computed"]]
    w.writerow(["code"] + keys + ["calc_" + k for k in ck])
    for r in ctx.rows(kind):
        w.writerow([r["code"]] + [jv(r[k]) if r[k] is not None else "" for k in keys] + [jv(comp[r["code"]].get(k)) if comp[r["code"]].get(k) is not None else "" for k in ck])
    s.seek(0)
    return StreamingResponse(iter([s.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={kind}.csv"})

@router.get("/audit")
def audit(u: User = Depends(current_user), db: Session = Depends(get_db)):
    if u.role != "owner": raise HTTPException(403, "Owner only")
    rows = db.query(Audit).filter_by(org_id=u.org_id).order_by(Audit.id.desc()).limit(200).all()
    return {"rows": [dict(at=r.at.isoformat(timespec="minutes"), user=r.user_name, action=r.action, kind=r.kind, code=r.code, detail=r.detail) for r in rows]}
