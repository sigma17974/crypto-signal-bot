#!/usr/bin/env python3
"""
Quick Setup for Crypto Sniper Bot
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_banner():
    """Print setup banner"""
    print("""
🚀 Crypto Sniper Bot - Quick Setup
===================================
""")

def show_menu():
    """Show main menu"""
    print("""
Choose an option:

1. 📱 Setup Telegram Bot (Interactive)
2. 🧪 Run System Tests
3. 🚀 Start the Bot
4. 📊 View Admin Panel
5. 🔧 Manual Configuration
6. ❓ Help & Documentation
7. 🚪 Exit

""")

def setup_telegram():
    """Run Telegram setup"""
    print("\n📱 Starting Telegram Setup...")
    try:
        subprocess.run([sys.executable, "setup_telegram.py"])
    except FileNotFoundError:
        print("❌ setup_telegram.py not found")
        print("Please run: python setup_telegram.py")

def run_tests():
    """Run system tests"""
    print("\n🧪 Running System Tests...")
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
    except FileNotFoundError:
        print("❌ test_bot.py not found")

def start_bot():
    """Start the bot"""
    print("\n🚀 Starting Crypto Sniper Bot...")
    print("Press Ctrl+C to stop the bot")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except FileNotFoundError:
        print("❌ main.py not found")

def show_admin_info():
    """Show admin panel information"""
    print("""
📊 Admin Panel Information:
==========================

🌐 Web Interface:
   • Admin Panel: http://localhost:5000/admin
   • Signals API: http://localhost:5000/signals
   • Market Data: http://localhost:5000/market-data

📱 Telegram:
   • Check your Telegram for signals
   • Bot sends real-time trading signals

📈 Monitoring:
   • Bot status and statistics
   • Signal history and performance
   • Market data overview
""")

def manual_config():
    """Show manual configuration options"""
    print("""
🔧 Manual Configuration:
=======================

📁 Files to edit:
   • .env - Environment variables
   • config.py - Bot configuration
   • main.py - Core bot logic

🔑 Required Environment Variables:
   • TELEGRAM_TOKEN - Your bot token
   • TELEGRAM_CHAT_ID - Your chat ID
   • BINANCE_API_KEY - (Optional) For real trading
   • BINANCE_SECRET_KEY - (Optional) For real trading

⚙️ Configuration Options:
   • Trading pairs in config.py
   • Risk management settings
   • Technical indicator parameters
   • Signal filtering rules

📚 Documentation:
   • README.md - Complete guide
   • config.py - Configuration options
   • utils.py - Technical analysis
""")

def show_help():
    """Show help and documentation"""
    print("""
❓ Help & Documentation:
=======================

📚 Quick Start:
   1. python setup_telegram.py (Setup Telegram)
   2. python test_bot.py (Test everything)
   3. python main.py (Start bot)

📖 Documentation:
   • README.md - Complete setup guide
   • config.py - Configuration options
   • utils.py - Technical analysis functions

🔧 Troubleshooting:
   • Check .env file exists and has correct values
   • Ensure all dependencies are installed
   • Verify Telegram bot is working
   • Check internet connection

📞 Support:
   • GitHub Issues
   • Check logs for errors
   • Run test_bot.py for diagnostics

🎯 Features:
   • Real-time crypto signals
   • Advanced technical analysis
   • Risk management
   • Telegram notifications
   • Web admin panel
   • REST API access
""")

def check_environment():
    """Check if environment is properly configured"""
    print("\n🔍 Checking Environment...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Check required variables
    required_vars = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment configured")
    return True

def main():
    """Main setup function"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                setup_telegram()
            elif choice == "2":
                if check_environment():
                    run_tests()
                else:
                    print("❌ Please configure environment first (Option 1)")
            elif choice == "3":
                if check_environment():
                    start_bot()
                else:
                    print("❌ Please configure environment first (Option 1)")
            elif choice == "4":
                show_admin_info()
            elif choice == "5":
                manual_config()
            elif choice == "6":
                show_help()
            elif choice == "7":
                print("\n👋 Goodbye! Happy trading! 🚀")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy trading! 🚀")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()