#!/usr/bin/env python3
"""
Test Alert Script for CryptoSniperXProBot
Sends a test alert to verify Telegram integration
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_alert():
    """Send a test alert to Telegram"""
    
    # Get credentials from environment
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not found in .env file")
        return False
    
    try:
        # Test message
        message = f"""
🚀 **CRYPTOSNIPERXPRO BOT TEST ALERT** 🚀

✅ **Bot Status**: ONLINE
📊 **Test Type**: Telegram Integration Test
⏰ **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 **Purpose**: Verify Telegram connection

🔍 **System Check**:
• ✅ Telegram Bot Token: Configured
• ✅ Chat ID: Configured
• ✅ Connection: Testing...

💰 **Advanced Features Available**:
• Multi-exchange arbitrage detection (40+ exchanges)
• Newly listed coin monitoring
• Deposit/withdrawal verification
• Bad trade protection
• Risk scoring and filtering
• Real-time monitoring
• Fee calculation and net profit analysis
• Execution speed optimization

📈 **Ready for Trading Signals!**

⚠️ **Note**: This is a test message. Real trading signals will be sent automatically when opportunities are detected.

🎉 **CryptoSniperXProBot is ready for action!**
        """.strip()
        
        # Send message
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ Test alert sent successfully!")
            print(f"📱 Message sent to chat ID: {TELEGRAM_CHAT_ID}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"❌ Error sending message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_arbitrage_test_alert():
    """Send a test arbitrage alert"""
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    try:
        # Test arbitrage message
        message = f"""
💰 **CRYPTOSNIPERXPRO ARBITRAGE TEST** 💰

🎯 **Symbol**: BTC/USDT
📊 **Buy Exchange**: BINANCE
📈 **Sell Exchange**: BYBIT
💵 **Buy Price**: $50,000.00
💸 **Sell Price**: $50,100.00
📈 **Net Profit**: 0.15%
⏰ **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 **Arbitrage Analysis**:
• Price Difference: $100.00
• Gross Profit: 0.20%
• Net Profit: 0.15%
• Risk Score: 0.30
• Execution Speed: 0.80
• Volume: 5000.00

⚠️ **Important**: 
• Execute quickly as arbitrage opportunities disappear fast
• Consider trading fees in profit calculation
• Monitor for slippage during execution
• Check deposit/withdrawal status before trading

⚠️ **Risk Warning**: This is a test message. Not financial advice.
        """.strip()
        
        # Send message
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ Arbitrage test alert sent successfully!")
            return True
        else:
            print(f"❌ Error sending arbitrage alert: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 CryptoSniperXProBot - Telegram Test Alert")
    print("=" * 50)
    
    # Send basic test alert
    print("\n📱 Sending basic test alert...")
    success1 = send_test_alert()
    
    # Send arbitrage test alert
    print("\n💰 Sending arbitrage test alert...")
    success2 = send_arbitrage_test_alert()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if success1 and success2:
        print("✅ All test alerts sent successfully!")
        print("🎉 Your Telegram integration is working perfectly!")
        print("\n🚀 Your bot is ready to receive real trading signals!")
    else:
        print("❌ Some test alerts failed. Please check your configuration.")
    
    return success1 and success2

if __name__ == "__main__":
    main()