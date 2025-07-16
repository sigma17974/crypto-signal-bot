#!/usr/bin/env python3
"""
Interactive Telegram Setup for Crypto Sniper Bot
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load existing environment variables
load_dotenv()

def print_banner():
    """Print setup banner"""
    print("""
🤖 Telegram Bot Setup for Crypto Sniper Bot
============================================
""")

def get_user_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def create_telegram_bot():
    """Guide user through creating a Telegram bot"""
    print("\n📱 Step 1: Create a Telegram Bot")
    print("=" * 40)
    
    print("""
1. Open Telegram and search for @BotFather
2. Send /start to BotFather
3. Send /newbot to create a new bot
4. Choose a name for your bot (e.g., "Crypto Sniper Bot")
5. Choose a username (must end with 'bot', e.g., "crypto_sniper_bot")
6. BotFather will give you a token like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
""")
    
    token = get_user_input("Enter your bot token")
    
    if not token:
        print("❌ Bot token is required")
        return None
    
    # Validate token format
    if not token.count(':') == 1:
        print("❌ Invalid token format. Should be like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return None
    
    return token

def get_chat_id(token):
    """Get chat ID using the bot token"""
    print("\n📋 Step 2: Get Chat ID")
    print("=" * 40)
    
    print("""
1. Start a chat with your bot (search for your bot's username)
2. Send any message to your bot (e.g., "Hello")
3. The script will try to get your chat ID automatically
""")
    
    input("Press Enter when you've sent a message to your bot...")
    
    try:
        # Get updates from Telegram
        response = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok'] and data['result']:
                # Get the latest message
                latest_message = data['result'][-1]
                chat_id = latest_message['message']['chat']['id']
                chat_type = latest_message['message']['chat']['type']
                chat_title = latest_message['message']['chat'].get('title', 'Private Chat')
                
                print(f"✅ Found chat: {chat_title} (ID: {chat_id})")
                return chat_id
            else:
                print("❌ No messages found. Please send a message to your bot first.")
                return None
        else:
            print(f"❌ Failed to get updates: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

def test_telegram_connection(token, chat_id):
    """Test the Telegram connection"""
    print("\n🧪 Step 3: Test Connection")
    print("=" * 40)
    
    try:
        # Test bot info
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: @{bot_info['result']['username']}")
        else:
            print("❌ Invalid bot token")
            return False
        
        # Test message sending
        test_message = """🤖 Crypto Sniper Bot - Connection Test

✅ Bot successfully connected!
⏰ Time: {time}
📊 Status: Ready to send signals

This bot will send you real-time crypto trading signals with:
• Entry/Exit prices
• Stop Loss & Take Profit levels
• Risk/Reward ratios
• Technical analysis details

⚠️ Remember: This is for educational purposes only.
""".format(time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
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
            print("📱 Check your Telegram for the test message")
            return True
        else:
            print(f"❌ Failed to send message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def save_to_env(token, chat_id):
    """Save credentials to .env file"""
    print("\n💾 Step 4: Save Configuration")
    print("=" * 40)
    
    env_file = Path(".env")
    
    # Read existing .env content
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Update or add Telegram credentials
    lines = env_content.split('\n')
    updated_lines = []
    telegram_token_found = False
    telegram_chat_found = False
    
    for line in lines:
        if line.startswith('TELEGRAM_TOKEN='):
            updated_lines.append(f'TELEGRAM_TOKEN={token}')
            telegram_token_found = True
        elif line.startswith('TELEGRAM_CHAT_ID='):
            updated_lines.append(f'TELEGRAM_CHAT_ID={chat_id}')
            telegram_chat_found = True
        else:
            updated_lines.append(line)
    
    # Add if not found
    if not telegram_token_found:
        updated_lines.append(f'TELEGRAM_TOKEN={token}')
    if not telegram_chat_found:
        updated_lines.append(f'TELEGRAM_CHAT_ID={chat_id}')
    
    # Write back to file
    try:
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        print("✅ Configuration saved to .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def show_manual_setup():
    """Show manual setup instructions"""
    print("""
📋 Manual Setup Instructions:
============================

If the automatic setup doesn't work, you can set up manually:

1. Create a Telegram Bot:
   - Message @BotFather on Telegram
   - Send /newbot
   - Choose a name and username
   - Copy the token

2. Get Chat ID:
   - Message your bot
   - Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   - Copy the 'chat_id' from the response

3. Edit .env file:
   TELEGRAM_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here

4. Test: python test_bot.py
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check if already configured
    existing_token = os.getenv("TELEGRAM_TOKEN")
    existing_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if existing_token and existing_chat_id:
        print(f"✅ Telegram already configured:")
        print(f"   Bot: {existing_token[:10]}...")
        print(f"   Chat ID: {existing_chat_id}")
        
        choice = get_user_input("Do you want to reconfigure? (y/N)", "N").lower()
        if choice != 'y':
            print("Keeping existing configuration.")
            return
    
    print("Let's set up your Telegram bot step by step...")
    
    # Step 1: Get bot token
    token = create_telegram_bot()
    if not token:
        print("❌ Bot token is required. Please try again.")
        show_manual_setup()
        return
    
    # Step 2: Get chat ID
    chat_id = get_chat_id(token)
    if not chat_id:
        print("❌ Could not get chat ID. Please try again.")
        show_manual_setup()
        return
    
    # Step 3: Test connection
    if not test_telegram_connection(token, chat_id):
        print("❌ Connection test failed. Please check your credentials.")
        show_manual_setup()
        return
    
    # Step 4: Save configuration
    if not save_to_env(token, chat_id):
        print("❌ Failed to save configuration.")
        return
    
    print("\n🎉 Telegram setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python test_bot.py")
    print("2. Start bot: python main.py")
    print("3. Visit: http://localhost:5000/admin")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)