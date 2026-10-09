import os

def _b(name, default="0"):
    return os.getenv(name, default).lower() in ("1", "true", "yes")

class Settings:
    APP_NAME = "RITS One"
    ENV = os.getenv("ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ritsone.db")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "14"))
    SUPERADMIN_EMAIL = os.getenv("SUPERADMIN_EMAIL", "").strip().lower()
    SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "")
    COOKIE_SECURE = _b("COOKIE_SECURE", "1" if os.getenv("ENV") == "production" else "0")
    ALLOW_SIGNUP = _b("ALLOW_SIGNUP", "1")
    # Manual payments (bKash / Nagad / bank): text shown on the Billing page
    PAY_INSTRUCTIONS = os.getenv("PAY_INSTRUCTIONS", "Send the amount by bKash/Nagad (Personal) to 01XXXXXXXXX, then submit the transaction ID below.")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "RITS One <no-reply@example.com>")

settings = Settings()
if settings.ENV == "production" and settings.SECRET_KEY == "dev-only-change-me":
    raise RuntimeError("Set a strong SECRET_KEY in production (see .env.example).")
