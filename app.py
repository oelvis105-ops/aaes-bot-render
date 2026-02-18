import os
import json
import logging

sa_json = os.getenv("GOOGLE_SA_JSON")
if sa_json:
    with open("service_account.json", "w") as f:
        f.write(sa_json)
    print("✅ service_account.json created from environment")
else:
    print("⚠️ GOOGLE_SA_JSON not set - Google Drive will fail")
# ========== CREATE SERVICE ACCOUNT JSON FIRST ==========
import base64

sa_json_b64 = os.getenv("GOOGLE_SA_JSON_B64")
if sa_json_b64:
    # Decode base64 to get original JSON
    sa_json = base64.b64decode(sa_json_b64).decode('utf-8')
    with open("service_account.json", "w") as f:
        f.write(sa_json)
    print("✅ service_account.json created from base64 environment")
else:
    print("⚠️ GOOGLE_SA_JSON_B64 not set - Google Drive will fail")    
from flask import Flask, request
from telegram import Update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aaes-bot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set")

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✈️ AAES Bot is running!", 200

@flask_app.route("/health")
def health():
    return {"status": "alive"}, 200

# Import your existing bot
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Build bot application
from telegram.ext import ApplicationBuilder
from bot import build_app

telegram_app = build_app()

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), telegram_app.bot)
    telegram_app.process_update(update)
    return "ok", 200

import asyncio
import re

def run():
    # Set webhook properly
    render_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    
    # Remove any non-printable characters
    render_url = ''.join(char for char in render_url if ord(char) >= 32 and ord(char) <= 126)
    
    # Ensure it starts with https://
    if render_url and not render_url.startswith('http'):
        render_url = f"https://{render_url}"
    
    if render_url:
        webhook_url = f"{render_url}/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        try:
            # Run async set_webhook in sync context
            asyncio.run(telegram_app.bot.set_webhook(url=webhook_url))
            logger.info(f"✅ Webhook set successfully")
        except Exception as e:
            logger.error(f"❌ Failed to set webhook: {e}")
    else:
        logger.warning("⚠️ RENDER_EXTERNAL_URL not set, skipping webhook setup")
    
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()
