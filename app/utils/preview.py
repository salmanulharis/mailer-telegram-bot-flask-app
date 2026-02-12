"""Build the email preview text shown to users."""


def build_preview(
    receiver: str,
    cc_list: list[str],
    subject: str,
    body: str,
) -> str:
    cc_text = (
        "\n".join(f"• {email}" for email in cc_list)
        if cc_list
        else "No CC recipients"
    )
    return (
        f"📧 **EMAIL PREVIEW** 📧\n\n"
        f"**To:** {receiver}\n"
        f"**CC:** {cc_text}\n"
        f"**Subject:** {subject}\n\n"
        f"**Message:**\n"
        f"─────────────────\n"
        f"{body}\n"
        f"─────────────────"
    )
