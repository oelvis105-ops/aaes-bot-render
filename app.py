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

def run():
    # Set webhook
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = f"{render_url}/webhook"
        telegram_app.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set: {webhook_url}")
    
    port = int(os.getenv("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()
