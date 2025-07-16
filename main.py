import os
import time
import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Third-party imports
import ccxt
import pandas as pd
import numpy as np
import ta
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from dotenv import load_dotenv

# Local imports
from config import Config
from utils import TechnicalAnalysis, SignalGenerator, DataValidator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL), format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class CryptoSniperBot:
    def __init__(self):
        self.app = Flask(__name__)
        self.scheduler = BackgroundScheduler()
        
        # Validate configuration
        if not Config.validate():
            raise ValueError("Invalid configuration. Please check your environment variables.")
        
        # Configuration from Config class
        self.TELEGRAM_TOKEN = Config.TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = Config.TELEGRAM_CHAT_ID
        self.BINANCE_API_KEY = Config.BINANCE_API_KEY
        self.BINANCE_SECRET_KEY = Config.BINANCE_SECRET_KEY
        
        # Trading pairs and timeframes
        self.SYMBOLS = Config.SYMBOLS
        self.TIMEFRAMES = Config.TIMEFRAMES
        
        # Initialize exchange
        self.exchange = self._initialize_exchange()
        
        # Store market data
        self.market_data = {}
        self.signals = []
        
        # Risk management
        self.max_risk_per_trade = Config.MAX_RISK_PER_TRADE
        self.min_risk_reward_ratio = Config.MIN_RISK_REWARD_RATIO
        
        # Initialize bot
        self._setup_routes()
        self._setup_scheduler()
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange = ccxt.binance({
                'apiKey': self.BINANCE_API_KEY,
                'secret': self.BINANCE_SECRET_KEY,
                'sandbox': Config.EXCHANGE_SANDBOX,
                'enableRateLimit': True,
            })
            logger.info("Exchange initialized successfully")
            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            return None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.app.route("/")
        def ping():
            return {"status": "Crypto Sniper Bot is Alive!", "timestamp": datetime.now().isoformat()}
        
        @self.app.route("/admin")
        def admin():
            return f"""
            <h1>🚀 Crypto Sniper Bot Admin Panel</h1>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Monitored Pairs:</strong> {len(self.SYMBOLS)}</p>
            <p><strong>Signals Generated:</strong> {len(self.signals)}</p>
            <p><strong>Last Update:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
        
        @self.app.route("/signals")
        def get_signals():
            return jsonify({
                "signals": self.signals[-10:],  # Last 10 signals
                "total_signals": len(self.signals)
            })
        
        @self.app.route("/market-data")
        def get_market_data():
            return jsonify({
                "symbols": list(self.market_data.keys()),
                "data_points": sum(len(data) for data in self.market_data.values())
            })
    
    def _setup_scheduler(self):
        """Setup background tasks"""
        self.scheduler.add_job(self.update_market_data, 'interval', minutes=Config.MARKET_DATA_UPDATE_INTERVAL)
        self.scheduler.add_job(self.analyze_markets, 'interval', minutes=Config.ANALYSIS_INTERVAL)
        self.scheduler.add_job(self.cleanup_old_data, 'interval', minutes=Config.CLEANUP_INTERVAL)
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def update_market_data(self):
        """Update market data for all symbols"""
        if not self.exchange:
            logger.error("Exchange not initialized")
            return
        
        try:
            for symbol in self.SYMBOLS:
                for timeframe in self.TIMEFRAMES:
                    try:
                        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # Clean and validate data
                        df = DataValidator.clean_data(df)
                        if not DataValidator.validate_ohlcv_data(df):
                            logger.warning(f"Invalid data for {symbol} {timeframe}")
                            continue
                        
                        if symbol not in self.market_data:
                            self.market_data[symbol] = {}
                        
                        self.market_data[symbol][timeframe] = df
                        
                    except Exception as e:
                        logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
                        
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            return TechnicalAnalysis.calculate_all_indicators(df)
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def detect_sniper_entries(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Detect sniper entry opportunities"""
        try:
            if symbol not in self.market_data or timeframe not in self.market_data[symbol]:
                return None
            
            df = self.market_data[symbol][timeframe].copy()
            if len(df) < 50:
                return None
            
            df = self.calculate_technical_indicators(df)
            
            # Use advanced signal detection
            signals = SignalGenerator.detect_sniper_entries(df)
            
            if signals:
                current = df.iloc[-1]
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "signals": [s["type"] for s in signals],
                    "price": current['close'],
                    "timestamp": current['timestamp'],
                    "rsi": current.get('rsi', 0),
                    "volume_ratio": current.get('volume_ratio', 0),
                    "price_change": current.get('price_change', 0),
                    "confidence": max([s["confidence"] for s in signals]),
                    "strength": max([s["strength"] for s in signals], key=lambda x: {"WEAK": 1, "MEDIUM": 2, "STRONG": 3}[x])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting sniper entries for {symbol}: {e}")
            return None
    
    def calculate_risk_reward(self, entry_price: float, stop_loss: float, take_profit: float) -> Dict:
        """Calculate risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        ratio = reward / risk if risk > 0 else 0
        
        return {
            "risk": risk,
            "reward": reward,
            "ratio": ratio,
            "risk_percentage": (risk / entry_price) * 100
        }
    
    def generate_trading_signal(self, sniper_data: Dict) -> Dict:
        """Generate complete trading signal"""
        try:
            symbol = sniper_data['symbol']
            price = sniper_data['price']
            
            # Calculate stop loss and take profit
            if "BULLISH" in str(sniper_data['signals']) or "RESISTANCE_BREAK" in sniper_data['signals']:
                direction = "LONG"
                stop_loss = price * 0.98  # 2% below entry
                take_profit = price * 1.04  # 4% above entry
            else:
                direction = "SHORT"
                stop_loss = price * 1.02  # 2% above entry
                take_profit = price * 0.96  # 4% below entry
            
            risk_reward = self.calculate_risk_reward(price, stop_loss, take_profit)
            
            # Only generate signal if risk-reward ratio is acceptable
            if risk_reward['ratio'] >= self.min_risk_reward_ratio:
                signal = {
                    "id": f"signal_{int(time.time())}",
                    "symbol": symbol,
                    "direction": direction,
                    "entry_price": price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "risk_reward": risk_reward,
                    "signals": sniper_data['signals'],
                    "timestamp": sniper_data['timestamp'],
                    "timeframe": sniper_data['timeframe'],
                    "confidence": len(sniper_data['signals']) * 20  # Higher confidence with more signals
                }
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return None
    
    def analyze_markets(self):
        """Analyze all markets for sniper entries"""
        logger.info("Starting market analysis...")
        
        for symbol in self.SYMBOLS:
            for timeframe in self.TIMEFRAMES:
                try:
                    sniper_data = self.detect_sniper_entries(symbol, timeframe)
                    
                    if sniper_data:
                        signal = self.generate_trading_signal(sniper_data)
                        
                        if signal:
                            self.signals.append(signal)
                            self.send_telegram_signal(signal)
                            logger.info(f"Generated signal for {symbol}: {signal['direction']}")
                
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
    
    def send_telegram_signal(self, signal: Dict):
        """Send trading signal to Telegram"""
        if not self.TELEGRAM_TOKEN or not self.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return
        
        try:
            emoji_map = {
                "LONG": "🚀",
                "SHORT": "📉",
                "RSI_OVERSOLD_REVERSAL": "🔄",
                "MACD_BULLISH_CROSS": "📈",
                "BB_SQUEEZE": "🎯",
                "VOLUME_SPIKE": "💥",
                "PRICE_MOMENTUM": "⚡",
                "RESISTANCE_BREAK": "🔥",
                "SUPPORT_BREAK": "❄️"
            }
            
            direction_emoji = emoji_map.get(signal['direction'], "📊")
            signal_emojis = [emoji_map.get(s, "•") for s in signal['signals']]
            
            message = f"""
{direction_emoji} **CRYPTO SNIPER SIGNAL** {direction_emoji}

🎯 **Symbol:** {signal['symbol']}
📊 **Direction:** {signal['direction']}
💰 **Entry Price:** ${signal['entry_price']:.4f}
🛑 **Stop Loss:** ${signal['stop_loss']:.4f}
🎯 **Take Profit:** ${signal['take_profit']:.4f}
⚖️ **Risk/Reward:** 1:{signal['risk_reward']['ratio']:.1f}
📈 **Confidence:** {signal['confidence']}%
⏰ **Timeframe:** {signal['timeframe']}
🕐 **Time:** {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

🔍 **Signals Detected:**
{chr(10).join([f"{emoji} {signal}" for emoji, signal in zip(signal_emojis, signal['signals'])])}

⚠️ **Risk Warning:** This is not financial advice. Always do your own research and manage risk properly.
            """.strip()
            
            requests.post(
                f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": self.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            logger.info(f"Telegram signal sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending Telegram signal: {e}")
    
    def cleanup_old_data(self):
        """Clean up old market data and signals"""
        try:
            # Keep only last 100 signals
            if len(self.signals) > 100:
                self.signals = self.signals[-100:]
            
            # Clean up old market data (keep last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            for symbol in self.market_data:
                for timeframe in self.market_data[symbol]:
                    df = self.market_data[symbol][timeframe]
                    df = df[df['timestamp'] > cutoff_time]
                    self.market_data[symbol][timeframe] = df
            
            logger.info("Cleaned up old data")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            # Start Flask app in a separate thread
            def run_flask():
                self.app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
            
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            
            logger.info("🚀 Crypto Sniper Bot started successfully!")
            logger.info(f"Monitoring {len(self.SYMBOLS)} symbols across {len(self.TIMEFRAMES)} timeframes")
            
            # Keep main thread alive
            while True:
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")

# Initialize and run bot
if __name__ == "__main__":
    bot = CryptoSniperBot()
    bot.run()
