import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import os
import time

TOKEN = os.environ['TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
CHECK_URL = "https://tixcraft.com/ticket/area/25_bm/19396"
CHECK_INTERVAL = 30
REPORT_INTERVAL = 3600

intents = discord.Intents.default()
client = discord.Client(intents=intents)
last_report_time = time.time()

async def check_tickets():
    global last_report_time
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(CHECK_URL, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            now = time.time()
            if "立即購票" in soup.text or "選擇座位" in soup.text:
                await channel.send(f"🎟️ 有票啦！快衝 👉 {CHECK_URL}")
            elif now - last_report_time >= REPORT_INTERVAL:
                await channel.send("🕒 [定時通知] 目前仍無釋票（持續監控中）")
                last_report_time = now
            else:
                print("尚未釋票")
        except Exception as e:
            print("⚠️ 發生錯誤：", e)
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f'✅ 已登入 Discord：{client.user}')
    client.loop.create_task(check_tickets())

client.run(TOKEN)
