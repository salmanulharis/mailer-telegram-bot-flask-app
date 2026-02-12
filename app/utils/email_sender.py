"""SMTP email sending utility."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD


def send_email(
    receiver: str,
    subject: str,
    body: str,
    cc_list: list[str] | None = None,
) -> None:
    """Send a plain-text email via Gmail SMTP.

    Raises:
        Exception: propagates any SMTP / auth error to the caller.
    """
    if cc_list is None:
        cc_list = []

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg["Subject"] = subject
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        recipients = [receiver] + cc_list
        server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
