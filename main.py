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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoSniperBot:
    def __init__(self):
        self.app = Flask(__name__)
        self.scheduler = BackgroundScheduler()
        
        # Configuration
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
        
        # Trading pairs to monitor
        self.SYMBOLS = [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", 
            "ADA/USDT", "DOT/USDT", "LINK/USDT", "MATIC/USDT",
            "AVAX/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT"
        ]
        
        # Timeframes for analysis
        self.TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]
        
        # Initialize exchange
        self.exchange = self._initialize_exchange()
        
        # Store market data
        self.market_data = {}
        self.signals = []
        
        # Risk management
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.min_risk_reward_ratio = 2.0
        
        # Initialize bot
        self._setup_routes()
        self._setup_scheduler()
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange = ccxt.binance({
                'apiKey': self.BINANCE_API_KEY,
                'secret': self.BINANCE_SECRET_KEY,
                'sandbox': False,  # Set to True for testing
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
        self.scheduler.add_job(self.update_market_data, 'interval', minutes=1)
        self.scheduler.add_job(self.analyze_markets, 'interval', minutes=5)
        self.scheduler.add_job(self.cleanup_old_data, 'interval', hours=1)
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
                        
                        if symbol not in self.market_data:
                            self.market_data[symbol] = {}
                        
                        self.market_data[symbol][timeframe] = df
                        
                    except Exception as e:
                        logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
                        
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        try:
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_middle'] = bb.bollinger_mavg()
            
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price action
            df['price_change'] = df['close'].pct_change()
            df['price_change_ma'] = df['price_change'].rolling(window=20).mean()
            
            return df
            
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
            
            # Get latest data
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Sniper entry conditions
            signals = []
            
            # 1. RSI oversold/overbought reversal
            if current['rsi'] < 30 and prev['rsi'] >= 30:
                signals.append("RSI_OVERSOLD_REVERSAL")
            elif current['rsi'] > 70 and prev['rsi'] <= 70:
                signals.append("RSI_OVERBOUGHT_REVERSAL")
            
            # 2. MACD crossover
            if (current['macd'] > current['macd_signal'] and 
                prev['macd'] <= prev['macd_signal']):
                signals.append("MACD_BULLISH_CROSS")
            elif (current['macd'] < current['macd_signal'] and 
                  prev['macd'] >= prev['macd_signal']):
                signals.append("MACD_BEARISH_CROSS")
            
            # 3. Bollinger Band squeeze
            bb_width = (current['bb_upper'] - current['bb_lower']) / current['bb_middle']
            if bb_width < 0.1:  # Tight squeeze
                signals.append("BB_SQUEEZE")
            
            # 4. Volume spike
            if current['volume_ratio'] > 2.0:
                signals.append("VOLUME_SPIKE")
            
            # 5. Price momentum
            if current['price_change'] > 0.02:  # 2% price increase
                signals.append("PRICE_MOMENTUM")
            
            # 6. Support/Resistance break
            if current['close'] > current['bb_upper']:
                signals.append("RESISTANCE_BREAK")
            elif current['close'] < current['bb_lower']:
                signals.append("SUPPORT_BREAK")
            
            if signals:
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "signals": signals,
                    "price": current['close'],
                    "timestamp": current['timestamp'],
                    "rsi": current['rsi'],
                    "volume_ratio": current['volume_ratio'],
                    "price_change": current['price_change']
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
