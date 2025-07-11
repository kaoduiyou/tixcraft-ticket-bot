import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import os
import time
import threading
import http.server
import socketserver

# ===== Discord Bot 設定 =====
TOKEN = os.environ['TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

# ===== tixCraft 網址 & 頻率設定 =====
CHECK_URL = "https://tixcraft.com/ticket/area/25_bm/19396"
CHECK_INTERVAL = 10         # 每幾秒檢查一次
REPORT_INTERVAL = 300      # 每幾秒報一次平安（預設 5 分鐘）

# ===== Discord 初始化 =====
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

            result = []
            for btn in soup.find_all('button'):
                text = btn.get_text(strip=True)
                if "剩餘" in text:
                    result.append(text)

            if result:
                msg = "🎟️ 有票啦！目前釋出票區如下：\n"
                for line in result:
                    msg += f"- {line}\n"
                msg += f"\n👉 {CHECK_URL}"
                await channel.send(msg)
                print("[通知] 已釋票！")
            elif now - last_report_time >= REPORT_INTERVAL:
                await channel.send("🕒 [定時通知] 目前仍無釋票（持續監控中）")
                last_report_time = now
                print("[定時通知] 無票")
            else:
                print("[掃描中] 尚未釋票")
        except Exception as e:
            print("⚠️ 發生錯誤：", e)
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f'✅ 已登入 Discord：{client.user}')
    client.loop.create_task(check_tickets())

# ===== 假裝開一個網站 (for Render) =====
def run_fake_web_server():
    PORT = 10000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 假網站運行中（Render 會掃這個 port）: {PORT}")
        httpd.serve_forever()

# 啟動 fake web server（獨立執行緒）
threading.Thread(target=run_fake_web_server).start()

# 啟動 Discord bot
client.run(TOKEN)
