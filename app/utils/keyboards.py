"""Reusable inline keyboard builders."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Send Email", callback_data="send_email")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])


def recipient_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Select Group", callback_data="select_group")],
        [InlineKeyboardButton("✏️ Manual Entry", callback_data="manual_entry")],
    ])


def cc_options_keyboard(has_cc: bool = False) -> InlineKeyboardMarkup:
    if has_cc:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add More CC", callback_data="add_more_cc")],
            [InlineKeyboardButton("🗑️ Remove Last", callback_data="remove_last_cc")],
            [InlineKeyboardButton("✅ Done with CC", callback_data="done_with_cc")],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Add CC", callback_data="add_cc")],
        [InlineKeyboardButton("⏭️ Skip CC", callback_data="skip_cc")],
    ])


def modify_cc_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Modify CCs", callback_data="modify_cc")],
        [InlineKeyboardButton("✅ Continue", callback_data="done_with_cc")],
    ])


def message_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Use Preset Message", callback_data="use_preset")],
        [InlineKeyboardButton("✍️ Write Custom Message", callback_data="use_custom")],
    ])


def preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Edit", callback_data="preview_edit")],
        [InlineKeyboardButton("📧 Send", callback_data="send_email_confirm")],
    ])


def edit_options_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Edit Subject", callback_data="edit_subject")],
        [InlineKeyboardButton("✏️ Edit Body", callback_data="edit_body")],
        [InlineKeyboardButton("📧 Send Email", callback_data="send_email_confirm")],
    ])


def date_type_keyboard(multi_day: bool = True) -> InlineKeyboardMarkup:
    if multi_day:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Select Date Range", callback_data="date_select_range")],
            [InlineKeyboardButton("📅 Single Day", callback_data="date_select_single")],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Select Date", callback_data="date_select_single")],
    ])


def reason_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Personal Reasons", callback_data="reason_personal")],
        [InlineKeyboardButton("✍️ Custom Reason", callback_data="reason_custom")],
        [InlineKeyboardButton("⏭️ Skip Reason", callback_data="reason_skip")],
    ])


def post_send_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Send Another", callback_data="send_another")],
        [InlineKeyboardButton("🏠 Home", callback_data="back_to_home")],
    ])
