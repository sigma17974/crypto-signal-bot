from flask import Flask, request, jsonify
from threading import Thread
import time, os, asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import random
# Select scanner implementation
from sniper.scanner import PairWatcherScanner
from sniper.trader import Trader

app = Flask(__name__)

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
TIMEFRAMES = ["1d", "4h", "1h", "15m"]

# === DUMMY STRATEGY ENGINE ===
def analyze_market():
    signal = random.choice(["LONG", "SHORT", None])
    coin = random.choice(COINS)
    if signal:
        send_telegram(f"🔥 {signal} Signal on {coin}\nTime: {time.ctime()}\nRisk: 1-2%\nTP/SL: 1:2 Ratio\nMomentum: Strong")

def send_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         params={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        except Exception as e:
            print("Telegram error:", e)

# === BACKGROUND SCHEDULER ===
scheduler = BackgroundScheduler()
scheduler.add_job(analyze_market, 'interval', minutes=5)
scheduler.start()

# === ADMIN PANEL ===
@app.route("/admin", methods=["GET"])
def admin():
    return "<h1>SigmaGPT Admin</h1><p>Signals running every 5 minutes.</p>", 200

# === UptimeRobot Ping ===
@app.route("/")
def ping():
    return "SigmaGPT Bot is Alive!", 200

# === START BOT ===
def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

Thread(target=run).start()

# Keep main thread alive


# === SNIPER ORCHESTRATOR ===

async def orchestrator():
    """Coordinates scanner and trader pipelines."""
    queue: asyncio.Queue = asyncio.Queue()
    scanner = PairWatcherScanner(queue)
    trader = Trader()

    # Launch scanner as a background task
    scanner_task = asyncio.create_task(scanner.start())

    try:
        while True:
            target = await queue.get()
            await trader.execute(target)
    except asyncio.CancelledError:
        # Graceful shutdown
        scanner.stop()
        await scanner_task


# Kick off orchestrator in main thread
asyncio.run(orchestrator())
