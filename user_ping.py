# user_ping.py  – run with python3
import os, asyncio
from telethon import TelegramClient

api_id   = int(os.getenv('TG_API_ID'))      # from https://my.telegram.org
api_hash = os.getenv('TG_API_HASH')
bot_id   = int(os.getenv('BOT_ID'))         # bot’s numeric ID (from t.me/<botname>)
my_id    = int(os.getenv('MY_ID'))          # your ID from step 1

async def main():
    async with TelegramClient('user_session', api_id, api_hash) as client:
        await client.send_message(bot_id, '/ping')

if __name__ == '__main__':
    asyncio.run(main())
    