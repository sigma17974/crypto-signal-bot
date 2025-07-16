#!/usr/bin/env python3
"""
Setup script for Crypto Sniper Bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping environment setup")
            return True
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Environment file created: .env")
        print("📝 Please edit .env with your credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def get_telegram_credentials():
    """Interactive Telegram setup"""
    print("\n📱 Telegram Bot Setup")
    print("=" * 30)
    
    print("1. Create a Telegram bot:")
    print("   - Message @BotFather on Telegram")
    print("   - Send /newbot")
    print("   - Follow the instructions")
    print("   - Copy the bot token")
    
    token = input("\nEnter your bot token: ").strip()
    
    if not token:
        print("❌ Bot token is required")
        return False
    
    print("\n2. Get your chat ID:")
    print("   - Message your bot")
    print("   - Visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("   - Copy the 'chat_id' value")
    
    chat_id = input("\nEnter your chat ID: ").strip()
    
    if not chat_id:
        print("❌ Chat ID is required")
        return False
    
    # Update .env file
    try:
        env_content = Path(".env").read_text()
        env_content = env_content.replace("your_telegram_bot_token_here", token)
        env_content = env_content.replace("your_telegram_chat_id_here", chat_id)
        Path(".env").write_text(env_content)
        print("✅ Telegram credentials saved to .env")
        return True
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def run_tests():
    """Run system tests"""
    print("\n🧪 Running system tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Crypto Sniper Bot Setup")
    print("=" * 40)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Telegram Setup", get_telegram_credentials),
        ("System Tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your Binance API keys (optional)")
    print("2. Run the bot: python main.py")
    print("3. Or use Docker: docker-compose up -d")
    print("4. Visit http://localhost:5000/admin for the admin panel")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)