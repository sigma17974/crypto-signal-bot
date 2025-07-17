#!/usr/bin/env python3
"""
Setup script for Crypto Sniper Bot
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("""
🚀 Crypto Sniper Bot Setup
==========================
""")

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    
    env_content = """# Telegram Configuration (Required)
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Binance API (Optional - for real trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Bot Configuration
PORT=5000
LOG_LEVEL=INFO

# Trading Configuration
MAX_RISK_PER_TRADE=0.02
MIN_RISK_REWARD_RATIO=2.0
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env file with your credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def get_telegram_help():
    """Show Telegram setup help"""
    print("""
📱 Telegram Setup Options:
==========================

Option 1 - Interactive Setup (Recommended):
   python setup_telegram.py

Option 2 - Manual Setup:
   1. Create a Telegram bot:
      - Message @BotFather on Telegram
      - Send /newbot
      - Choose a name for your bot
      - Choose a username (must end with 'bot')
      - Copy the token to TELEGRAM_TOKEN in .env

   2. Get your Chat ID:
      - Message your bot
      - Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
      - Copy the 'chat_id' to TELEGRAM_CHAT_ID in .env

   3. Test the connection:
      - Run: python test_bot.py
""")

def run_tests():
    """Run system tests"""
    print("\n🧪 Running system tests...")
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def show_next_steps():
    """Show next steps"""
    print("""
🚀 Next Steps:
==============

1. Edit .env file with your credentials
2. Run tests: python test_bot.py
3. Start the bot: python main.py
4. Visit admin panel: http://localhost:5000/admin

📚 Documentation:
- README.md - Complete setup guide
- config.py - Configuration options
- utils.py - Technical analysis functions

🐳 Docker (Optional):
- Build: docker build -t crypto-sniper-bot .
- Run: docker-compose up -d

Happy Trading! 🚀
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Show Telegram help
    get_telegram_help()
    
    # Run tests if .env is configured
    if os.getenv("TELEGRAM_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        run_tests()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()