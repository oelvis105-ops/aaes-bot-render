# daily_ping.py
import os, requests, time

TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("1836471542")   # your own chat with the bot

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
try:
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": "/ping"}, timeout=15)
except Exception as e:
    pass          # fail silently – we only care that *something* hits the bot
