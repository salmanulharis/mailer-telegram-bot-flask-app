# 📧 Email Telegram Bot — Flask + Webhook

A Telegram bot that lets you send emails (leave requests, WFH, custom messages) via inline keyboard flows. Built with **Flask** + **python-telegram-bot v21** running on **webhooks**.

---

## 📁 Folder Structure

```
email_bot/
├── app.py                    # Flask entry point & webhook route
├── set_webhook.py            # One-time script: register webhook with Telegram
├── delete_webhook.py         # Remove webhook (switch back to polling)
├── requirements.txt
├── Procfile                  # Gunicorn (for Heroku / Railway / Render)
├── .env.example              # Copy to .env and fill in your values
├── .gitignore
└── app/
    ├── __init__.py
    ├── config.py             # All env-var loading & constants
    ├── handlers/
    │   ├── __init__.py
    │   ├── commands.py       # /start command
    │   ├── messages.py       # Text message handler (multi-step states)
    │   └── callbacks.py      # Inline keyboard callback handler
    └── utils/
        ├── __init__.py
        ├── keyboards.py      # Reusable InlineKeyboardMarkup builders
        ├── email_sender.py   # SMTP send via Gmail
        ├── preview.py        # Build email preview text
        └── preset_builder.py # Fill date/reason into preset bodies
```

---

## 🚀 Setup Guide

### 1. Prerequisites

- Python 3.11+
- A **public HTTPS URL** for your server (Telegram requires HTTPS for webhooks)
  - Free options: [ngrok](https://ngrok.com) (local dev), [Railway](https://railway.app), [Render](https://render.com), [Heroku](https://heroku.com)
- A **Telegram bot token** from [@BotFather](https://t.me/BotFather)
- A **Gmail App Password** (not your real password — see step 4)

---

### 2. Clone & Install

```bash
git clone <your-repo>
cd email_bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

### 3. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDefgh...
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop     # Gmail App Password (16 chars with spaces)
WEBHOOK_HOST=https://yourdomain.com    # Your public HTTPS URL (no trailing slash)
WEBHOOK_SECRET=some_long_random_string # Becomes part of the webhook path
```

---

### 4. Generate a Gmail App Password

> ⚠️ Do **not** use your real Gmail password. Google blocks plain-password SMTP by default.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already on
3. Search for **"App passwords"**
4. Create a new app password (name it "Telegram Bot" or anything)
5. Copy the 16-character password into `EMAIL_PASSWORD` in `.env`

---

### 5. Register the Webhook

After your server is running and publicly reachable:

```bash
python set_webhook.py
```

Expected output:
```
🤖 Bot: @your_bot_name
✅ Webhook set to: https://yourdomain.com/webhook/some_long_random_string

Webhook info:
  URL:             https://yourdomain.com/webhook/some_long_random_string
  Pending updates: 0
```

---

### 6. Run Locally (with ngrok)

**Terminal 1 — start the Flask app:**
```bash
python app.py
# Runs on http://0.0.0.0:5000
```

**Terminal 2 — expose it publicly:**
```bash
ngrok http 5000
# Note the https URL, e.g. https://abc123.ngrok.io
```

Update `.env`:
```env
WEBHOOK_HOST=https://abc123.ngrok.io
```

Then register the webhook:
```bash
python set_webhook.py
```

---

### 7. Run in Production (Gunicorn)

```bash
gunicorn "app:flask_app" \
  --worker-class gevent \
  --workers 1 \
  --bind 0.0.0.0:5000
```

Or set `PORT` environment variable and use the included `Procfile`.

---

### 8. Deploy to Railway / Render / Heroku

1. Push your code to GitHub (`.env` is gitignored — set env vars in the platform dashboard)
2. Set all env vars in the platform's settings panel
3. Deploy — the platform assigns a public HTTPS URL automatically
4. Run `python set_webhook.py` once (or add it as a post-deploy hook)

---

## ⚙️ Customisation

### Change receiver groups

Edit `.env` to override the default groups:

```env
RECEIVER_GROUPS={"hr_managers":{"name":"👥 HR + Managers","receiver":"hr@company.com","cc":["mgr@company.com"]},"hr":{"name":"🤝 HR Only","receiver":"hr@company.com","cc":[]}}
```

Or edit the `_default_groups` dict directly in `app/config.py`.

### Add new preset messages

Add an entry to `PRESET_MESSAGES` in `app/config.py`:

```python
"medical_leave": {
    "subject": "Medical Leave Request",
    "body": "Hi,\n\nI am writing to request medical leave on [dates][reason].\n\n...",
}
```

If it needs date input, add its key to `DATE_REQUIRING_PRESETS` in the same file.

---

## 🔍 Useful Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/<SECRET>` | POST | Telegram update receiver |
| `/health` | GET | Health check |
| `/` | GET | Status page |

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `401 Unauthorized` from Telegram | Wrong `BOT_TOKEN` |
| `SMTPAuthenticationError` | Use a Gmail App Password, not your real password |
| Webhook not receiving updates | Check HTTPS cert is valid; re-run `set_webhook.py` |
| `409 Conflict` error in logs | Another instance using polling — run `delete_webhook.py` on old instance |
| Updates arrive but bot doesn't reply | Check `/health` endpoint; look at server logs |

---

## 🔄 Switch Back to Polling (development)

```bash
python delete_webhook.py
# Then run the original polling bot if needed
```
