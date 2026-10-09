import smtplib, logging
from email.message import EmailMessage
from .config import settings
log = logging.getLogger("ritsone")

def send_mail(to, subject, body):
    if not settings.SMTP_HOST:
        log.warning("SMTP not configured. Mail to %s: %s\n%s", to, subject, body); return False
    m = EmailMessage(); m["From"], m["To"], m["Subject"] = settings.SMTP_FROM, to, subject; m.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as s:
            s.starttls()
            if settings.SMTP_USER: s.login(settings.SMTP_USER, settings.SMTP_PASS)
            s.send_message(m)
        return True
    except Exception as e:
        log.error("Mail failed: %s", e); return False
