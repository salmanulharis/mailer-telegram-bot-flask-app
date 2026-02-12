"""Fill in date/reason placeholders in preset message bodies."""
from app.config import PRESET_MESSAGES


def build_preset_body(preset_key: str, user_data: dict) -> str:
    """Return the preset body with all placeholders replaced."""
    preset = PRESET_MESSAGES[preset_key]
    body: str = preset["body"]

    date_start: str = user_data.get("date_start", "")
    date_end: str = user_data.get("date_end", "")
    date_single: str = user_data.get("date_single", "")
    reason: str = user_data.get("leave_reason", "")

    # ── Date substitution ─────────────────────────────────────────────────────
    if preset_key in ("leave_request", "wfh"):
        if date_end:
            body = body.replace("[dates]", f"{date_start} to {date_end}")
        else:
            body = body.replace("[dates]", date_single)
    elif preset_key in ("half_day", "half_day_leave_wfh"):
        body = body.replace("[date]", date_single)

    # ── Reason substitution ───────────────────────────────────────────────────
    if reason:
        # Insert with a leading separator for readability
        body = body.replace("[reason]", f" due to {reason}")
    else:
        body = body.replace(" [reason]", "").replace("[reason]", "")

    return body
