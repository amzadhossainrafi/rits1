import os, sys, tempfile
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL") or "sqlite:///" + os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["SUPERADMIN_EMAIL"] = "admin@ritsone.test"; os.environ["SUPERADMIN_PASSWORD"] = "SuperSecret123"
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime, timedelta, date
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models import Org

H = {"X-Requested-With": "RITS"}
def client(): return TestClient(app, headers=H)

def test_everything():
    with TestClient(app, headers=H) as a:
        r = a.post("/api/auth/signup", json={"org_name": "Rafirit Station", "name": "Amzad", "email": "amzad@rafirit.test", "password": "password123", "template": "agency"}); assert r.status_code == 200, r.text
        me = a.get("/api/me").json(); assert me["user"]["role"] == "owner" and me["subscription"]["status"] == "trialing" and me["subscription"]["active"]
        assert a.post("/api/auth/signup", json={"org_name": "x", "name": "y", "email": "amzad@rafirit.test", "password": "password123"}).status_code == 409
        # CSRF guard
        assert TestClient(app).post("/api/auth/login", json={}).status_code == 403
        # employees
        e2 = a.post("/api/d/employee", json={"name": "Nadia", "role": "Team Lead", "salary": 45000}).json(); e3 = a.post("/api/d/employee", json={"name": "Sabbir", "role": "Team Member", "salary": 25000}).json()
        assert e2["code"] == "E-002" and e2["salary"] == 45000
        # leads
        now = datetime.utcnow() + timedelta(hours=6)
        L = a.post("/api/d/lead", json={"name": "John Doe", "company": "Acme", "channel": "Meta Ads", "country": "United States", "service": "SEO Services", "bok": "Yes", "dm": "Yes", "need": "Yes", "soon": "No",
              "received_at": (now - timedelta(hours=1)).isoformat(timespec="minutes"), "first_response_at": (now - timedelta(minutes=30)).isoformat(timespec="minutes"), "stage": "Won"}).json()
        assert L["code"] == "L-0001" and L["c_qual"] == "Qualified" and L["c_score"] == 75 and L["c_ptype"] == "Paid" and L["c_market"] == "International" and L["c_sla"] == "On time"
        L2 = a.post("/api/d/lead", json={"name": "Rahim", "country": "Bangladesh", "service": "Web Development", "received_at": (now - timedelta(hours=5)).isoformat(timespec="minutes")}).json()
        assert L2["c_fu_status"] == "Respond now" and L2["c_sla"].startswith("Breached") and L2["c_market"] == "Local"
        assert a.post("/api/d/lead", json={"name": "Bad", "stage": "Nonsense"}).status_code == 400
        assert a.post("/api/d/lead", json={"service": "SEO Services"}).status_code == 400
        q = a.get("/api/report/today").json()["rows"]; assert q[0]["code"] == "L-0002"
        a.post("/api/d/followup", json={"lead_code": "L-0001", "chan": "WhatsApp", "outcome": "Meeting booked"})
        assert a.get("/api/d/lead/L-0001").json()["c_fu_count"] == 1
        # client, deal, payment
        c = a.post("/api/d/client", json={"lead_code": "L-0001", "status": "Active", "am": e2["code"], "health": "Red"}).json(); assert c["code"] == "C-0001" and c["c_display"] == "John Doe · Acme"
        assert a.get("/api/d/lead/L-0001").json()["c_client_code"] == "C-0001"
        d = a.post("/api/d/deal", json={"client_code": "C-0001", "service": "SEO Services", "price_fc": 500, "charge_pct": 5, "pstatus": "In progress", "due_date": (date.today() - timedelta(days=3)).isoformat()}).json()
        assert d["c_total"] == 78750 and d["c_pay_status"] == "Unpaid" and d["c_alert"] == "Overdue" and d["c_project_lead"] == "Not assigned"
        a.post("/api/d/payment", json={"deal_code": "D-0001", "amount": 40000, "method": "bKash", "date": date.today().isoformat()})
        d = a.get("/api/d/deal/D-0001").json(); assert d["c_paid"] == 40000 and d["c_balance"] == 38750 and d["c_pay_status"] == "Partial"
        # assignments & workload
        a.post("/api/d/assignment", json={"deal_code": "D-0001", "employee": e2["code"], "prole": "Project Lead", "alloc": 40})
        a.post("/api/d/assignment", json={"deal_code": "D-0001", "employee": e3["code"], "prole": "Team Member", "alloc": 120})
        assert a.get("/api/d/deal/D-0001").json()["c_project_lead"] == "Nadia"
        emps = {x["name"]: x for x in a.get("/api/d/employee").json()["rows"]}; assert emps["Sabbir"]["c_util"] == "Overloaded" and emps["Nadia"]["c_util"] == "Available"
        # tasks, updates, ads, expenses, payroll, own ads
        a.post("/api/d/task", json={"client_code": "C-0001", "title": "Audit", "assignee": e3["code"], "due": (date.today() - timedelta(days=1)).isoformat()})
        assert a.get("/api/d/task/T-0001").json()["c_flag"] == "Overdue"
        a.post("/api/d/update", json={"client_code": "C-0001", "utype": "Weekly report", "summary": "Done", "sentiment": "Happy"})
        a.post("/api/d/clientad", json={"client_code": "C-0001", "platform": "Meta Ads", "currency": "USD", "budget": 400, "spend": 130, "paid_by": "Agency card (reimburse)", "reimbursed": "No", "results": 18, "revenue": 900})
        ad = a.get("/api/d/clientad/B-0001").json(); assert ad["c_budget_base"] == 60000 and ad["c_spend_base"] == 19500 and ad["c_flag"] == "OK"
        a.post("/api/d/expense", json={"category": "Software & Tools", "amount": 5000, "client_code": "C-0001"})
        a.post("/api/d/payroll", json={"employee": e2["code"], "status": "Pending"}); assert a.get("/api/d/payroll/PR-0001").json()["c_net"] == 45000
        a.post("/api/d/ownad", json={"platform": "Meta Ads", "amount": 12.5, "currency": "USD"})
        cl = a.get("/api/d/client/C-0001").json(); assert cl["c_contract"] == 78750 and cl["c_paid"] == 40000 and cl["c_team"] == 2 and cl["c_open_tasks"] == 1 and cl["c_overdue_tasks"] == 1 and cl["c_margin"] == 35000
        assert cl["c_update_status"] == "OK" and cl["c_budget_m"] == 60000
        # reports
        db = a.get("/api/report/dashboard").json()["cards"]; assert db["leads"] == 2 and db["won"] == 1 and db["revenue"] == 78750 and db["cash"] == 40000 and db["ad_spend"] == 1875 and db["outstanding"] == 38750
        op = a.get("/api/report/operations").json(); assert op["cards"]["active"] == 1 and op["cards"]["red"] == 1 and op["cards"]["overloaded"] == 1 and op["cards"]["advanced"] == 19500
        fn = a.get("/api/report/finance").json(); assert fn["totals"]["cash"] == 40000 and fn["totals"]["payroll"] == 45000 and fn["totals"]["costs"] == 1875 + 45000 + 5000
        v = a.get("/api/client360/C-0001").json(); assert len(v["deals"]) == 1 and len(v["team"]) == 2 and len(v["payments"]) == 1 and len(v["updates"]) == 1
        assert a.get("/api/export/lead.csv").text.startswith("code,")
        # referential integrity
        assert a.delete("/api/d/client/C-0001").status_code == 409
        # team logins & roles
        assert a.post("/api/team/users", json={"name": "Seller", "email": "sales@rafirit.test", "role": "sales", "password": "password123"}).status_code == 200
        assert a.post("/api/team/users", json={"name": "Mem", "email": "mem@rafirit.test", "role": "member", "password": "password123"}).status_code == 200
        s = client(); assert s.post("/api/auth/login", json={"email": "sales@rafirit.test", "password": "password123"}).status_code == 200
        assert s.get("/api/report/finance").status_code == 403 and s.get("/api/d/payment").status_code == 403 and s.get("/api/d/payroll").status_code == 403
        assert s.post("/api/d/lead", json={"name": "Via sales"}).status_code == 200
        m = client(); m.post("/api/auth/login", json={"email": "mem@rafirit.test", "password": "password123"})
        assert "salary" not in m.get("/api/d/employee").json()["rows"][0] if m.get("/api/d/employee").status_code == 200 else True
        assert m.get("/api/d/lead").status_code == 403 and m.post("/api/d/task", json={"client_code": "C-0001", "title": "x"}).status_code == 200
        assert client().post("/api/auth/login", json={"email": "sales@rafirit.test", "password": "wrong"}).status_code == 401
        # tenant isolation
        b = client(); b.post("/api/auth/signup", json={"org_name": "Other Co", "name": "Bob", "email": "bob@other.test", "password": "password123", "template": "general"})
        assert b.get("/api/d/lead").json()["rows"] == [] and b.get("/api/d/lead/L-0001").status_code == 404 and b.get("/api/client360/C-0001").status_code == 404
        assert "Consulting" in b.get("/api/me").json()["settings"]["lists"]["services"]
        assert b.post("/api/d/deal", json={"client_code": "C-0001", "service": "x", "price_fc": 1}).status_code == 400
        # settings
        assert a.put("/api/org", json={"settings": {"rate": 120, "monthly_target": 500000, "lists": {"services": ["A", "B"]}}}).status_code == 200
        assert a.get("/api/d/deal/D-0001").json()["c_total"] == 78750  # deal keeps working; default rate only used when blank
        # subscription enforcement
        with SessionLocal() as ses:
            o = ses.query(Org).filter_by(name="Rafirit Station").first(); o.trial_ends_at = datetime.utcnow() - timedelta(days=1); ses.commit()
        assert a.get("/api/d/lead").status_code == 200 and a.post("/api/d/lead", json={"name": "Blocked"}).status_code == 402
        bl = a.get("/api/billing").json(); assert bl["state"]["status"] == "expired" and len(bl["plans"]) == 3
        assert a.post("/api/billing/request", json={"plan_key": "growth", "months": 1, "method": "bKash", "txn_id": "TX12345"}).json()["amount"] == 2499
        assert a.post("/api/billing/request", json={"plan_key": "growth", "months": 1, "txn_id": "TX12345"}).status_code == 409
        # platform admin approves
        adm = client(); assert adm.post("/api/auth/login", json={"email": "admin@ritsone.test", "password": "SuperSecret123"}).status_code == 200
        assert adm.get("/api/me").json()["user"]["superadmin"] and adm.get("/api/d/lead").status_code == 403
        pend = adm.get("/api/admin/payments").json()["rows"]; assert len(pend) == 1 and pend[0]["org"] == "Rafirit Station"
        assert adm.post(f"/api/admin/payments/{pend[0]['id']}/decide", json={"approve": True}).status_code == 200
        assert a.get("/api/me").json()["subscription"]["status"] == "active" and a.post("/api/d/lead", json={"name": "Back again"}).status_code == 200
        assert adm.get("/api/admin/overview").json()["orgs"] == 2 and not client().get("/api/admin/orgs").status_code == 200
        assert a.get("/api/admin/orgs").status_code == 403
        # plan limits
        assert adm.put("/api/admin/plans/growth", json={"max_users": 3}).status_code == 200
        assert a.post("/api/team/users", json={"name": "Over", "email": "over@rafirit.test", "role": "member", "password": "password123"}).status_code == 402
        assert a.get("/api/audit").json()["rows"]
        assert a.get("/health").json()["ok"] and a.get("/some/page").status_code == 200

if __name__ == "__main__":
    test_everything(); print("ALL OK")
