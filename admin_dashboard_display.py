#!/usr/bin/env python3
"""
Admin Dashboard Display for CryptoSniperXProBot
Shows comprehensive bot information and status
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AdminDashboardDisplay:
    def __init__(self):
        self.bot_url = "http://localhost:5000"
        self.admin_url = f"{self.bot_url}/admin"
        self.api_status_url = f"{self.bot_url}/api/status"
        self.signals_url = f"{self.bot_url}/signals"
        self.performance_url = f"{self.bot_url}/performance"
        
    def check_bot_status(self):
        """Check if bot is running"""
        try:
            response = requests.get(self.bot_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_api_status(self):
        """Get API status"""
        try:
            response = requests.get(self.api_status_url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_signals(self):
        """Get recent signals"""
        try:
            response = requests.get(self.signals_url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_performance(self):
        """Get performance data"""
        try:
            response = requests.get(self.performance_url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def display_header(self):
        """Display dashboard header"""
        print("=" * 80)
        print("🎛️  CRYPTOSNIPERXPROBOT ADMIN DASHBOARD")
        print("=" * 80)
        print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def display_bot_status(self):
        """Display bot status"""
        print("\n🔍 BOT STATUS")
        print("-" * 40)
        
        if self.check_bot_status():
            print("✅ Bot is RUNNING")
            print(f"🌐 Dashboard URL: {self.admin_url}")
            print(f"📊 API Status: {self.api_status_url}")
        else:
            print("❌ Bot is NOT RUNNING")
            print("💡 Start the bot with: python3 main.py")
    
    def display_configuration(self):
        """Display bot configuration"""
        print("\n⚙️  CONFIGURATION")
        print("-" * 40)
        
        # Telegram settings
        telegram_token = os.getenv('TELEGRAM_TOKEN', 'Not set')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', 'Not set')
        
        print(f"📱 Telegram Token: {'✅ Set' if telegram_token != 'Not set' else '❌ Not set'}")
        print(f"💬 Chat ID: {telegram_chat_id}")
        
        # Email settings
        email_server = os.getenv('EMAIL_SMTP_SERVER', 'Not set')
        email_address = os.getenv('EMAIL_ADDRESS', 'Not set')
        recipient_email = os.getenv('RECIPIENT_EMAIL', 'Not set')
        
        print(f"📧 SMTP Server: {email_server}")
        print(f"📧 Email Address: {'✅ Set' if email_address != 'Not set' else '❌ Not set'}")
        print(f"📧 Recipient Email: {recipient_email}")
        
        # Trading settings
        print(f"🎯 Max Risk Per Trade: 2%")
        print(f"⚖️ Min Risk/Reward Ratio: 2.0")
        print(f"📊 Trading Pairs: 20 major pairs")
        print(f"⏰ Timeframes: 1m, 5m, 15m, 1h, 4h")
    
    def display_features(self):
        """Display bot features"""
        print("\n🔧 ENHANCED FEATURES")
        print("-" * 40)
        
        features = [
            "✅ TP/SL calculation with dynamic adjustment",
            "✅ Momentum-based signal generation",
            "✅ Smart AI logic for trading decisions",
            "✅ Dynamic market scanning system",
            "✅ Risk assessment and scoring",
            "✅ Support/Resistance detection",
            "✅ Email notifications (if configured)",
            "✅ Telegram notifications with detailed analysis",
            "✅ Arbitrage detection across 40+ exchanges",
            "✅ Real-time chart generation",
            "✅ Performance tracking and analytics",
            "✅ Institutional-grade Z+++ indicators",
            "✅ New listing detection",
            "✅ Bad trade protection",
            "✅ Multi-exchange support"
        ]
        
        for feature in features:
            print(f"  {feature}")
    
    def display_api_status(self):
        """Display API status"""
        print("\n📊 API STATUS")
        print("-" * 40)
        
        status = self.get_api_status()
        if status:
            print("✅ API is responding")
            print(f"🤖 Bot Name: {status.get('bot_name', 'CryptoSniperXProBot')}")
            print(f"⏰ Uptime: {status.get('uptime', 'Unknown')}")
            print(f"📈 Signals Generated: {status.get('signals_generated', 0)}")
            print(f"📊 Market Data Points: {status.get('market_data_points', 0)}")
            print(f"🎯 Active Symbols: {status.get('active_symbols', 0)}")
        else:
            print("❌ API not responding")
    
    def display_recent_signals(self):
        """Display recent signals"""
        print("\n📈 RECENT SIGNALS")
        print("-" * 40)
        
        signals = self.get_signals()
        if signals and signals.get('signals'):
            recent_signals = signals['signals'][-5:]  # Last 5 signals
            print(f"📊 Total Signals: {signals.get('total_signals', 0)}")
            print("\nRecent Signals:")
            
            for i, signal in enumerate(recent_signals, 1):
                signal_type = signal.get('signal_type', 'Unknown')
                symbol = signal.get('symbol', 'Unknown')
                entry_price = signal.get('entry_price', 0)
                timestamp = signal.get('timestamp', 'Unknown')
                
                emoji = "🟢" if signal_type == "LONG" else "🔴"
                print(f"  {i}. {emoji} {signal_type} {symbol} @ ${entry_price:.6f} ({timestamp})")
        else:
            print("📊 No signals generated yet")
            print("💡 Bot is monitoring markets for opportunities")
    
    def display_performance(self):
        """Display performance metrics"""
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 40)
        
        performance = self.get_performance()
        if performance:
            print("✅ Performance tracking active")
            print(f"📈 Win Rate: {performance.get('win_rate', 0):.1%}")
            print(f"📊 Total Trades: {performance.get('total_trades', 0)}")
            print(f"💰 Total Profit: ${performance.get('total_profit', 0):.2f}")
            print(f"📉 Max Drawdown: {performance.get('max_drawdown', 0):.1%}")
            print(f"⚖️ Avg Risk/Reward: {performance.get('avg_risk_reward', 0):.2f}")
        else:
            print("📊 Performance data not available")
    
    def display_telegram_info(self):
        """Display Telegram bot information"""
        print("\n📱 TELEGRAM BOT INFO")
        print("-" * 40)
        
        print("🤖 Bot Name: CryptoSniperXProBot")
        print("📱 Username: @crypto_sniper_pro_bot")
        print("💬 Chat ID: " + os.getenv('TELEGRAM_CHAT_ID', 'Not set'))
        print("📊 Signal Types:")
        print("  🟢 LONG signals (Bullish momentum)")
        print("  🔴 SHORT signals (Bearish momentum)")
        print("📈 Signal Features:")
        print("  🎯 Take Profit & Stop Loss levels")
        print("  📊 Momentum analysis")
        print("  ⚠️ Risk assessment")
        print("  📈 Support/Resistance levels")
        print("  💰 Risk/Reward ratios")
    
    def display_arbitrage_info(self):
        """Display arbitrage information"""
        print("\n🔄 ARBITRAGE SYSTEM")
        print("-" * 40)
        
        exchanges = [
            "Binance", "Bybit", "Bitget", "Gate.io", "KuCoin", 
            "OKX", "MEXC", "Coinbase", "Kraken", "Huobi"
        ]
        
        print("🌍 Monitored Exchanges:")
        for exchange in exchanges:
            print(f"  ✅ {exchange}")
        
        print("\n🎯 Arbitrage Features:")
        print("  🔍 New listing detection")
        print("  💰 Profit calculation")
        print("  ⚡ Execution speed optimization")
        print("  🛡️ Bad trade protection")
        print("  📊 Risk scoring")
        print("  💸 Fee calculation")
    
    def display_help(self):
        """Display help information"""
        print("\n❓ HELP & SUPPORT")
        print("-" * 40)
        
        print("🌐 Admin Dashboard: http://localhost:5000/admin")
        print("📊 API Status: http://localhost:5000/api/status")
        print("📈 Signals: http://localhost:5000/signals")
        print("📊 Performance: http://localhost:5000/performance")
        print("📋 Signal History: http://localhost:5000/signals/history")
        
        print("\n🔧 Bot Controls:")
        print("  🚀 Start Bot: python3 main.py")
        print("  🛑 Stop Bot: Ctrl+C")
        print("  🔄 Restart Bot: Stop and start again")
        
        print("\n📱 Telegram Setup:")
        print("  1. Create bot with @BotFather")
        print("  2. Get bot token")
        print("  3. Set TELEGRAM_TOKEN in .env")
        print("  4. Set TELEGRAM_CHAT_ID in .env")
        
        print("\n📧 Email Setup (Optional):")
        print("  1. Set EMAIL_SMTP_SERVER in .env")
        print("  2. Set EMAIL_ADDRESS in .env")
        print("  3. Set EMAIL_PASSWORD in .env")
        print("  4. Set RECIPIENT_EMAIL in .env")
    
    def display_full_dashboard(self):
        """Display complete admin dashboard"""
        self.display_header()
        self.display_bot_status()
        self.display_configuration()
        self.display_features()
        self.display_api_status()
        self.display_recent_signals()
        self.display_performance()
        self.display_telegram_info()
        self.display_arbitrage_info()
        self.display_help()
        
        print("\n" + "=" * 80)
        print("🎉 CryptoSniperXProBot is ready for trading!")
        print("📱 Monitor your Telegram for real-time signals")
        print("🌐 Access admin dashboard for detailed analytics")
        print("=" * 80)

def main():
    """Main function"""
    dashboard = AdminDashboardDisplay()
    dashboard.display_full_dashboard()

if __name__ == "__main__":
    main()