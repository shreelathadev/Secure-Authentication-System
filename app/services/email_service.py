import smtplib, secrets
from email.mime.text import MIMEText
from app.core.config import settings

def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"

def send_email(to: str, subject: str, body: str):
    # Dev fallback: no SMTP configured -> print to console instead of failing
    if not settings.MAIL_USERNAME:
        print(f"\n--- DEV EMAIL (no SMTP configured) ---\nTo: {to}\nSubject: {subject}\n{body}\n---\n")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(settings.MAIL_FROM, [to], msg.as_string())