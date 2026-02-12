"""Telegram command handlers (/start, etc.)."""
from telegram import Update
from telegram.ext import ContextTypes

from app.utils.keyboards import home_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    context.user_data.clear()
    await update.message.reply_text(
        "Welcome to Email Bot! 📧\n\nChoose an option below:",
        reply_markup=home_keyboard(),
    )
