#!/usr/bin/env python3
"""
Deployment Script for CryptoSniperXProBot
Starts the bot with all enhanced features and admin dashboard
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'ta', 'requests', 
        'flask', 'apscheduler', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip3 install --break-system-packages " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_configuration():
    """Check if bot configuration is properly set"""
    print("\n🔍 Checking configuration...")
    
    required_env_vars = [
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} - Not set")
        else:
            print(f"✅ {var} - Set")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print("✅ Configuration is properly set!")
    return True

def start_bot():
    """Start the crypto sniper bot"""
    print("\n🚀 Starting CryptoSniperXProBot...")
    
    try:
        # Import and start the bot
        from main import CryptoSniperBot
        
        print("✅ Bot imported successfully")
        print("🔄 Initializing bot...")
        
        # Create bot instance
        bot = CryptoSniperBot()
        
        print("✅ Bot initialized successfully")
        print("🔄 Starting bot services...")
        
        # Start the bot in a separate thread
        def run_bot():
            try:
                bot.run()
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
            except Exception as e:
                print(f"❌ Bot error: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        print("✅ Bot started successfully!")
        print("🔄 Bot is now running in the background...")
        
        return bot
        
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        return None

def check_bot_status(bot):
    """Check if bot is running properly"""
    print("\n🔍 Checking bot status...")
    
    try:
        # Check if bot is running
        if bot and bot.is_running:
            print("✅ Bot is running")
        else:
            print("❌ Bot is not running")
            return False
        
        # Check admin dashboard
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                print("✅ Admin dashboard is accessible")
            else:
                print("❌ Admin dashboard not responding")
        except Exception as e:
            print(f"⚠️ Admin dashboard check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def display_admin_info():
    """Display admin dashboard information"""
    print("\n" + "="*60)
    print("🎛️  ADMIN DASHBOARD INFORMATION")
    print("="*60)
    
    print("🌐 Admin Dashboard URL: http://localhost:5000/admin")
    print("📊 API Status: http://localhost:5000/api/status")
    print("📈 Signals: http://localhost:5000/signals")
    print("📊 Performance: http://localhost:5000/performance")
    print("📋 Signal History: http://localhost:5000/signals/history")
    
    print("\n🔧 Bot Features:")
    print("✅ TP/SL calculation with dynamic adjustment")
    print("✅ Momentum-based signal generation")
    print("✅ Smart AI logic for trading decisions")
    print("✅ Dynamic market scanning system")
    print("✅ Risk assessment and scoring")
    print("✅ Support/Resistance detection")
    print("✅ Email notifications (if configured)")
    print("✅ Telegram notifications with detailed analysis")
    print("✅ Arbitrage detection across 40+ exchanges")
    print("✅ Real-time chart generation")
    print("✅ Performance tracking and analytics")
    
    print("\n📱 Telegram Bot:")
    print(f"🤖 Bot Name: CryptoSniperXProBot")
    print(f"📱 Username: @crypto_sniper_pro_bot")
    print(f"💬 Chat ID: {os.getenv('TELEGRAM_CHAT_ID', 'Not set')}")
    
    print("\n⚙️ Configuration:")
    print(f"📊 Trading Pairs: 20 major pairs")
    print(f"⏰ Timeframes: 1m, 5m, 15m, 1h, 4h")
    print(f"🎯 Risk Management: 2% max risk per trade")
    print(f"⚖️ Min Risk/Reward: 2.0")
    print(f"🔄 Update Interval: 1 minute")
    
    print("\n🚀 Bot is now running and monitoring markets!")
    print("📱 You will receive signals via Telegram")
    print("🌐 Access admin dashboard for detailed monitoring")

def main():
    """Main deployment function"""
    print("🚀 CryptoSniperXProBot Deployment")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Deployment failed: Missing dependencies")
        return False
    
    # Check configuration
    if not check_configuration():
        print("\n❌ Deployment failed: Configuration issues")
        return False
    
    # Start bot
    bot = start_bot()
    if not bot:
        print("\n❌ Deployment failed: Could not start bot")
        return False
    
    # Wait a moment for bot to initialize
    time.sleep(3)
    
    # Check bot status
    if not check_bot_status(bot):
        print("\n❌ Deployment failed: Bot not running properly")
        return False
    
    # Display admin information
    display_admin_info()
    
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("="*60)
    
    # Keep the script running to maintain bot
    try:
        while True:
            time.sleep(60)  # Check every minute
            if not bot.is_running:
                print("❌ Bot stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Deployment stopped by user")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)