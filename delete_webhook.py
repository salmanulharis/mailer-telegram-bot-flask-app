#!/usr/bin/env python3
"""Delete the registered webhook (switch back to polling mode)."""
import asyncio

from telegram import Bot
from app.config import BOT_TOKEN


async def delete_webhook() -> None:
    async with Bot(token=BOT_TOKEN) as bot:
        result = await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted." if result else "❌ Failed to delete webhook.")


if __name__ == "__main__":
    asyncio.run(delete_webhook())
