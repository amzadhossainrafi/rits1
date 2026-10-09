from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Date, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from .db import Base
from .schema import ENT

def utcnow(): return datetime.utcnow()

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    key = Column(String(40), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    price_monthly = Column(Float, default=0)
    price_yearly = Column(Float, default=0)
    currency = Column(String(8), default="BDT")
    max_users = Column(Integer, default=5)
    max_leads = Column(Integer, default=500)
    features = Column(Text, default="")
    stripe_price_monthly = Column(String(80), default="")
    stripe_price_yearly = Column(String(80), default="")
    active = Column(Boolean, default=True)
    sort = Column(Integer, default=0)

class Org(Base):
    __tablename__ = "orgs"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    settings_json = Column(Text, default="{}")
    plan_key = Column(String(40), default="business")
    sub_status = Column(String(20), default="trialing")   # trialing | active | canceled
    trial_ends_at = Column(DateTime)
    period_end = Column(DateTime)
    suspended = Column(Boolean, default=False)
    stripe_customer_id = Column(String(80), default="")
    stripe_subscription_id = Column(String(80), default="")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(160), nullable=False)
    password_hash = Column(String(120), nullable=False)
    role = Column(String(20), default="member")
    employee_code = Column(String(20), default="")
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    last_login = Column(DateTime)
    token_version = Column(Integer, default=0)

class Counter(Base):
    __tablename__ = "counters"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, index=True)
    kind = Column(String(30))
    n = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint("org_id", "kind", name="uq_counter"),)

class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), index=True)
    plan_key = Column(String(40))
    months = Column(Integer, default=1)
    amount = Column(Float, default=0)
    currency = Column(String(8), default="BDT")
    method = Column(String(40))
    txn_id = Column(String(120))
    note = Column(Text, default="")
    status = Column(String(20), default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=utcnow)
    decided_at = Column(DateTime)
    decided_by = Column(Integer)

class ResetToken(Base):
    __tablename__ = "reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    token_hash = Column(String(64), unique=True)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)

class Audit(Base):
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, index=True)
    user_id = Column(Integer)
    user_name = Column(String(160))
    action = Column(String(20))
    kind = Column(String(30))
    code = Column(String(30))
    detail = Column(String(300), default="")
    at = Column(DateTime, default=utcnow)

_T = {"str": lambda: String(255), "text": lambda: Text(), "int": lambda: Integer(), "float": lambda: Float(), "date": lambda: Date(),
      "datetime": lambda: DateTime(), "select": lambda: String(120), "ref": lambda: String(40)}
MODELS = {}
for _k, _e in ENT.items():
    attrs = {"__tablename__": "e_" + _k, "id": Column(Integer, primary_key=True),
             "org_id": Column(Integer, ForeignKey("orgs.id"), index=True, nullable=False), "code": Column(String(20), index=True),
             "created_at": Column(DateTime, default=utcnow), "updated_at": Column(DateTime, default=utcnow, onupdate=utcnow), "created_by": Column(Integer),
             "__table_args__": (UniqueConstraint("org_id", "code", name=f"uq_{_k}_code"),)}
    for _f in _e["fields"]:
        attrs[_f.name] = Column(_T[_f.type]())
    MODELS[_k] = type("E_" + _k.title(), (Base,), attrs)

def next_code(db, org_id, kind):
    c = db.query(Counter).filter_by(org_id=org_id, kind=kind).with_for_update().first()
    if not c:
        c = Counter(org_id=org_id, kind=kind, n=0); db.add(c); db.flush()
    c.n += 1
    e = ENT[kind]
    return f"{e['prefix']}{c.n:0{e['digits']}d}"
