"""Optional SMTP alerts for high-risk transaction assessments.

Configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD and ALERT_FROM
in your environment to enable delivery. Without configuration, the application
continues safely and records the event in its application log.
"""

import logging
import os
import smtplib
from email.message import EmailMessage


LOGGER = logging.getLogger(__name__)


def _deliver(recipient: str, subject: str, body: str) -> bool:
    """Send a message only when the application's SMTP environment is set."""
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("ALERT_FROM")
    if not host or not sender:
        LOGGER.info("Email prepared for %s but SMTP is not configured.", recipient)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as server:
            server.starttls()
            username = os.getenv("SMTP_USERNAME")
            password = os.getenv("SMTP_PASSWORD")
            if username and password:
                server.login(username, password)
            server.send_message(message)
        LOGGER.info("Email sent to %s", recipient)
        return True
    except (OSError, smtplib.SMTPException) as error:
        LOGGER.warning("Email could not be sent: %s", error)
        return False


def send_welcome_email(recipient: str, name: str) -> bool:
    return _deliver(
        recipient,
        "Welcome to SecureSpend",
        f"Hello {name},\n\nYour SecureSpend workspace has been created successfully. "
        "You can now sign in and analyze transactions.\n\n"
        "This is an educational portfolio application, not a live banking service.",
    )


def send_risk_alert(recipient: str, name: str, merchant: str, amount: float, risk_score: int) -> bool:
    return _deliver(
        recipient,
        "Action recommended: high-risk transaction detected",
        f"Hello {name},\n\nSecureSpend flagged a transaction for review.\n\n"
        f"Merchant: {merchant}\nAmount: INR {amount:,.2f}\nRisk score: {risk_score}/100\n\n"
        "Open your SecureSpend workspace to review the assessment.\n\n"
        "This is an educational portfolio application, not a live banking alert.",
    )
