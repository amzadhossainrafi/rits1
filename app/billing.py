import json, math
from datetime import datetime, timedelta
from fastapi import HTTPException
from .config import settings
from .models import Plan, Org

DEFAULT_PLANS = [
    dict(key="starter", name="Starter", price_monthly=999, price_yearly=9990, max_users=5, max_leads=500, sort=1,
         features="5 team logins|500 leads|Leads, clients, deals, tasks|Dashboards & Client 360|Email support"),
    dict(key="growth", name="Growth", price_monthly=2499, price_yearly=24990, max_users=15, max_leads=3000, sort=2,
         features="15 team logins|3,000 leads|Everything in Starter|Payroll, expenses & finance|Client ad budgets|Priority support"),
    dict(key="business", name="Business", price_monthly=4999, price_yearly=49990, max_users=50, max_leads=20000, sort=3,
         features="50 team logins|20,000 leads|Everything in Growth|Audit log & CSV export|Onboarding help"),
]

def seed_plans(db):
    if db.query(Plan).count(): return
    for p in DEFAULT_PLANS: db.add(Plan(currency="BDT", **p))
    db.commit()

def sub_state(org):
    now = datetime.utcnow()
    if org.suspended: return dict(status="suspended", active=False, days_left=0, ends=None)
    end = org.trial_ends_at if org.sub_status == "trialing" else org.period_end
    if end and end > now:
        return dict(status=org.sub_status, active=True, days_left=max(0, math.ceil((end - now).total_seconds() / 86400)), ends=end.isoformat())
    return dict(status="expired", active=False, days_left=0, ends=end.isoformat() if end else None)

def require_active(org):
    st = sub_state(org)
    if not st["active"]:
        raise HTTPException(402, "Your subscription is not active. Open Billing to renew." if st["status"] != "suspended" else "This workspace is suspended. Contact support.")

def plan_of(db, org):
    return db.query(Plan).filter_by(key=org.plan_key).first() or db.query(Plan).order_by(Plan.sort).first()

def activate(org, plan_key, days):
    now = datetime.utcnow()
    base = org.period_end if (org.sub_status == "active" and org.period_end and org.period_end > now) else now
    org.plan_key, org.sub_status, org.period_end = plan_key, "active", base + timedelta(days=days)

def plan_dict(p):
    return dict(key=p.key, name=p.name, price_monthly=p.price_monthly, price_yearly=p.price_yearly, currency=p.currency, max_users=p.max_users,
                max_leads=p.max_leads, features=[x for x in (p.features or "").split("|") if x], active=p.active, sort=p.sort,
                stripe_price_monthly=p.stripe_price_monthly or "", stripe_price_yearly=p.stripe_price_yearly or "")

def stripe_enabled(): return bool(settings.STRIPE_SECRET_KEY)

def stripe_checkout(org, user, plan, interval):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    price = plan.stripe_price_yearly if interval == "yearly" else plan.stripe_price_monthly
    if not price: raise HTTPException(400, "This plan has no Stripe price configured yet.")
    s = stripe.checkout.Session.create(mode="subscription", line_items=[{"price": price, "quantity": 1}], customer_email=user.email,
        client_reference_id=str(org.id), metadata={"org_id": str(org.id), "plan_key": plan.key},
        success_url=settings.BASE_URL + "/#/billing?paid=1", cancel_url=settings.BASE_URL + "/#/billing")
    return s.url

def stripe_event(db, payload, sig):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try: ev = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception: raise HTTPException(400, "Bad signature")
    obj = ev["data"]["object"]; t = ev["type"]
    org = None
    if t == "checkout.session.completed":
        org = db.get(Org, int(obj.get("client_reference_id") or (obj.get("metadata") or {}).get("org_id") or 0))
        if org:
            org.stripe_customer_id, org.stripe_subscription_id = obj.get("customer") or "", obj.get("subscription") or ""
            org.plan_key = (obj.get("metadata") or {}).get("plan_key") or org.plan_key
            org.sub_status = "active"; org.period_end = datetime.utcnow() + timedelta(days=35)
    elif t == "invoice.paid":
        org = db.query(Org).filter_by(stripe_customer_id=obj.get("customer")).first()
        if org:
            try: end = obj["lines"]["data"][0]["period"]["end"]; org.period_end = datetime.utcfromtimestamp(end) + timedelta(days=2)
            except (KeyError, IndexError): org.period_end = datetime.utcnow() + timedelta(days=33)
            org.sub_status = "active"
    elif t == "customer.subscription.deleted":
        org = db.query(Org).filter_by(stripe_customer_id=obj.get("customer")).first()
        if org: org.sub_status = "canceled"
    db.commit()
