#!/usr/bin/env python3
"""
Test script for Crypto Sniper Bot
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration...")
    
    required_vars = [
        "TELEGRAM_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        "flask",
        "apscheduler", 
        "requests",
        "ccxt",
        "pandas",
        "numpy",
        "ta",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def test_telegram_connection():
    """Test Telegram bot connection"""
    print("\n📱 Testing Telegram Connection...")
    
    import requests
    
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    try:
        # Test bot info
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: @{bot_info['result']['username']}")
        else:
            print("❌ Invalid Telegram token")
            return False
        
        # Test message sending
        test_message = f"🤖 Crypto Sniper Bot Test\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nStatus: ✅ Connected"
        
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": test_message,
                "parse_mode": "Markdown"
            }
        )
        
        if response.status_code == 200:
            print("✅ Test message sent successfully")
            return True
        else:
            print(f"❌ Failed to send message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram connection error: {e}")
        return False

def test_exchange_connection():
    """Test exchange connection"""
    print("\n💱 Testing Exchange Connection...")
    
    import ccxt
    
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })
        
        # Test market data
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Exchange connected - BTC Price: ${ticker['last']:,.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Exchange connection error: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization"""
    print("\n🤖 Testing Bot Initialization...")
    
    try:
        from main import CryptoSniperBot
        
        # Test bot creation
        bot = CryptoSniperBot()
        print("✅ Bot initialized successfully")
        
        # Test configuration
        print(f"📊 Monitored pairs: {len(bot.SYMBOLS)}")
        print(f"⏰ Timeframes: {len(bot.TIMEFRAMES)}")
        print(f"⚙️ Risk per trade: {bot.max_risk_per_trade * 100}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Crypto Sniper Bot - System Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_dependencies,
        test_telegram_connection,
        test_exchange_connection,
        test_bot_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error: {test.__name__} - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        print("\n🚀 Start the bot with: python main.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)