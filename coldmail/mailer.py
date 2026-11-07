import os
import smtplib
from email.message import EmailMessage

def send_approved_email(to_email, subject, body):
    """Send one message only after explicit approval in the app."""
    if os.getenv("ENABLE_EMAIL_SENDING", "false").lower() != "true":
        raise RuntimeError("Sending is disabled. Set ENABLE_EMAIL_SENDING=true to enable.")
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing SMTP settings: " + ", ".join(missing))
    msg = EmailMessage()
    msg["From"] = f'{os.getenv("SMTP_FROM_NAME", "ColdMail Pro")} <{os.environ["SMTP_FROM_EMAIL"]}>'
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"]), timeout=20) as server:
        if os.getenv("SMTP_USE_TLS", "true").lower() == "true":
            server.starttls()
        server.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        server.send_message(msg)
    return True
