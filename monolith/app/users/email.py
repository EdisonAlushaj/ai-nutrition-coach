import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("uvicorn.error")

FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL", "http://localhost:3000/reset-password")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@ai-nutrition-coach.local")


def build_reset_link(token: str) -> str:
    separator = "&" if "?" in FRONTEND_RESET_URL else "?"
    return f"{FRONTEND_RESET_URL}{separator}token={token}"


def send_password_reset_email(to_email: str, token: str) -> None:
    reset_link = build_reset_link(token)
    subject = "Reset your AI Nutrition Coach password"
    body = (
        "You requested a password reset.\n\n"
        f"Reset your password using this link (valid for 1 hour):\n{reset_link}\n\n"
        "If you did not request this, you can ignore this email."
    )

    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = FROM_EMAIL
        message["To"] = to_email
        message.set_content(body)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        logger.info("Password reset email sent to %s", to_email)
        return

    logger.warning(
        "Password reset requested for %s. SMTP not configured; reset link: %s",
        to_email,
        reset_link,
    )
