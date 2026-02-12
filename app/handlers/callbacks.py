"""Telegram inline-keyboard callback handler."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.config import (
    RECEIVER_GROUPS,
    PRESET_MESSAGES,
    DATE_REQUIRING_PRESETS,
)
from app.utils.keyboards import (
    home_keyboard,
    recipient_type_keyboard,
    cc_options_keyboard,
    modify_cc_keyboard,
    message_type_keyboard,
    preview_keyboard,
    edit_options_keyboard,
    date_type_keyboard,
    reason_keyboard,
    post_send_keyboard,
)
from app.utils.preview import build_preview
from app.utils.preset_builder import build_preset_body
from app.utils.email_sender import send_email as smtp_send_email

logger = logging.getLogger(__name__)


# ── Small helpers ─────────────────────────────────────────────────────────────

async def _show_preview(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    receiver = context.user_data.get("receiver_email", "Not set")
    cc_list = context.user_data.get("cc_recipients", [])
    subject = context.user_data.get("email_subject", "No subject")
    body = context.user_data.get("email_body", "No body")
    await query.edit_message_text(
        text=build_preview(receiver, cc_list, subject, body),
        reply_markup=preview_keyboard(),
        parse_mode="Markdown",
    )


async def _finish_preset_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    preset_key = context.user_data.get("selected_preset")
    if not preset_key or preset_key not in PRESET_MESSAGES:
        await query.edit_message_text("❌ Preset not found. Please start over with /start")
        return
    body = build_preset_body(preset_key, context.user_data)
    context.user_data["email_subject"] = PRESET_MESSAGES[preset_key]["subject"]
    context.user_data["email_body"] = body
    await _show_preview(query, context)


# ── Main dispatcher ───────────────────────────────────────────────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data: str = query.data

    # ── Home / Help ───────────────────────────────────────────────────────────
    if data == "back_to_home":
        context.user_data.clear()
        await query.edit_message_text(
            text="Welcome to Email Bot! 📧\n\nChoose an option below:",
            reply_markup=home_keyboard(),
        )

    elif data == "help":
        help_text = (
            "📧 **Email Bot Help**\n\n"
            "1. Click 'Send Email' to start\n"
            "2. Select a group OR enter receiver email manually\n"
            "3. Add additional CC recipients (optional)\n"
            "4. Choose message type (preset or custom)\n"
            "5. Preview and confirm\n"
            "6. Message will be sent!\n\n"
            "/start — Return to main menu"
        )
        await query.edit_message_text(text=help_text, parse_mode="Markdown")

    # ── Start email flow ──────────────────────────────────────────────────────
    elif data == "send_email":
        await query.edit_message_text(
            text="📧 Choose how to select recipients:",
            reply_markup=recipient_type_keyboard(),
        )

    # ── Recipient selection ───────────────────────────────────────────────────
    elif data == "select_group":
        keyboard_rows = [
            [__import__("telegram", fromlist=["InlineKeyboardButton"]).InlineKeyboardButton(
                group["name"], callback_data=f"group_{key}"
            )]
            for key, group in RECEIVER_GROUPS.items()
        ]
        from telegram import InlineKeyboardMarkup
        await query.edit_message_text(
            text="👥 **Select a receiver group:**",
            reply_markup=InlineKeyboardMarkup(keyboard_rows),
            parse_mode="Markdown",
        )

    elif data == "manual_entry":
        context.user_data["waiting_for"] = "receiver_email"
        await query.edit_message_text(text="📧 Enter the receiver's email address:")

    elif data.startswith("group_"):
        group_key = data.removeprefix("group_")
        group = RECEIVER_GROUPS.get(group_key)
        if not group:
            await query.edit_message_text("❌ Group not found.")
            return
        context.user_data["receiver_email"] = group["receiver"]
        context.user_data["cc_recipients"] = group["cc"].copy()
        context.user_data["selected_group"] = group_key

        cc_text = "\n".join(f"• {e}" for e in group["cc"]) or "None"
        await query.edit_message_text(
            text=(
                f"✅ **Group Selected: {group['name']}**\n\n"
                f"**Main Receiver:** {group['receiver']}\n\n"
                f"**CC Recipients:**\n{cc_text}"
            ),
            reply_markup=modify_cc_keyboard(),
            parse_mode="Markdown",
        )

    # ── CC management ─────────────────────────────────────────────────────────
    elif data == "add_cc":
        context.user_data["waiting_for"] = "cc_email"
        await query.edit_message_text(text="📧 Enter CC email address:")

    elif data == "skip_cc":
        await query.edit_message_text(
            text="📝 Choose message type:",
            reply_markup=message_type_keyboard(),
        )

    elif data == "modify_cc":
        cc_list = context.user_data.get("cc_recipients", [])
        cc_text = "\n".join(f"• {e}" for e in cc_list) or "No CC recipients"
        await query.edit_message_text(
            text=f"📋 Current CCs:\n{cc_text}\n\nWhat would you like to do?",
            reply_markup=cc_options_keyboard(has_cc=True),
        )

    elif data == "add_more_cc":
        context.user_data["waiting_for"] = "cc_email"
        await query.edit_message_text(text="📧 Enter another CC email address:")

    elif data == "remove_last_cc":
        cc_list = context.user_data.get("cc_recipients", [])
        if cc_list:
            removed = cc_list.pop()
            cc_text = "\n".join(f"• {e}" for e in cc_list) or "No CC recipients"
            await query.edit_message_text(
                text=f"🗑️ Removed: {removed}\n\nCurrent CC List:\n{cc_text}",
                reply_markup=cc_options_keyboard(has_cc=bool(cc_list)),
            )
        else:
            await query.edit_message_text(
                text="No CC recipients to remove.",
                reply_markup=cc_options_keyboard(has_cc=False),
            )

    elif data == "done_with_cc":
        await query.edit_message_text(
            text="📝 Choose message type:",
            reply_markup=message_type_keyboard(),
        )

    # ── Message type ──────────────────────────────────────────────────────────
    elif data == "use_preset":
        keyboard_rows = [
            [__import__("telegram", fromlist=["InlineKeyboardButton"]).InlineKeyboardButton(
                msg["subject"], callback_data=f"preset_{key}"
            )]
            for key, msg in PRESET_MESSAGES.items()
        ]
        from telegram import InlineKeyboardMarkup
        await query.edit_message_text(
            text="📌 Select a preset message:",
            reply_markup=InlineKeyboardMarkup(keyboard_rows),
        )

    elif data.startswith("preset_"):
        preset_key = data.removeprefix("preset_")
        if preset_key not in PRESET_MESSAGES:
            await query.edit_message_text("❌ Preset not found.")
            return
        context.user_data["selected_preset"] = preset_key

        if preset_key in DATE_REQUIRING_PRESETS:
            multi_day = preset_key in ("leave_request", "wfh")
            label = "leave/WFH" if multi_day else "half-day/WFH"
            await query.edit_message_text(
                text=f"📅 **Select date(s) for your {label}:**",
                reply_markup=date_type_keyboard(multi_day=multi_day),
                parse_mode="Markdown",
            )
        else:
            # Non-date preset — straight to preview
            preset = PRESET_MESSAGES[preset_key]
            context.user_data["email_subject"] = preset["subject"]
            context.user_data["email_body"] = preset["body"]
            await _show_preview(query, context)

    elif data == "use_custom":
        context.user_data["waiting_for"] = "custom_subject"
        await query.edit_message_text(text="📝 Enter the email subject:")

    # ── Date selection ────────────────────────────────────────────────────────
    elif data == "date_select_range":
        context.user_data["waiting_for"] = "date_range_start"
        await query.edit_message_text(
            text="📅 Enter start date (format: YYYY-MM-DD or DD/MM/YYYY):\nExample: 2026-02-15"
        )

    elif data == "date_select_single":
        context.user_data["waiting_for"] = "date_single"
        await query.edit_message_text(
            text="📅 Enter the date (format: YYYY-MM-DD or DD/MM/YYYY):\nExample: 2026-02-15"
        )

    # ── Reason selection ──────────────────────────────────────────────────────
    elif data == "reason_personal":
        context.user_data["leave_reason"] = "personal reasons"
        await _finish_preset_callback(query, context)

    elif data == "reason_custom":
        context.user_data["waiting_for"] = "leave_reason"
        await query.edit_message_text(text="✍️ Enter your reason for leave:")

    elif data == "reason_skip":
        context.user_data["leave_reason"] = ""
        await _finish_preset_callback(query, context)

    # ── Preview editing ───────────────────────────────────────────────────────
    elif data == "preview_edit":
        await query.edit_message_text(
            text="What would you like to edit?",
            reply_markup=edit_options_keyboard(),
        )

    elif data == "edit_subject":
        current = context.user_data.get("email_subject", "")
        context.user_data["waiting_for"] = "edit_subject_text"
        await query.edit_message_text(
            text=f"✏️ **Current Subject:**\n{current}\n\n📝 Enter new subject:",
            parse_mode="Markdown",
        )

    elif data == "edit_body":
        current = context.user_data.get("email_body", "")
        context.user_data["waiting_for"] = "edit_body_text"
        await query.edit_message_text(
            text=(
                f"✏️ **Current Body:**\n─────────────────\n{current}\n─────────────────\n\n"
                f"📝 Enter new message body:"
            ),
            parse_mode="Markdown",
        )

    # ── Send ──────────────────────────────────────────────────────────────────
    elif data == "send_email_confirm":
        receiver = context.user_data.get("receiver_email")
        cc_list = context.user_data.get("cc_recipients", [])
        subject = context.user_data.get("email_subject")
        body = context.user_data.get("email_body")

        if not all([receiver, subject, body]):
            await query.edit_message_text(
                "❌ Missing email details. Please start over with /start"
            )
            return

        try:
            smtp_send_email(receiver, subject, body, cc_list)
            await query.edit_message_text(
                text="✅ **Email sent successfully!** 📧\n\nWhat's next?",
                reply_markup=post_send_keyboard(),
                parse_mode="Markdown",
            )
        except Exception as exc:
            logger.error("SMTP error: %s", exc)
            await query.edit_message_text(
                text=(
                    f"❌ Error sending email:\n`{exc}`\n\n"
                    "Please check your email credentials in the `.env` file."
                ),
                parse_mode="Markdown",
            )

    elif data == "send_another":
        context.user_data.clear()
        await query.edit_message_text(
            text="📧 Choose how to select recipients:",
            reply_markup=recipient_type_keyboard(),
        )

    else:
        logger.warning("Unhandled callback: %s", data)
        await query.edit_message_text(
            text="❓ Unknown action. Please start over with /start",
            reply_markup=home_keyboard(),
        )
