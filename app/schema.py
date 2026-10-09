"""Entity definitions (the 'sheets' of the CRM), picklists, and role permissions."""
from dataclasses import dataclass
import copy

@dataclass
class F:
    name: str; type: str; label: str; opt: str = None; ref: str = None
    default: object = None; wide: bool = False; req: bool = False; only: tuple = None

def C(key, label, fmt="text"): return dict(key=key, label=label, fmt=fmt)

ROLES = ["owner", "coo", "accounts", "team_lead", "member", "sales"]
ROLE_LABEL = {"owner": "Owner / CEO", "coo": "COO / Operations", "accounts": "Accounts", "team_lead": "Team Lead", "member": "Team Member", "sales": "Sales / BD"}
# order of letters: coo, accounts, team_lead, member, sales   (owner always edits)  e=edit v=view -=none
PERM = {"lead": "v---e", "followup": "v---e", "client": "evvve", "deal": "eev-e", "assignment": "e-ev-", "task": "e-ee-",
        "update": "eveev", "clientad": "eeee-", "payment": "ve---", "ownad": "ve---", "employee": "evv--", "payroll": "-e---",
        "expense": "ve---", "dashboard": "vv--v", "operations": "v-v--", "finance": "vv---", "client360": "vvvvv", "today": "v---v",
        "users": "-----", "settings": "-----", "audit": "-----", "billing": "-----"}

def can(role, res, need="v"):
    if role == "owner": return True
    p = PERM.get(res, "-----")
    ch = p[ROLES.index(role) - 1] if role in ROLES else "-"
    return ch == "e" if need == "e" else ch in "ve"

ENT = {}
ENT["lead"] = dict(label="Leads", one="Lead", prefix="L-", digits=4, sort="received_at", desc=True, title=["name"], sub=["company", "service"], board="stage",
 fields=[F("received_at","datetime","Received",default="now"),F("method","select","Contact method",opt="contact"),F("channel","select","Channel",opt="channels"),F("campaign","str","Campaign / UTM"),
  F("name","str","Name",req=True),F("company","str","Company"),F("email","str","Email"),F("phone","str","Phone / WhatsApp"),F("country","select","Country",opt="countries"),F("city","str","City"),
  F("service","select","Service wanted",opt="services"),F("wants","text","What the client wants",wide=True),F("budget_fc","float","Est. budget (foreign ccy)"),
  F("bok","select","Budget OK?",opt="yn"),F("dm","select","Decision maker?",opt="yn"),F("need","select","Real need?",opt="yn"),F("soon","select","Starts within 90 days?",opt="yn"),
  F("stage","select","Stage",opt="stages",default="New"),F("owner","ref","Owner",ref="employee"),F("first_response_at","datetime","First response"),F("call_booked","select","Call / meeting booked?",opt="yn"),
  F("proposal_fc","float","Proposal value (foreign ccy)"),F("next_followup","date","Next follow-up",default="today"),F("lost_reason","select","Lost reason",opt="lost"),F("notes","text","Notes",wide=True)],
 computed=[C("qual","Qualification","chip"),C("score","Score","int"),C("ptype","Paid / organic"),C("market","Market"),C("fu_status","Follow-up","chip"),C("sla","Response SLA","chip"),
  C("resp_hours","Response (h)","num"),C("last_contact","Last contact","date"),C("fu_count","Follow-ups","int"),C("age","Age (days)","int"),C("client_code","Client code")],
 cols=["name","company","service","channel","stage","c_qual","c_fu_status","next_followup","owner"])
ENT["followup"] = dict(label="Follow-ups", one="Follow-up", prefix="F-", digits=5, sort="at", desc=True, title=["lead_code"], sub=["chan", "outcome"],
 fields=[F("lead_code","ref","Lead",ref="lead",req=True),F("at","datetime","When",default="now"),F("chan","select","Channel used",opt="fchan"),F("direction","select","Direction",opt="direction"),
  F("summary","text","What was said / done",wide=True),F("outcome","select","Outcome",opt="outcome"),F("next_step","text","Next step",wide=True),F("by","ref","Done by",ref="employee")],
 computed=[C("lead","Lead")], cols=["lead_code","at","chan","outcome","next_step","by"])
ENT["client"] = dict(label="Clients", one="Client", prefix="C-", digits=4, sort="id", desc=True, title=["c_display"], sub=["status", "am"], board="status",
 fields=[F("lead_code","ref","From lead",ref="lead",req=True),F("since","date","Client since",default="today"),F("status","select","Status",opt="cstatus",default="Onboarding"),F("am","ref","Account manager",ref="employee"),
  F("health","select","Health",opt="health",default="Green"),F("next_review","date","Next review"),F("contract_end","date","Contract / renewal date"),F("rating","select","Satisfaction (1-5)",opt="rating"),F("notes","text","Notes",wide=True)],
 computed=[C("display","Client"),C("company","Company"),C("email","Email"),C("phone","Phone"),C("country","Country"),C("channel","Acquired via"),C("deals","Deals","int"),C("contract","Contract value","money"),C("paid","Paid","money"),
  C("balance","Balance","money"),C("budget_m","Ad budget (month)","money"),C("spend_m","Ad spend (month)","money"),C("last_update","Last update","date"),C("days_update","Days since update","int"),C("update_status","Update status","chip"),
  C("team","Team size","int"),C("open_tasks","Open tasks","int"),C("overdue_tasks","Overdue tasks","int"),C("direct_costs","Direct costs","money"),C("margin","Collected − direct costs","money")],
 cols=["c_display","status","health","am","c_contract","c_balance","c_update_status","c_open_tasks","c_team"])
ENT["deal"] = dict(label="Deals", one="Deal", prefix="D-", digits=4, sort="id", desc=True, title=["service"], sub=["c_client", "pstatus"], board="pstatus",
 fields=[F("client_code","ref","Client",ref="client",req=True),F("service","select","Service sold",opt="services",req=True),F("won_date","date","Won date",default="today"),F("dtype","select","Deal type",opt="dtype"),
  F("price_fc","float","Package price (foreign ccy)",req=True),F("charge_pct","float","Service charge % (blank = current default)"),F("rate","float","Rate to base ccy (blank = current default)"),
  F("pstatus","select","Project status",opt="pstat",default="Not started"),F("start_date","date","Start date"),F("due_date","date","Due date"),F("notes","text","Notes",wide=True)],
 computed=[C("lead_code","Lead"),C("client","Client"),C("country","Country"),C("channel","Channel"),C("charge_used","Charge used %","num"),C("rate_used","Rate used","num"),C("total_fc","Total (foreign)","money"),C("total","Total payable","money"),
  C("paid","Paid","money"),C("balance","Balance","money"),C("paid_pct","Paid %","pct"),C("pay_status","Payment","chip"),C("alert","Delivery","chip"),C("project_lead","Project lead"),C("team","Team size","int")],
 cols=["service","c_client","won_date","c_total","c_paid","c_balance","c_pay_status","pstatus","c_alert","c_project_lead"])
ENT["assignment"] = dict(label="Assignments", one="Assignment", prefix="A-", digits=4, sort="id", desc=True, title=["c_emp_name"], sub=["c_client", "prole"],
 fields=[F("deal_code","ref","Deal",ref="deal",req=True),F("employee","ref","Employee",ref="employee",req=True),F("prole","select","Role on project",opt="arole",default="Team Member"),
  F("alloc","float","Time allocation %"),F("start_date","date","Start"),F("end_date","date","End"),F("status","select","Status",opt="astatus",default="Active"),F("notes","text","Notes",wide=True)],
 computed=[C("client_code","Client code"),C("client","Client"),C("service","Service"),C("emp_name","Employee"),C("emp_role","Company role")],
 cols=["c_emp_name","c_emp_role","prole","deal_code","c_client","c_service","alloc","status"])
ENT["task"] = dict(label="Tasks", one="Task", prefix="T-", digits=4, sort="due", desc=False, title=["title"], sub=["c_client", "assignee"], board="status",
 fields=[F("client_code","ref","Client",ref="client",req=True),F("deal_code","ref","Deal (optional)",ref="deal"),F("title","str","Task",req=True,wide=True),F("assignee","ref","Assigned to",ref="employee"),
  F("priority","select","Priority",opt="prio",default="Medium"),F("status","select","Status",opt="tstatus",default="To do"),F("created","date","Created",default="today"),F("due","date","Due date"),
  F("done_on","date","Completed on"),F("est_hours","float","Est. hours"),F("act_hours","float","Actual hours"),F("notes","text","Notes",wide=True)],
 computed=[C("client","Client"),C("flag","Flag","chip"),C("days_late","Days late","int")], cols=["title","c_client","assignee","priority","status","due","c_flag"])
ENT["update"] = dict(label="Client updates", one="Update", prefix="U-", digits=4, sort="at", desc=True, title=["c_client"], sub=["utype", "sentiment"],
 fields=[F("client_code","ref","Client",ref="client",req=True),F("at","datetime","When",default="now"),F("utype","select","Type",opt="utype"),F("summary","text","What was done / reported",wide=True),
  F("results","text","Results / key numbers",wide=True),F("next_steps","text","Next steps",wide=True),F("sentiment","select","Client sentiment",opt="sentiment"),F("by","ref","Reported by",ref="employee"),
  F("sent","select","Report sent to client?",opt="yn"),F("link","str","Report / doc link")],
 computed=[C("client","Client")], cols=["c_client","at","utype","summary","sentiment","by","sent"])
ENT["clientad"] = dict(label="Client ads", one="Client ad line", prefix="B-", digits=4, sort="month", desc=True, title=["c_client"], sub=["platform", "campaign"],
 fields=[F("client_code","ref","Client",ref="client",req=True),F("month","date","Month",default="today"),F("platform","select","Platform",opt="paid_channels"),F("campaign","str","Campaign"),
  F("currency","select","Currency",opt="curr"),F("budget","float","Approved budget"),F("spend","float","Spent so far"),F("paid_by","select","Paid by",opt="paidby"),F("reimbursed","select","Reimbursed?",opt="reimb"),
  F("impressions","int","Impressions"),F("clicks","int","Clicks"),F("results","int","Results (leads / sales)"),F("revenue","float","Client revenue from ads"),F("notes","text","Notes",wide=True)],
 computed=[C("client","Client"),C("budget_base","Budget (base)","money"),C("spend_base","Spend (base)","money"),C("used","Used %","pct"),C("flag","Budget flag","chip"),C("cpr","Cost / result","money"),C("roas","Client ROAS","num")],
 cols=["c_client","month","platform","campaign","c_budget_base","c_spend_base","c_used","c_flag","results"])
ENT["payment"] = dict(label="Payments", one="Payment", prefix="P-", digits=4, sort="date", desc=True, title=["c_client"], sub=["method", "ref"],
 fields=[F("deal_code","ref","Deal",ref="deal",req=True),F("date","date","Date received",default="today"),F("amount","float","Amount received (base ccy)",req=True),F("method","select","Method",opt="paym"),F("ref","str","Transaction / ref no."),F("notes","text","Notes",wide=True)],
 computed=[C("client_code","Client code"),C("client","Client"),C("service","Service"),C("rate","Rate","num"),C("amount_fc","≈ Foreign ccy","money")],
 cols=["date","c_client","c_service","deal_code","amount","method","ref"])
ENT["ownad"] = dict(label="Own ad spend", one="Ad spend", prefix="O-", digits=4, sort="date", desc=True, title=["platform"], sub=["campaign", "service"],
 fields=[F("date","date","Date",default="today"),F("platform","select","Platform",opt="paid_channels"),F("campaign","str","Campaign"),F("service","select","Service promoted",opt="services"),F("amount","float","Amount spent",req=True),
  F("currency","select","Currency",opt="curr"),F("impressions","int","Impressions"),F("clicks","int","Clicks"),F("results","int","Results (leads)"),F("notes","text","Notes",wide=True)],
 computed=[C("spend_base","Spend (base)","money"),C("ctr","CTR","pct"),C("cpc","CPC","num"),C("cpr","Cost / result","money")], cols=["date","platform","campaign","service","c_spend_base","clicks","results","c_cpr"])
ENT["employee"] = dict(label="Team", one="Employee", prefix="E-", digits=3, sort="name", desc=False, title=["name"], sub=["role", "dept"],
 fields=[F("name","str","Full name",req=True),F("role","select","Job role",opt="erole"),F("dept","select","Department",opt="depts"),F("reports_to","ref","Reports to",ref="employee"),F("phone","str","Phone"),F("email","str","Email"),
  F("join_date","date","Join date"),F("etype","select","Employment type",opt="etype"),F("status","select","Status",opt="estatus",default="Active"),F("salary","float","Monthly salary (base ccy)",only=("owner","accounts")),
  F("skills","text","Skills / services",wide=True),F("notes","text","Notes",wide=True)],
 computed=[C("alloc","Allocated %","pct"),C("assigns","Active assignments","int"),C("clients_am","Clients as account mgr","int"),C("open_tasks","Open tasks","int"),C("overdue","Overdue tasks","int"),C("util","Workload","chip")],
 cols=["name","role","dept","status","c_alloc","c_util","c_clients_am","c_open_tasks","c_overdue"])
ENT["payroll"] = dict(label="Payroll", one="Salary", prefix="PR-", digits=4, sort="month", desc=True, title=["c_emp_name"], sub=["status"],
 fields=[F("month","date","Salary month",default="today"),F("employee","ref","Employee",ref="employee",req=True),F("base_override","float","Base override (optional)"),F("bonus","float","Bonus"),F("deductions","float","Deductions"),
  F("paid_on","date","Paid on"),F("method","select","Method",opt="paym"),F("status","select","Status",opt="pay_status",default="Pending"),F("notes","text","Notes",wide=True)],
 computed=[C("emp_name","Employee"),C("emp_role","Role"),C("base","Base","money"),C("net","Net pay","money")], cols=["month","c_emp_name","c_emp_role","c_base","bonus","deductions","c_net","status"])
ENT["expense"] = dict(label="Expenses", one="Expense", prefix="X-", digits=4, sort="date", desc=True, title=["category"], sub=["paid_to"],
 fields=[F("date","date","Date",default="today"),F("category","select","Category",opt="xcat"),F("paid_to","str","Paid to"),F("description","text","Description",wide=True),F("amount","float","Amount (base ccy)",req=True),
  F("method","select","Method",opt="paym"),F("client_code","ref","Client (if for a client)",ref="client"),F("notes","text","Notes",wide=True)],
 computed=[C("client","Client")], cols=["date","category","paid_to","description","amount","c_client"])

AGENCY_SERVICES = ["Web Development","App Development","UI/UX Design","Graphic Design","E-commerce Solutions","Video Editing","Content Writing","Landing Page Design","Digital Marketing","SEO Services",
 "Google Ads & Bing Ads","Meta Ads","Social Media Management","Web Analytics","CRO - Conversion Optimization","Email Marketing","Legal Data Entry & Data Analysis","GoHighLevel Migration & Automation",
 "Zoho Setup & Automation","CRM Data Management & Automation","Lead Generation","Web Research","Microsoft Excel Cleaning & Formatting","Data Collecting from Social Media","Multiple Services / Not Sure"]
GENERAL_SERVICES = ["Consulting", "Project work", "Retainer / support", "Training", "Products", "Other"]
COUNTRIES = ["Bangladesh","United States","United Kingdom","Germany","Canada","Australia","United Arab Emirates","Saudi Arabia","Qatar","Kuwait","Bahrain","Oman","Jordan","Lebanon","Brazil","Mexico","Colombia","Argentina","Chile","Peru","France","Netherlands","Italy","Spain","Sweden","Norway","Denmark","Finland","Poland","Switzerland","Austria","Belgium","Portugal","Greece","Turkey","Romania","Ireland","India","Singapore","Japan","South Korea","China","New Zealand","Thailand","Malaysia","Indonesia","Philippines","Vietnam","Pakistan","Sri Lanka","Nepal","Maldives","South Africa","Nigeria","Kenya","Egypt","Other"]
EDITABLE_LISTS = ["services","channels","paid_channels","contact","lost","fchan","outcome","paym","xcat","depts","erole","utype","etype","countries"]

def default_lists(template="agency"):
    return {"services": list(AGENCY_SERVICES if template == "agency" else GENERAL_SERVICES),
     "channels": ["Meta Ads","Google Ads","Bing Ads","LinkedIn Ads","TikTok Ads","Other Paid","Organic Search (SEO)","Direct / Website","Referral","Social Organic","Upwork","Fiverr","Cold Outreach","Other"],
     "paid_channels": ["Meta Ads","Google Ads","Bing Ads","LinkedIn Ads","TikTok Ads","Other Paid"],
     "contact": ["Website Form","WhatsApp","Calendly Booking","Email","Phone Call","Social DM","Live Chat","Other"],
     "stages": ["New","Contacted","Qualified","Discovery Call Booked","Proposal Sent","Negotiation","Won","Lost","Nurture (Later)"],
     "lost": ["Budget too low","Went with a competitor","No response / ghosted","Not a fit / out of scope","Timing not right","Spam / fake lead","Other"],
     "fchan": ["WhatsApp","Email","Phone Call","Calendly Meeting","Google Meet / Zoom","Facebook DM","Instagram DM","LinkedIn DM","SMS","Other"],
     "direction": ["Outbound (we reached out)","Inbound (they reached out)"],
     "outcome": ["No answer","Replied","Interested","Meeting booked","Proposal requested","Negotiating","Won","Not interested","Wrong number / spam"],
     "paym": ["bKash","Nagad","Rocket","Bank Transfer","Wise","Payoneer","PayPal","Stripe","Card","Cash","Other"],
     "pstat": ["Not started","In progress","Waiting on client","Delivered","On hold","Cancelled"], "dtype": ["One-time project","Monthly retainer"],
     "erole": ["CEO","COO","Accounts Manager","Accountant","Team Lead","Team Member","Sales / BD Executive","Client Success Manager","HR / Admin","Intern","Other"],
     "depts": ["Management","Accounts & Finance","Sales & Business Development","Client Success","Web Development","App Development","UI/UX & Graphic Design","SEO & Content","Paid Ads","Video & Creative","Data & CRM","Admin & HR"] if template == "agency" else ["Management","Accounts & Finance","Sales","Operations","Support","Admin & HR"],
     "etype": ["Full-time","Part-time","Contract","Freelancer","Intern"], "estatus": ["Active","On leave","Resigned","Terminated"],
     "cstatus": ["Onboarding","Active","Paused","Completed","Churned"], "health": ["Green","Amber","Red"],
     "arole": ["Project Lead","Team Lead","Account Manager","Team Member","Specialist","QA / Reviewer"], "astatus": ["Active","Completed","Removed"],
     "prio": ["Low","Medium","High","Urgent"], "tstatus": ["To do","In progress","In review","Blocked","Done"],
     "utype": ["Weekly report","Monthly report","Call / Meeting","WhatsApp update","Milestone delivered","Issue / Risk","Approval received","Invoice sent","Other"],
     "sentiment": ["Happy","Neutral","At risk"],
     "xcat": ["Software & Tools","Hosting & Domains","Rent & Utilities","Freelancer / Contractor","Marketing & Branding","Tax & Legal","Equipment","Bank & Gateway Fees","Training","Travel","Office & Admin","Other"],
     "paidby": ["Client direct","Agency card (reimburse)"], "reimb": ["Yes","No","N/A"], "rating": ["1","2","3","4","5"], "pay_status": ["Paid","Pending"],
     "yn": ["Yes","No"], "curr": ["BDT","USD"], "countries": list(COUNTRIES)}

DEFAULT_SETTINGS = dict(currency_base="BDT", currency_foreign="USD", rate=150.0, card_rate=150.0, default_charge=0.0, qualified_score=75, warm_score=50,
    sla_hours=2.0, monthly_target=0.0, update_days=7, budget_alert=90.0, busy_alloc=80.0, home_country="Bangladesh", tz_offset=6.0, template="agency")

def merged_settings(stored):
    s = copy.deepcopy(DEFAULT_SETTINGS)
    s["lists"] = default_lists((stored or {}).get("template", "agency"))
    for k, v in (stored or {}).items():
        if k == "lists":
            for lk, lv in v.items():
                if lk in EDITABLE_LISTS and isinstance(lv, list): s["lists"][lk] = [str(x).strip() for x in lv if str(x).strip()]
        elif k in s: s[k] = v
    s["lists"]["curr"] = [s["currency_base"], s["currency_foreign"]]
    return s

def public_entities():
    out = {}
    for k, e in ENT.items():
        out[k] = dict(label=e["label"], one=e["one"], title=e["title"], sub=e["sub"], cols=e["cols"], board=e.get("board"), sort=e["sort"], desc=e["desc"],
            fields=[dict(name=f.name, type=f.type, label=f.label, opt=f.opt, ref=f.ref, default=f.default, wide=f.wide, req=f.req, only=f.only) for f in e["fields"]], computed=e["computed"])
    return out
