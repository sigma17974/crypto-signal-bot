#!/usr/bin/env python3
"""
Test script for Crypto Sniper Bot
"""

import os
import sys
import time
from datetime import datetime
import requests
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
    
    optional_vars = [
        "BINANCE_API_KEY",
        "BINANCE_SECRET_KEY"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these variables in your .env file")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {missing_optional}")
        print("These are optional but recommended for full functionality")
    
    print("✅ Environment configuration looks good!")
    return True

def test_telegram():
    """Test Telegram bot connection"""
    print("\n📱 Testing Telegram Bot...")
    
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Telegram credentials not configured")
        return False
    
    try:
        # Test bot info
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: @{bot_info['result']['username']}")
            
            # Test sending message
            test_message = f"🤖 Crypto Sniper Bot Test\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nStatus: Online and ready!"
            
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": test_message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                print("✅ Test message sent successfully!")
                return True
            else:
                print(f"❌ Failed to send test message: {response.text}")
                return False
                
        else:
            print(f"❌ Failed to connect to Telegram: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

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
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def test_bot_import():
    """Test bot module import"""
    print("\n🤖 Testing Bot Import...")
    
    try:
        from main import CryptoSniperBot
        print("✅ Bot module imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to import bot: {e}")
        return False

def test_config():
    """Test configuration validation"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        from config import Config
        
        if Config.validate():
            print("✅ Configuration validation passed!")
            print(f"📊 Monitored pairs: {len(Config.SYMBOLS)}")
            print(f"⏰ Timeframes: {len(Config.TIMEFRAMES)}")
            print(f"🎯 Risk per trade: {Config.MAX_RISK_PER_TRADE * 100}%")
            print(f"⚖️  Min risk-reward: 1:{Config.MIN_RISK_REWARD_RATIO}")
            return True
        else:
            print("❌ Configuration validation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Crypto Sniper Bot - System Test")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Configuration", test_config),
        ("Bot Import", test_bot_import),
        ("Telegram", test_telegram)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("\nTo start the bot:")
        print("python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the bot.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)