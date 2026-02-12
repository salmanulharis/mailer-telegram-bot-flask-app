#!/usr/bin/env python3
"""One-time script to register the webhook URL with Telegram."""
import asyncio
import sys

from telegram import Bot
from app.config import BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_SECRET, validate_config


async def set_webhook() -> None:
    missing = validate_config()
    if missing:
        print(f"❌ Missing config keys: {', '.join(missing)}")
        sys.exit(1)

    if not WEBHOOK_HOST:
        print("❌ WEBHOOK_HOST is not set in your .env file.")
        print("   Example: WEBHOOK_HOST=https://yourdomain.com")
        sys.exit(1)

    webhook_url = f"{WEBHOOK_HOST.rstrip('/')}/webhook/{WEBHOOK_SECRET}"

    async with Bot(token=BOT_TOKEN) as bot:
        me = await bot.get_me()
        print(f"🤖 Bot: @{me.username}")

        result = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
        )
        if result:
            print(f"✅ Webhook set to: {webhook_url}")
        else:
            print("❌ Failed to set webhook.")
            sys.exit(1)

        info = await bot.get_webhook_info()
        print(f"\nWebhook info:")
        print(f"  URL:             {info.url}")
        print(f"  Pending updates: {info.pending_update_count}")
        if info.last_error_message:
            print(f"  Last error:      {info.last_error_message}")


if __name__ == "__main__":
    asyncio.run(set_webhook())
