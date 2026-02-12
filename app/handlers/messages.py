"""Telegram text message handler — manages the multi-step conversation flow."""
from telegram import Update
from telegram.ext import ContextTypes

from app.config import PRESET_MESSAGES, DATE_REQUIRING_PRESETS
from app.utils.keyboards import (
    home_keyboard,
    cc_options_keyboard,
    preview_keyboard,
    reason_keyboard,
)
from app.utils.preview import build_preview
from app.utils.preset_builder import build_preset_body


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _send_preview(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    receiver = context.user_data.get("receiver_email", "Not set")
    cc_list = context.user_data.get("cc_recipients", [])
    subject = context.user_data.get("email_subject", "No subject")
    body = context.user_data.get("email_body", "No body")

    await message.reply_text(
        text=build_preview(receiver, cc_list, subject, body),
        reply_markup=preview_keyboard(),
        parse_mode="Markdown",
    )


async def _ask_for_reason(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    await message.reply_text(
        text=(
            "📋 **Add a reason (optional):**\n\n"
            "Choose 'Personal Reasons', enter a custom reason, or skip."
        ),
        reply_markup=reason_keyboard(),
        parse_mode="Markdown",
    )


# ── Main handler ──────────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route incoming text messages based on the current conversation state."""
    message = update.message
    text = message.text
    text_lower = text.lower().strip()

    # ── Greeting — restart bot ────────────────────────────────────────────────
    if text_lower in ("hi", "hello", "hey", "start"):
        context.user_data.clear()
        await message.reply_text(
            "Welcome to Email Bot! 📧\n\nChoose an option below:",
            reply_markup=home_keyboard(),
        )
        return

    waiting = context.user_data.get("waiting_for")

    # ── Receiver email ────────────────────────────────────────────────────────
    if waiting == "receiver_email":
        context.user_data["receiver_email"] = text.strip()
        context.user_data["waiting_for"] = None
        await message.reply_text(
            f"✅ Receiver: {text.strip()}\n\nDo you want to add CC recipients?",
            reply_markup=cc_options_keyboard(has_cc=False),
        )

    # ── CC email ──────────────────────────────────────────────────────────────
    elif waiting == "cc_email":
        cc = context.user_data.setdefault("cc_recipients", [])
        cc.append(text.strip())
        cc_list_text = "\n".join(f"• {e}" for e in cc)
        context.user_data["waiting_for"] = None
        await message.reply_text(
            f"✅ CC Added!\n\nCurrent CC List:\n{cc_list_text}\n\nWhat would you like to do?",
            reply_markup=cc_options_keyboard(has_cc=True),
        )

    # ── Custom subject ────────────────────────────────────────────────────────
    elif waiting == "custom_subject":
        context.user_data["email_subject"] = text
        context.user_data["waiting_for"] = "custom_body"
        await message.reply_text(f"✅ Subject: {text}\n\n📝 Now please type the message body:")

    # ── Custom body ───────────────────────────────────────────────────────────
    elif waiting == "custom_body":
        context.user_data["email_body"] = text
        context.user_data["waiting_for"] = None
        await _send_preview(message, context)

    # ── Date range start ──────────────────────────────────────────────────────
    elif waiting == "date_range_start":
        context.user_data["date_start"] = text.strip()
        context.user_data["waiting_for"] = "date_range_end"
        await message.reply_text(
            "📅 Now enter end date (format: YYYY-MM-DD or DD/MM/YYYY):\nExample: 2026-02-20"
        )

    # ── Date range end ────────────────────────────────────────────────────────
    elif waiting == "date_range_end":
        context.user_data["date_end"] = text.strip()
        context.user_data["waiting_for"] = None
        if context.user_data.get("selected_preset") in DATE_REQUIRING_PRESETS:
            await _ask_for_reason(message, context)
        else:
            await _finish_preset(message, context)

    # ── Single date ───────────────────────────────────────────────────────────
    elif waiting == "date_single":
        context.user_data["date_single"] = text.strip()
        context.user_data["waiting_for"] = None
        if context.user_data.get("selected_preset") in DATE_REQUIRING_PRESETS:
            await _ask_for_reason(message, context)
        else:
            await _finish_preset(message, context)

    # ── Leave reason ──────────────────────────────────────────────────────────
    elif waiting == "leave_reason":
        context.user_data["leave_reason"] = text.strip()
        context.user_data["waiting_for"] = None
        await _finish_preset(message, context)

    # ── Edit subject ──────────────────────────────────────────────────────────
    elif waiting == "edit_subject_text":
        context.user_data["email_subject"] = text
        context.user_data["waiting_for"] = None
        await message.reply_text(f"✅ Subject updated: {text}")
        await _send_preview(message, context)

    # ── Edit body ─────────────────────────────────────────────────────────────
    elif waiting == "edit_body_text":
        context.user_data["email_body"] = text
        context.user_data["waiting_for"] = None
        await message.reply_text("✅ Message body updated!")
        await _send_preview(message, context)

    # ── Unrecognised state ────────────────────────────────────────────────────
    else:
        await message.reply_text(
            "👋 Not sure what you mean. Use /start to begin.",
            reply_markup=home_keyboard(),
        )


async def _finish_preset(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Build the preset body and show the email preview."""
    preset_key = context.user_data.get("selected_preset")
    if not preset_key or preset_key not in PRESET_MESSAGES:
        await message.reply_text("❌ Error: Preset not found. Please start over with /start")
        return

    body = build_preset_body(preset_key, context.user_data)
    context.user_data["email_subject"] = PRESET_MESSAGES[preset_key]["subject"]
    context.user_data["email_body"] = body
    await _send_preview(message, context)
