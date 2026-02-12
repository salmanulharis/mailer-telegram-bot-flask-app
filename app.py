import asyncio
import logging
import os

from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from app.config import BOT_TOKEN, WEBHOOK_SECRET
from app.handlers.commands import start_command
from app.handlers.messages import handle_message
from app.handlers.callbacks import button_callback

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

# Build the PTB application once at module level
ptb_app = Application.builder().token(BOT_TOKEN).build()

# Register all handlers
ptb_app.add_handler(CommandHandler("start", start_command))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
ptb_app.add_handler(CallbackQueryHandler(button_callback))


def run_async(coro):
    """Run an async coroutine safely from a sync Flask route."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@flask_app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    """Receive updates from Telegram via webhook."""
    if request.content_type != "application/json":
        abort(415)

    data = request.get_json(force=True)
    if not data:
        abort(400)

    async def process():
        update = Update.de_json(data, ptb_app.bot)
        async with ptb_app:
            await ptb_app.process_update(update)

    run_async(process())
    return "OK", 200


@flask_app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@flask_app.route("/", methods=["GET"])
def index():
    return {"message": "Email Telegram Bot is running!"}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port, debug=False)