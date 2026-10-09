# RITS One

All-in-one business software (web + installable mobile app) built for Rafirit Station and sellable to any service business by subscription.
Leads → follow-ups → clients → deals → team assignments → tasks → client reports → ad budgets → payments → payroll → finance, with live dashboards.

**Stack:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL (SQLite for local), vanilla-JS PWA (no build step), Docker + Caddy (automatic HTTPS).

## What customers get
- Sign up → 14-day free trial → pick a plan. Every business is a separate, isolated workspace.
- 6 roles: Owner/CEO, COO, Accounts, Team Lead, Team Member, Sales/BD (permissions in *Logins & access → Roles & access*).
- Mobile-first screens, installable on phone like an app (PWA), dark mode, CSV export, activity log.
- Codes everywhere: Lead `L-0001`, Client `C-0001`, Deal `D-0001`, Task `T-0001`, Employee `E-001`...

## What you get (platform owner)
- **Admin** screen (login with your SUPERADMIN account): all businesses, extend trials, suspend, change plan, approve bKash/Nagad/bank payments, edit plan prices and limits, reset an owner's password.
- Subscription lock: when a trial or plan expires, that business becomes read-only until you approve a payment.

---
## A. Try it on your computer (10 minutes, optional)
```bash
cd rits-one
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
SUPERADMIN_EMAIL=you@example.com SUPERADMIN_PASSWORD='ChangeMe12345' uvicorn app.main:app --reload
```
Open http://localhost:8000 → *Start your free trial*. Run the tests: `python tests/test_smoke.py`.

## B. Put it online (about 45 minutes)
1. **Buy** a small VPS (2 GB RAM, Ubuntu 24.04; Hetzner, DigitalOcean, Vultr or any provider) and a domain.
2. **DNS:** add an `A` record, e.g. `app.yourdomain.com` → your server IP. Wait a few minutes.
3. **Connect:** `ssh root@YOUR_SERVER_IP`, then install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable
   ```
4. **Upload** the `rits-one` folder to the server (from your computer: `scp -r rits-one root@YOUR_SERVER_IP:/opt/`), then `cd /opt/rits-one`.
5. **Configure:** `cp .env.example .env` and edit it (`nano .env`):
   - `DOMAIN` = your domain, e.g. `app.yourdomain.com`
   - `POSTGRES_PASSWORD` = a long random password
   - `SECRET_KEY` = output of `openssl rand -hex 32` (**required**, the app refuses to start without it)
   - `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` = your platform-admin login
   - `PAY_INSTRUCTIONS` = your bKash/Nagad number text shown on the Billing page
6. **Start:** `docker compose up -d --build`. HTTPS is issued automatically. Check: `curl https://app.yourdomain.com/health`.
7. **First login:** open the site → *Start your free trial* and create **Rafirit Station** as your own business. Sign out, sign in with the SUPERADMIN email → **Admin** menu.
8. **Prices:** *Admin → Plans*. The prices (৳999 / ৳2,499 / ৳4,999 per month) and limits are **placeholders**; set your own.
9. **Backups:** `crontab -e` and add: `0 2 * * * /opt/rits-one/scripts/backup.sh >> /opt/rits-one/backups/backup.log 2>&1`. Copy the `backups/` folder off the server regularly.
10. **Update later:** upload the new files, then `docker compose up -d --build`. Logs: `docker compose logs -f app`.

## C. Taking subscription payments
**bKash / Nagad / bank (works out of the box):** customer opens *Billing → Pay*, sends money to your number, submits the transaction ID. You verify it in your bKash/Nagad app, then *Admin → Payments → Approve*. Their plan activates instantly for the period paid. Duplicate transaction IDs are rejected.

**Card payments (optional, Stripe):** create one Product per plan with a monthly and a yearly Price in Stripe → paste the Price IDs in *Admin → Plans* → set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in `.env` → in Stripe add a webhook to `https://YOUR_DOMAIN/api/billing/webhook` with events `checkout.session.completed`, `invoice.paid`, `customer.subscription.deleted` → `docker compose up -d`. The Stripe code was written to Stripe's documented API but **has not been run against a live Stripe account**: test it in Stripe test mode first. Stripe availability depends on where your business is registered; other gateways (SSLCommerz, etc.) are not included.

**Email (optional):** fill `SMTP_*` in `.env` so "Forgot password" emails work. Without it, owners ask you to reset (*Admin → Businesses → Reset owner pw*), and owners reset their own staff in *Logins & access*.

## D. Mobile app
- **Installable app (included):** customers open your site on their phone → Android Chrome: menu → *Install app*; iPhone Safari: Share → *Add to Home Screen*. It opens full-screen with your icon. There is an in-app *Install* button with these instructions.
- **Play Store / App Store (optional later):** the same site can be wrapped. Android: upload your URL to https://www.pwabuilder.com and download the Android package (needs a Google Play developer account, one-time fee). iPhone: wrap with Capacitor (`npm i @capacitor/core @capacitor/cli`, `npx cap init`, point `server.url` to your domain, `npx cap add ios`) and publish via Xcode (needs a Mac and an Apple developer account, yearly fee). Apple may reject apps that are only a website wrapper, so keep the PWA as the main route.

## E. Security checklist (already in the code unless marked)
Passwords hashed with bcrypt · session in HttpOnly cookie · CSRF header check on every change · strict Content-Security-Policy · login/signup/forgot rate limits · every query filtered by business ID (tested) · roles enforced on the server · deletes blocked when records are still linked · activity log.
**You must:** keep `.env` private, use a long `SECRET_KEY`, keep the server updated (`apt upgrade`), copy backups off-server. *Salaries:* only Owner and Accounts can see them.

## F. Honest limits (read before selling)
- Tested end-to-end on SQLite (automated tests + simulated browser run). **PostgreSQL (used by Docker) has not been run here**; run `TEST_DATABASE_URL=postgresql://... python tests/test_smoke.py` once on your server before going live.
- Built for small and mid-size businesses: lists load whole tables per business (fine into the tens of thousands of rows). Login rate limits are per server process.
- Not included yet: importing your old Google Sheet (CSV import), automatic reminder emails/WhatsApp, database migrations tool (add Alembic before changing the data model on live customers), automatic tax invoices, a real-device test pass on iPhone/Android (UI was checked in a simulated browser only).

## G. Where things are
`app/schema.py` records, fields, dropdown defaults, role permissions (add a field here and it appears in forms, tables, API and CSV) · `app/compute.py` all formulas and dashboards · `app/routes_*.py` API · `app/billing.py` plans and subscription rules · `static/app.js` + `app.css` the whole interface · `tests/test_smoke.py` automated tests.
