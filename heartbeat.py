from flask import Flask
import requests
import os
import time

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('1836471542')  # Replace with your chat ID

@app.route('/heartbeat')
def heartbeat():
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                   params={'chat_id': CHAT_ID, 'text': 'Heartbeat: Bot is still running.'})
        return "Heartbeat sent successfully", 200
    except Exception as e:
        return f"Failed to send heartbeat: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)  # Run on localhost