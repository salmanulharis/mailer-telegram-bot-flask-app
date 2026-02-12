import json
import os
from dotenv import load_dotenv

load_dotenv()

# ── Core credentials ─────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

# ── Webhook ───────────────────────────────────────────────────────────────────
# A random secret token that forms part of the webhook URL, e.g.:
#   https://yourdomain.com/webhook/<WEBHOOK_SECRET>
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "supersecrettoken")
WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "")   # e.g. https://yourdomain.com

# ── Receiver groups ───────────────────────────────────────────────────────────
_default_groups = {
    "hr_managers": {
        "name": "👥 HR + Managers",
        "receiver": "hr@acodez.in",
        "cc": [
            "jamsheer.k@acodez.in",
            "sanjay.shankar@acodez.in",
            "sanesh.p@acodez.in",
        ],
    },
    "hr": {
        "name": "🤝 HR",
        "receiver": "hr@acodez.in",
        "cc": [],
    },
    "testing": {
        "name": "🧪 Testing Team",
        "receiver": "salmanulharrish.sh@gmail.com",
        "cc": [
            "salmanul.haris@acodez.co.in",
            "salmanul.haris+1@acodez.co.in",
        ],
    },
}

try:
    RECEIVER_GROUPS: dict = json.loads(os.getenv("RECEIVER_GROUPS", "{}")) or _default_groups
except json.JSONDecodeError:
    print("Warning: Invalid RECEIVER_GROUPS in .env — using defaults")
    RECEIVER_GROUPS = _default_groups

# ── Preset messages ───────────────────────────────────────────────────────────
PRESET_MESSAGES: dict = {
    "leave_request": {
        "subject": "Leave Request",
        "body": (
            "Hi,\n\n"
            "I am writing to request leave on [dates][reason].\n\n"
            "Please let me know if you require any further details from my end.\n\n"
            "Thank you for your understanding.\n\n"
            "Best regards,\n"
            "Salmanul Haris"
        ),
    },
    "wfh": {
        "subject": "Work From Home Request",
        "body": (
            "Hi,\n\n"
            "I am writing to request to work from home on [dates][reason].\n\n"
            "I will be fully available online and will ensure all my tasks are completed as scheduled.\n\n"
            "Thank you for your understanding.\n\n"
            "Best regards,\n"
            "Salmanul Haris"
        ),
    },
    "half_day": {
        "subject": "Half Day Leave Request",
        "body": (
            "Hi,\n\n"
            "I am writing to request a half day leave on [date][reason].\n\n"
            "I will ensure all my tasks are completed before or after the leave period.\n\n"
            "Thank you for your understanding.\n\n"
            "Best regards,\n"
            "Salmanul Haris"
        ),
    },
    "half_day_leave_wfh": {
        "subject": "Half Day Leave + Work From Home Request",
        "body": (
            "Hi,\n\n"
            "I am writing to request a half day leave on [date] and work from home for the rest of the day[reason].\n\n"
            "I will be fully available online and will ensure all my tasks are completed as scheduled.\n\n"
            "Thank you for your understanding.\n\n"
            "Best regards,\n"
            "Salmanul Haris"
        ),
    },
}

# Preset keys that need date input
DATE_REQUIRING_PRESETS = {"leave_request", "wfh", "half_day", "half_day_leave_wfh"}

# ── Validation ────────────────────────────────────────────────────────────────
def validate_config() -> list[str]:
    """Return list of missing required config keys."""
    missing = []
    if not BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not EMAIL_ADDRESS:
        missing.append("EMAIL_ADDRESS")
    if not EMAIL_PASSWORD:
        missing.append("EMAIL_PASSWORD")
    return missing
