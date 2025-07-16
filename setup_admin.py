#!/usr/bin/env python3
"""
Admin Dashboard Setup Script for Crypto Sniper Pro Bot
"""

import os
import sys
import getpass
from dotenv import load_dotenv

def setup_admin_dashboard():
    """Setup admin dashboard with Telegram authentication"""
    
    print("🚀 CryptoSniperXProBot - Admin Dashboard Setup")
    print("=" * 50)
    
    # Load existing environment variables
    load_dotenv()
    
    # Check if Telegram credentials exist
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print("\n📱 Telegram Authentication Setup")
    print("-" * 30)
    
    if telegram_token and telegram_chat_id:
        print("✅ Telegram credentials found in environment variables")
        print(f"Bot Token: {telegram_token[:10]}...")
        print(f"Chat ID: {telegram_chat_id}")
        
        choice = input("\nDo you want to update these credentials? (y/N): ").lower()
        if choice != 'y':
            print("Using existing credentials...")
        else:
            telegram_token = None
            telegram_chat_id = None
    else:
        print("❌ No Telegram credentials found")
    
    # Get Telegram credentials
    if not telegram_token:
        print("\n🔧 Setting up Telegram Bot Token:")
        print("1. Go to @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the bot token")
        
        telegram_token = getpass.getpass("Enter your Telegram bot token: ").strip()
        
        if not telegram_token:
            print("❌ Bot token is required!")
            return False
    
    if not telegram_chat_id:
        print("\n🔧 Setting up Telegram Chat ID:")
        print("1. Start a chat with your bot")
        print("2. Send any message to the bot")
        print("3. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
        print("4. Find your chat_id in the response")
        
        telegram_chat_id = input("Enter your Telegram chat ID: ").strip()
        
        if not telegram_chat_id:
            print("❌ Chat ID is required!")
            return False
    
    # Test Telegram connection
    print("\n🧪 Testing Telegram connection...")
    try:
        import requests
        test_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        test_data = {
            "chat_id": telegram_chat_id,
            "text": "🔧 Admin Dashboard setup test - Connection successful!"
        }
        response = requests.post(test_url, json=test_data)
        
        if response.status_code == 200:
            print("✅ Telegram connection successful!")
        else:
            print(f"❌ Telegram connection failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram connection error: {e}")
        return False
    
    # Set admin secret key
    admin_secret = os.environ.get('ADMIN_SECRET_KEY')
    if not admin_secret:
        print("\n🔐 Setting up Admin Secret Key:")
        print("This is used to secure the admin dashboard sessions")
        
        import secrets
        admin_secret = secrets.token_hex(32)
        print(f"Generated secret key: {admin_secret[:16]}...")
    
    # Update .env file
    print("\n💾 Updating environment variables...")
    
    env_content = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.readlines()
    
    # Update or add Telegram credentials
    updated_vars = {
        'TELEGRAM_BOT_TOKEN': telegram_token,
        'TELEGRAM_CHAT_ID': telegram_chat_id,
        'ADMIN_SECRET_KEY': admin_secret
    }
    
    # Remove existing variables
    env_content = [line for line in env_content 
                   if not line.startswith(('TELEGRAM_BOT_TOKEN=', 'TELEGRAM_CHAT_ID=', 'ADMIN_SECRET_KEY='))]
    
    # Add new variables
    for key, value in updated_vars.items():
        env_content.append(f"{key}={value}\n")
    
    # Write updated .env file
    with open('.env', 'w') as f:
        f.writelines(env_content)
    
    print("✅ Environment variables updated successfully!")
    
    # Create admin dashboard startup script
    print("\n📝 Creating admin dashboard startup script...")
    
    startup_script = """#!/usr/bin/env python3
\"\"\"
Admin Dashboard Startup Script
\"\"\"

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required variables
required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'ADMIN_SECRET_KEY']
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please run setup_admin.py first")
    sys.exit(1)

# Import and start admin dashboard
try:
    from admin_dashboard import AdminDashboard
    from main import CryptoSniperBot
    
    print("🚀 Starting CryptoSniperXProBot with Admin Dashboard...")
    
    # Initialize bot
    bot = CryptoSniperBot()
    
    # Start admin dashboard
    print("🔧 Starting admin dashboard...")
    admin_dashboard = AdminDashboard(bot)
    
    # Run admin dashboard
    admin_dashboard.run(host='0.0.0.0', port=5000, debug=False)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting admin dashboard: {e}")
    sys.exit(1)
"""
    
    with open('start_admin.py', 'w') as f:
        f.write(startup_script)
    
    # Make script executable
    os.chmod('start_admin.py', 0o755)
    
    print("✅ Admin dashboard startup script created: start_admin.py")
    
    # Print next steps
    print("\n🎉 Admin Dashboard Setup Complete!")
    print("=" * 40)
    print("\n📋 Next Steps:")
    print("1. Start the admin dashboard:")
    print("   python start_admin.py")
    print("\n2. Access the admin panel:")
    print("   http://localhost:5000/admin")
    print("\n3. Login with your Telegram credentials")
    print("\n4. Monitor and manage your bot from the dashboard")
    
    print("\n🔧 Admin Dashboard Features:")
    print("• Real-time bot status monitoring")
    print("• Telegram connection management")
    print("• Auto-reconnect and auto-cleanup systems")
    print("• Error detection and auto-repair")
    print("• Performance tracking and analytics")
    print("• System health monitoring")
    
    return True

def main():
    """Main setup function"""
    try:
        success = setup_admin_dashboard()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()