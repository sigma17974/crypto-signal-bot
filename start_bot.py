#!/usr/bin/env python3port os
import sys
import time
import subprocess
import requests
from datetime import datetime

print("Starting CryptoSniperXProBot...")
print(= * 50 Check if bot file exists
if not os.path.exists(crypto_sniper_bot.py'):
    print(ERROR: crypto_sniper_bot.py not found!")
    sys.exit(1)

# Start the bot in background
print("Starting bot process...")
bot_process = subprocess.Popen([
    sys.executable, crypto_sniper_bot.py'
], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for startup
time.sleep(10
# Check if bot is running
if bot_process.poll() is None:
    print("Bot started successfully!")
    print("Bot will scan markets every 15 minutes")
    print("Admin Dashboard: http://localhost:5000/admin")
    print("Login: admin / admin123")
    print("Check Telegram for signals")
    print("Press Ctrl+C to stop")
    
    # Monitor bot
    try:
        while True:
            try:
                response = requests.get(http://localhost:5000/api/status', timeout=5                if response.status_code == 200:
                    status = response.json()
                    signals = status.get(signals_generated', 0)
                    print(f[{datetime.now().strftime('%H:%M:%S)}] Bot running - Signals: {signals})              else:
                    print(f[{datetime.now().strftime('%H:%M:%S')}] Bot not responding")
            except Exception as e:
                print(f[{datetime.now().strftime('%H:%M:%S')}] Monitoring error: {e}")
            
            time.sleep(60Check every minute
            
    except KeyboardInterrupt:
        print(nStopping bot...")
        bot_process.terminate()
        try:
            bot_process.wait(timeout=10)
            print("Bot stopped gracefully")
        except subprocess.TimeoutExpired:
            bot_process.kill()
            print("Bot force killed")
else:
    stdout, stderr = bot_process.communicate()
    print(f"Bot failed to start: {stderr.decode()}")
    sys.exit(1)