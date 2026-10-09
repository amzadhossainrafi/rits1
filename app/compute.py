"""Business logic: computed fields (the sheet formulas) and dashboards."""
import json
from datetime import datetime, date, timedelta
from .models import MODELS
from .schema import ENT, merged_settings

def num(x):
    try: return float(x) if x not in (None, "") else 0.0
    except (TypeError, ValueError): return 0.0
def dd(x): return x.date() if isinstance(x, datetime) else x
def r0(x): return int(round(x))
def pct(a, b): return (a / b) if b else 0.0

def org_settings(org):
    try: stored = json.loads(org.settings_json or "{}")
    except ValueError: stored = {}
    return merged_settings(stored)

class Ctx:
    def __init__(self, db, org):
        self.db, self.org, self.s = db, org, org_settings(org)
        self.now = datetime.utcnow() + timedelta(hours=float(self.s["tz_offset"]))
        self.today = self.now.date()
        self._rows, self._by, self._grp, self._comp = {}, {}, {}, {}
    def rows(self, kind):
        if kind not in self._rows:
            M = MODELS[kind]; out = []
            for o in self.db.query(M).filter(M.org_id == self.org.id).order_by(M.id).all():
                d = {"id": o.id, "code": o.code, "created_at": o.created_at}
                for f in ENT[kind]["fields"]: d[f.name] = getattr(o, f.name)
                out.append(d)
            self._rows[kind] = out
        return self._rows[kind]
    def by(self, kind):
        if kind not in self._by: self._by[kind] = {r["code"]: r for r in self.rows(kind)}
        return self._by[kind]
    def group(self, kind, field):
        k = (kind, field)
        if k not in self._grp:
            g = {}
            for r in self.rows(kind): g.setdefault(r.get(field), []).append(r)
            self._grp[k] = g
        return self._grp[k]
    def comp(self, kind):
        if kind not in self._comp:
            fn = COMPUTE.get(kind)
            self._comp[kind] = {r["code"]: (fn(self, r) if fn else {}) for r in self.rows(kind)}
        return self._comp[kind]
    def label(self, kind, code):
        r = self.by(kind).get(code)
        if not r: return code or ""
        if kind == "lead": return r["name"] + (f" · {r['company']}" if r.get("company") else "")
        if kind == "client": return cdisp(self, code)
        if kind == "deal": return f"{code} · {r.get('service') or ''}"
        if kind == "employee": return r["name"]
        return code
    def labels(self, kinds):
        return {k: {r["code"]: self.label(k, r["code"]) for r in self.rows(k)} for k in kinds}
    def base_amt(self, amount, currency, rate=None):
        if amount in (None, ""): return None
        return float(amount) if currency == self.s["currency_base"] else float(amount) * (rate or self.s["rate"])
    def month_of(self, d): return d and (d.year, d.month)

def cdisp(c, code):
    cl = c.by("client").get(code)
    if not cl: return code or ""
    le = c.by("lead").get(cl["lead_code"])
    if not le: return "Lead ID not found"
    return le["name"] + (f" · {le['company']}" if le.get("company") else "")

def lead_c(c, r):
    s, code = c.s, r["code"]
    keys = ("bok", "dm", "need", "soon"); ans = [r[k] for k in keys if r[k]]
    score = 25 * sum(1 for k in keys if r[k] == "Yes") if ans else None
    qual = None
    if r["received_at"]:
        qual = "Not scored" if len(ans) < 4 else ("Qualified" if score >= s["qualified_score"] else "Warm" if score >= s["warm_score"] else "Unqualified")
    rec, fr = r["received_at"], r["first_response_at"]
    resp = round((fr - rec).total_seconds() / 3600, 1) if rec and fr else None
    open_new = (r["stage"] or "New") == "New"
    if resp is None:
        sla = "Breached - respond now" if rec and open_new and (c.now - rec).total_seconds() / 3600 > s["sla_hours"] else None
    else: sla = "On time" if resp <= s["sla_hours"] else "Late"
    fu = c.group("followup", "lead_code").get(code, [])
    last = max((f["at"] for f in fu if f["at"]), default=None)
    stage = r["stage"] or "New"
    if not rec: st = None
    elif stage in ("Won", "Lost"): st = "Closed"
    elif stage == "New" and not fr: st = "Respond now"
    elif not r["next_followup"]: st = "No date set"
    elif r["next_followup"] < c.today: st = "Overdue"
    elif r["next_followup"] == c.today: st = "Due today"
    else: st = "Upcoming"
    cl = next((x["code"] for x in c.group("client", "lead_code").get(code, [])), "")
    return dict(qual=qual, score=score, ptype=("Paid" if r["channel"] in s["lists"]["paid_channels"] else "Organic") if r["channel"] else None,
        market=None if not r["country"] else ("Local" if r["country"].strip().lower() == s["home_country"].lower() else "International"),
        resp_hours=resp, sla=sla, last_contact=last.isoformat() if last else None, fu_count=len(fu), fu_status=st,
        age=None if stage in ("Won", "Lost") or not rec else (c.now - rec).days, client_code=cl)

def followup_c(c, r):
    l = c.by("lead").get(r["lead_code"]); return dict(lead=l["name"] if l else "ID not found")

def client_c(c, r):
    s, code = c.s, r["code"]; le = c.by("lead").get(r["lead_code"]) or {}
    deals = c.group("deal", "client_code").get(code, []); dc = c.comp("deal")
    contract = sum(dc[d["code"]]["total"] for d in deals); paid = sum(dc[d["code"]]["paid"] for d in deals)
    ads = [a for a in c.group("clientad", "client_code").get(code, []) if a["month"] and (a["month"].year, a["month"].month) == (c.today.year, c.today.month)]
    ac = c.comp("clientad")
    ups = c.group("update", "client_code").get(code, []); last = max((u["at"] for u in ups if u["at"]), default=None)
    days = (c.now - last).days if last else None
    if r["status"] in ("Paused", "Completed", "Churned"): us = None
    elif last is None: us = "No update yet"
    else: us = "Update overdue" if days > s["update_days"] else "OK"
    tasks = c.group("task", "client_code").get(code, []); tc = c.comp("task")
    dcodes = {d["code"] for d in deals}
    team = [a for a in c.rows("assignment") if a["deal_code"] in dcodes and a["status"] == "Active"]
    dcost = sum(num(x["amount"]) for x in c.group("expense", "client_code").get(code, []))
    name = le.get("name") or "Lead ID not found"
    return dict(display=name + (f" · {le['company']}" if le.get("company") else ""), company=le.get("company") or "", email=le.get("email") or "", phone=le.get("phone") or "",
        country=le.get("country") or "", channel=le.get("channel") or "", deals=len(deals), contract=contract, paid=paid, balance=contract - paid,
        budget_m=sum(ac[a["code"]]["budget_base"] or 0 for a in ads), spend_m=sum(ac[a["code"]]["spend_base"] or 0 for a in ads),
        last_update=last.isoformat() if last else None, days_update=days, update_status=us, team=len(team),
        open_tasks=sum(1 for t in tasks if t["status"] != "Done"), overdue_tasks=sum(1 for t in tasks if tc[t["code"]]["flag"] == "Overdue"),
        direct_costs=dcost, margin=paid - dcost)

def deal_c(c, r):
    s = c.s; cl = c.by("client").get(r["client_code"]); le = c.by("lead").get(cl["lead_code"]) if cl else None
    chg = r["charge_pct"] if r["charge_pct"] is not None else s["default_charge"]; rate = r["rate"] or s["rate"]
    total_fc = num(r["price_fc"]) * (1 + num(chg) / 100); total = r0(total_fc * rate)
    paid = sum(num(p["amount"]) for p in c.group("payment", "deal_code").get(r["code"], []))
    bal = total - paid
    ps = None if r["price_fc"] is None else ("Unpaid" if paid <= 0 else "Overpaid" if paid > total else "Paid" if bal <= 0 else "Partial")
    if r["pstatus"] in ("Delivered", "Cancelled"): al = r["pstatus"]
    elif not r["due_date"]: al = "No due date"
    elif r["due_date"] < c.today: al = "Overdue"
    elif (r["due_date"] - c.today).days <= 3: al = f"Due in {(r['due_date'] - c.today).days} d"
    else: al = "On track"
    asg = [a for a in c.group("assignment", "deal_code").get(r["code"], []) if a["status"] == "Active"]
    pl = next((c.by("employee").get(a["employee"], {}).get("name") for a in asg if a["prole"] == "Project Lead"), None)
    return dict(lead_code=cl["lead_code"] if cl else "", client=cdisp(c, cl["code"]) if cl else "Client code not found",
        country=(le or {}).get("country") or "", channel=(le or {}).get("channel") or "", charge_used=num(chg), rate_used=rate, total_fc=total_fc, total=total,
        paid=paid, balance=bal, paid_pct=pct(paid, total) * 100, pay_status=ps, alert=al, project_lead=pl or "Not assigned", team=len(asg))

def assignment_c(c, r):
    d = c.by("deal").get(r["deal_code"]); e = c.by("employee").get(r["employee"]) or {}
    cc = d["client_code"] if d else ""
    return dict(client_code=cc, client=cdisp(c, cc) if cc else "", service=d["service"] if d else "", emp_name=e.get("name", "Not found"), emp_role=e.get("role") or "")

def task_c(c, r):
    if r["status"] == "Done": fl = "Done"
    elif not r["due"]: fl = "No due date"
    elif r["due"] < c.today: fl = "Overdue"
    elif r["due"] == c.today: fl = "Due today"
    elif (r["due"] - c.today).days <= 2: fl = "Due soon"
    else: fl = "On track"
    return dict(client=c.label("client", r["client_code"]), flag=fl, days_late=(c.today - r["due"]).days if fl == "Overdue" else None)

def update_c(c, r): return dict(client=c.label("client", r["client_code"]))

def clientad_c(c, r):
    s = c.s; b = c.base_amt(r["budget"], r["currency"]); sp = c.base_amt(r["spend"], r["currency"])
    used = (sp / b * 100) if (b and sp is not None) else None
    flag = None if used is None else ("Over budget" if used > 100 else "Near limit" if used >= s["budget_alert"] else "OK")
    return dict(client=c.label("client", r["client_code"]), budget_base=b, spend_base=sp, used=used, flag=flag,
        cpr=(sp / r["results"]) if sp and r["results"] else None, roas=(num(r["revenue"]) / num(r["spend"])) if r["revenue"] and num(r["spend"]) else None)

def payment_c(c, r):
    d = c.by("deal").get(r["deal_code"]); dc = c.comp("deal").get(r["deal_code"]) if d else None
    rate = dc["rate_used"] if dc else None
    return dict(client_code=d["client_code"] if d else "", client=dc["client"] if dc else "Deal not found", service=d["service"] if d else "", rate=rate,
        amount_fc=round(num(r["amount"]) / rate, 2) if rate else None)

def ownad_c(c, r):
    sp = num(r["amount"]) if r["currency"] == c.s["currency_base"] else num(r["amount"]) * c.s["card_rate"]
    return dict(spend_base=sp, ctr=pct(num(r["clicks"]), num(r["impressions"])) * 100 if r["impressions"] and r["clicks"] else None,
        cpc=sp / r["clicks"] if r["clicks"] else None, cpr=sp / r["results"] if r["results"] else None)

def employee_c(c, r):
    s, code = c.s, r["code"]
    asg = [a for a in c.group("assignment", "employee").get(code, []) if a["status"] == "Active"]
    alloc = sum(num(a["alloc"]) for a in asg); tc = c.comp("task")
    tasks = [t for t in c.group("task", "assignee").get(code, [])]
    util = "Overloaded" if alloc > 100 else "Busy" if alloc >= s["busy_alloc"] else "Available" if alloc > 0 else "Free"
    return dict(alloc=alloc, assigns=len(asg), clients_am=sum(1 for x in c.group("client", "am").get(code, []) if x["status"] in ("Active", "Onboarding")),
        open_tasks=sum(1 for t in tasks if t["status"] != "Done"), overdue=sum(1 for t in tasks if tc[t["code"]]["flag"] == "Overdue"), util=util)

def payroll_c(c, r):
    e = c.by("employee").get(r["employee"]) or {}
    base = num(r["base_override"]) if r["base_override"] is not None else num(e.get("salary"))
    return dict(emp_name=e.get("name", "Not found"), emp_role=e.get("role") or "", base=base, net=base + num(r["bonus"]) - num(r["deductions"]))

def expense_c(c, r): return dict(client=c.label("client", r["client_code"]) if r["client_code"] else "")

COMPUTE = dict(lead=lead_c, followup=followup_c, client=client_c, deal=deal_c, assignment=assignment_c, task=task_c, update=update_c,
               clientad=clientad_c, payment=payment_c, ownad=ownad_c, employee=employee_c, payroll=payroll_c, expense=expense_c)

# ---------------------------------------------------------------- reports
def _in(d, a, b):
    d = dd(d); return d is not None and a <= d <= b

def _month_key(d): return f"{d.year}-{d.month:02d}"

def dashboard(c, a, b):
    s = c.s; lc = c.comp("lead"); dc = c.comp("deal")
    leads = [r for r in c.rows("lead") if _in(r["received_at"], a, b)]
    deals = [r for r in c.rows("deal") if _in(r["won_date"], a, b)]
    pays = [r for r in c.rows("payment") if _in(r["date"], a, b)]
    ads = [r for r in c.rows("ownad") if _in(r["date"], a, b)]; oc = c.comp("ownad")
    spend = sum(oc[x["code"]]["spend_base"] for x in ads)
    revenue = sum(dc[d["code"]]["total"] for d in deals); cash = sum(num(p["amount"]) for p in pays)
    q = [r for r in leads if lc[r["code"]]["qual"] == "Qualified"]; won = [r for r in leads if r["stage"] == "Won"]
    paid_l = [r for r in leads if lc[r["code"]]["ptype"] == "Paid"]; paid_w = [r for r in paid_l if r["stage"] == "Won"]
    resp = [lc[r["code"]]["resp_hours"] for r in leads if lc[r["code"]]["resp_hours"] is not None]
    ont = sum(1 for r in leads if lc[r["code"]]["sla"] == "On time"); late = sum(1 for r in leads if lc[r["code"]]["sla"] == "Late")
    m0 = date(c.today.year, c.today.month, 1)
    month_rev = sum(dc[d["code"]]["total"] for d in c.rows("deal") if d["won_date"] and d["won_date"] >= m0)
    cards = dict(leads=len(leads), qualified=len(q), won=len(won), revenue=revenue, cash=cash, ad_spend=spend, roas=pct(revenue, spend), cpl=pct(spend, len(paid_l)), cac=pct(spend, len(paid_w)),
        avg_resp=(sum(resp) / len(resp)) if resp else 0, ontime=pct(ont, ont + late) * 100, month_target=pct(month_rev, s["monthly_target"]) * 100 if s["monthly_target"] else None,
        outstanding=sum(max(0, v["balance"]) for v in dc.values()), paid_leads=len(paid_l), deals=len(deals))
    st = lambda k: sum(1 for r in c.rows("lead") if lc[r["code"]]["fu_status"] == k)
    won_no_client = sum(1 for r in c.rows("lead") if r["stage"] == "Won" and not lc[r["code"]]["client_code"])
    action = [dict(label="New leads waiting for first response", n=st("Respond now"), hint="Reply now", link="today"),
        dict(label="SLA breached", n=sum(1 for r in c.rows("lead") if lc[r["code"]]["sla"] and lc[r["code"]]["sla"].startswith("Breached")), hint="Waited longer than your response target", link="today"),
        dict(label="Follow-ups overdue", n=st("Overdue"), hint="Contact and set a new date", link="today"), dict(label="Follow-ups due today", n=st("Due today"), hint="Contact today", link="today"),
        dict(label="Open leads with no follow-up date", n=st("No date set"), hint="Set a date so nobody is forgotten", link="lead"),
        dict(label="Won leads not yet set up as a client", n=won_no_client, hint="Create the client from the lead", link="client"),
        dict(label="Deals with payment due", n=sum(1 for v in dc.values() if v["pay_status"] in ("Unpaid", "Partial")), hint="Chase payment", link="deal")]
    funnel = [("Leads received", len(leads)), ("Contacted", sum(1 for r in leads if r["first_response_at"])), ("Qualified", len(q)),
        ("Call / meeting booked", sum(1 for r in leads if r["call_booked"] == "Yes")), ("Proposal sent", sum(1 for r in leads if num(r["proposal_fc"]) > 0)), ("Won", len(won))]
    def dim(field, items, rev_field, rev_src="deal"):
        out = []
        for it in items:
            ls = [r for r in leads if r[field] == it]
            rv = sum(dc[d["code"]]["total"] for d in deals if (d["service"] if rev_field == "service" else dc[d["code"]]["channel"]) == it)
            out.append(dict(name=it, leads=len(ls), qualified=sum(1 for r in ls if lc[r["code"]]["qual"] == "Qualified"), won=sum(1 for r in ls if r["stage"] == "Won"), revenue=rv))
        return [x for x in out if x["leads"] or x["revenue"]]
    paid = []
    for p in s["lists"]["paid_channels"]:
        sp = [x for x in ads if x["platform"] == p]; ls = [r for r in leads if r["channel"] == p]
        spd = sum(oc[x["code"]]["spend_base"] for x in sp); rv = sum(dc[d["code"]]["total"] for d in deals if dc[d["code"]]["channel"] == p)
        if sp or ls: paid.append(dict(platform=p, spend=spd, impressions=sum(num(x["impressions"]) for x in sp), clicks=sum(num(x["clicks"]) for x in sp), leads=len(ls),
            cpl=pct(spd, len(ls)), qualified=sum(1 for r in ls if lc[r["code"]]["qual"] == "Qualified"), won=sum(1 for r in ls if r["stage"] == "Won"), revenue=rv, roas=pct(rv, spd)))
    monthly = []; y = a.year
    for m in range(1, 13):
        k = f"{y}-{m:02d}"; inm = lambda d: d and (dd(d).year, dd(d).month) == (y, m)
        L = [r for r in c.rows("lead") if inm(r["received_at"])]
        monthly.append(dict(month=k, leads=len(L), qualified=sum(1 for r in L if lc[r["code"]]["qual"] == "Qualified"),
            deals=sum(1 for d in c.rows("deal") if inm(d["won_date"])), revenue=sum(dc[d["code"]]["total"] for d in c.rows("deal") if inm(d["won_date"])),
            cash=sum(num(p["amount"]) for p in c.rows("payment") if inm(p["date"])), spend=sum(oc[x["code"]]["spend_base"] for x in c.rows("ownad") if inm(x["date"]))))
    return dict(cards=cards, action=action, funnel=[dict(label=l, n=n) for l, n in funnel], channels=dim("channel", s["lists"]["channels"], "channel"),
        services=dim("service", s["lists"]["services"], "service"), contact=dim("method", s["lists"]["contact"], "none"), paid=paid, monthly=monthly,
        market=[dict(name=n, leads=sum(1 for r in leads if lc[r["code"]]["market"] == n), won=sum(1 for r in leads if lc[r["code"]]["market"] == n and r["stage"] == "Won")) for n in ("Local", "International")])

def operations(c):
    s = c.s; cc = c.comp("client"); tc = c.comp("task"); dc = c.comp("deal"); ec = c.comp("employee"); ac = c.comp("clientad")
    clients = c.rows("client"); live = [r for r in clients if r["status"] in ("Active", "Onboarding")]
    m = (c.today.year, c.today.month); ads = [a for a in c.rows("clientad") if a["month"] and (a["month"].year, a["month"].month) == m]
    notree = sum(1 for r in live if cc[r["code"]]["team"] == 0); noup = sum(1 for r in live if cc[r["code"]]["update_status"] in ("Update overdue", "No update yet"))
    red = sum(1 for r in live if r["health"] == "Red"); overdue = sum(1 for v in tc.values() if v["flag"] == "Overdue")
    action = [("Clients with no team assigned", notree, "Add people on Assignments", "assignment"), ("Clients with no update on time", noup, "Send a report and log it", "update"),
        ("Clients with Red health", red, "Call this week", "client"), ("Overdue tasks", overdue, "Unblock or re-plan", "task"),
        ("Deliveries overdue", sum(1 for v in dc.values() if v["alert"] == "Overdue"), "Check Deals", "deal"),
        ("Client ad lines over budget (this month)", sum(1 for a in ads if ac[a["code"]]["flag"] == "Over budget"), "Pause or get approval", "clientad"),
        ("Client ad lines near limit (this month)", sum(1 for a in ads if ac[a["code"]]["flag"] == "Near limit"), "Warn the client", "clientad"),
        ("Staff overloaded", sum(1 for v in ec.values() if v["util"] == "Overloaded"), "Re-balance Assignments", "employee"),
        ("Agency-paid ad spend not reimbursed", sum(1 for a in c.rows("clientad") if a["paid_by"] == "Agency card (reimburse)" and a["reimbursed"] == "No"), "Accounts: invoice the client", "clientad"),
        ("Salaries pending", sum(1 for p in c.rows("payroll") if p["status"] == "Pending"), "Accounts: pay and mark Paid", "payroll")]
    by_status = []
    for st in s["lists"]["cstatus"]:
        L = [r for r in clients if r["status"] == st]
        by_status.append(dict(name=st, n=len(L), contract=sum(cc[r["code"]]["contract"] for r in L), paid=sum(cc[r["code"]]["paid"] for r in L)))
    emps = [dict(code=r["code"], name=r["name"], role=r["role"], dept=r["dept"], status=r["status"], **ec[r["code"]]) for r in c.rows("employee")]
    plats = []
    for p in s["lists"]["paid_channels"]:
        L = [a for a in ads if a["platform"] == p]
        if L: plats.append(dict(platform=p, budget=sum(ac[a["code"]]["budget_base"] or 0 for a in L), spend=sum(ac[a["code"]]["spend_base"] or 0 for a in L), results=sum(num(a["results"]) for a in L)))
    bsum = sum(ac[a["code"]]["budget_base"] or 0 for a in ads); ssum = sum(ac[a["code"]]["spend_base"] or 0 for a in ads)
    cards = dict(active=sum(1 for r in clients if r["status"] == "Active"), onboarding=sum(1 for r in clients if r["status"] == "Onboarding"), red=red, amber=sum(1 for r in live if r["health"] == "Amber"),
        updates_due=noup, open_tasks=sum(1 for t in c.rows("task") if t["status"] != "Done"), overdue_tasks=overdue, in_progress=sum(1 for r in c.rows("deal") if r["pstatus"] == "In progress"),
        staff=sum(1 for r in c.rows("employee") if r["status"] == "Active"), avg_alloc=pct(sum(v["alloc"] for e, v in zip(c.rows("employee"), [ec[x["code"]] for x in c.rows("employee")]) if e["status"] == "Active"), max(1, sum(1 for r in c.rows("employee") if r["status"] == "Active"))),
        overloaded=sum(1 for v in ec.values() if v["util"] == "Overloaded"), ad_budget=bsum, ad_spend=ssum, advanced=sum(ac[a["code"]]["spend_base"] or 0 for a in c.rows("clientad") if a["paid_by"] == "Agency card (reimburse)" and a["reimbursed"] == "No"))
    health = [dict(name=h, n=sum(1 for r in live if r["health"] == h)) for h in s["lists"]["health"]]
    return dict(cards=cards, action=[dict(label=l, n=n, hint=h, link=k) for l, n, h, k in action], by_status=by_status, health=health, team=emps, ads=plats,
        deals_by=[dict(name=p, n=sum(1 for r in c.rows("deal") if r["pstatus"] == p)) for p in s["lists"]["pstat"]],
        tasks_by=[dict(name=p, n=sum(1 for r in c.rows("task") if r["status"] == p)) for p in s["lists"]["tstatus"]])

def finance(c, year, include_payroll=True):
    dc = c.comp("deal"); oc = c.comp("ownad"); pc = c.comp("payroll"); ac = c.comp("clientad"); rows = []
    for m in range(1, 13):
        inm = lambda d: d and (dd(d).year, dd(d).month) == (year, m)
        rev = sum(dc[d["code"]]["total"] for d in c.rows("deal") if inm(d["won_date"])); cash = sum(num(p["amount"]) for p in c.rows("payment") if inm(p["date"]))
        own = sum(oc[x["code"]]["spend_base"] for x in c.rows("ownad") if inm(x["date"]))
        pay = sum(pc[x["code"]]["net"] for x in c.rows("payroll") if inm(x["month"])) if include_payroll else 0
        oth = sum(num(x["amount"]) for x in c.rows("expense") if inm(x["date"]))
        cad = sum(ac[x["code"]]["spend_base"] or 0 for x in c.rows("clientad") if inm(x["month"]))
        rows.append(dict(month=f"{year}-{m:02d}", revenue=rev, cash=cash, own_ads=own, payroll=pay, other=oth, costs=own + pay + oth, net=cash - own - pay - oth, client_ads=cad))
    tot = {k: sum(r[k] for r in rows) for k in ("revenue", "cash", "own_ads", "payroll", "other", "costs", "net", "client_ads")}
    cats = [dict(name="Salaries (Payroll)", amount=tot["payroll"]), dict(name="Own ad spend", amount=tot["own_ads"])]
    for k in c.s["lists"]["xcat"]:
        cats.append(dict(name=k, amount=sum(num(x["amount"]) for x in c.rows("expense") if x["category"] == k and x["date"] and x["date"].year == year)))
    recv = [dict(code=r["code"], client=v["client"], service=r["service"], total=v["total"], paid=v["paid"], balance=v["balance"]) for r in c.rows("deal") for v in [dc[r["code"]]] if v["balance"] > 0]
    recv.sort(key=lambda x: -x["balance"])
    return dict(year=year, months=rows, totals=tot, costs=cats, receivables=recv[:25], receivable_total=sum(x["balance"] for x in recv),
        payroll_pending=sum(pc[x["code"]]["net"] for x in c.rows("payroll") if x["status"] == "Pending") if include_payroll else 0,
        advanced=sum(ac[a["code"]]["spend_base"] or 0 for a in c.rows("clientad") if a["paid_by"] == "Agency card (reimburse)" and a["reimbursed"] == "No"))

def today_queue(c):
    lc = c.comp("lead"); out = []
    for r in c.rows("lead"):
        st = lc[r["code"]]["fu_status"]
        if st in ("Respond now", "Overdue", "Due today"): out.append(dict(code=r["code"], name=r["name"], company=r["company"], phone=r["phone"], email=r["email"], service=r["service"], stage=r["stage"],
            status=st, next_followup=r["next_followup"].isoformat() if r["next_followup"] else None, last_contact=lc[r["code"]]["last_contact"], age=lc[r["code"]]["age"], owner=c.label("employee", r["owner"]) if r["owner"] else ""))
    order = {"Respond now": 0, "Overdue": 1, "Due today": 2}
    out.sort(key=lambda x: (order[x["status"]], x["next_followup"] or ""))
    return out
