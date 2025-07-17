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
from performance import PerformanceTracker, PerformanceAnalyzer
from admin_dashboard import AdminDashboard
from advanced_indicators import InstitutionalZPlusPlus
from chart_generator import ChartGenerator
from advanced_arbitrage import AdvancedArbitrage
from enhanced_trading_signals import EnhancedTradingSignals

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
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        self.start_time = datetime.now()
        
        # Signal tracking
        self.signal_cooldowns = {}  # Track signal cooldowns per symbol
        self.signal_count = 0  # Track total signals generated
        
        # Bot health tracking
        self.is_running = True
        self.start_time = datetime.now()
        
        # Advanced Z+++ indicators
        self.z_plus_plus = InstitutionalZPlusPlus()
        
        # Chart generator
        self.chart_generator = ChartGenerator()
        
        # Advanced arbitrage system
        self.arbitrage_system = AdvancedArbitrage()
        
        # Enhanced trading signals system
        self.enhanced_signals = EnhancedTradingSignals()
        
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
        # Initialize admin dashboard
        self.admin_dashboard = AdminDashboard(self)
        
        @self.app.route("/")
        def ping():
            return {"status": f"{Config.BOT_NAME} is Alive!", "timestamp": datetime.now().isoformat()}
        
        @self.app.route("/admin")
        def admin():
            return redirect("/admin/login")
        
        @self.app.route("/admin/login")
        def admin_login():
            return self.admin_dashboard._render_login_page()
        
        @self.app.route("/admin/dashboard")
        def admin_dashboard():
            return self.admin_dashboard._render_dashboard()
        
        @self.app.route("/api/status")
        def api_status():
            return jsonify(self.admin_dashboard._get_system_status())
        
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
        
        @self.app.route("/performance")
        def get_performance():
            stats = self.performance_tracker.get_performance_stats(30)
            return jsonify(stats)
        
        @self.app.route("/signals/history")
        def get_signal_history():
            limit = request.args.get('limit', 50, type=int)
            history = self.performance_tracker.get_signal_history(limit)
            return jsonify(history)
    
    def _setup_scheduler(self):
        """Setup background tasks"""
        self.scheduler.add_job(self.update_market_data, 'interval', minutes=Config.MARKET_DATA_UPDATE_INTERVAL)
        self.scheduler.add_job(self.analyze_markets, 'interval', minutes=Config.ANALYSIS_INTERVAL)
        self.scheduler.add_job(self.monitor_arbitrage, 'interval', minutes=1)  # Check arbitrage every minute
        self.scheduler.add_job(self.monitor_enhanced_signals, 'interval', minutes=2)  # Check enhanced signals every 2 minutes
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
            
            # Check signal cooldown
            if symbol in self.signal_cooldowns:
                last_signal_time = self.signal_cooldowns[symbol]
                time_since_last = (datetime.now() - last_signal_time).total_seconds() / 60
                if time_since_last < Config.SIGNAL_COOLDOWN_MINUTES:
                    return None
            
            # Get ATR for dynamic risk calculation
            df = self.market_data[symbol][sniper_data['timeframe']]
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else price * 0.02
            
            # Determine direction based on signals
            bullish_signals = Config.SIGNAL_TYPES["LONG"]
            
            if any(signal in sniper_data['signals'] for signal in bullish_signals):
                direction = "LONG"
            else:
                direction = "SHORT"
            
            # Calculate dynamic risk levels using ATR
            risk_levels = SignalGenerator.calculate_risk_levels(price, atr, direction)
            
            # Only generate signal if risk-reward ratio is acceptable and confidence is high enough
            if (risk_levels.get('ratio', 0) >= self.min_risk_reward_ratio and 
                sniper_data.get('confidence', 0) >= Config.MIN_CONFIDENCE):
                
                signal = {
                    "id": f"signal_{int(time.time())}",
                    "symbol": symbol,
                    "direction": direction,
                    "entry_price": price,
                    "stop_loss": risk_levels['stop_loss'],
                    "take_profit": risk_levels['take_profit'],
                    "risk_reward": risk_levels,
                    "signals": sniper_data['signals'],
                    "timestamp": sniper_data['timestamp'],
                    "timeframe": sniper_data['timeframe'],
                    "confidence": sniper_data.get('confidence', 0),
                    "strength": sniper_data.get('strength', 'MEDIUM')
                }
                
                # Update cooldown
                self.signal_cooldowns[symbol] = datetime.now()
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return None
    
    def analyze_markets(self):
        """Analyze all markets for sniper entries with Z+++ indicators"""
        logger.info("Starting advanced market analysis with Z+++ indicators...")
        
        # Get all types of signals
        all_signals = self.z_plus_plus.get_all_signals()
        
        # Process momentum signals
        for signal in all_signals.get('momentum_signals', []):
            if self._validate_signal(signal):
                self._process_advanced_signal(signal)
        
        # Process sentiment signals
        for signal in all_signals.get('sentiment_signals', []):
            if self._validate_signal(signal):
                self._process_advanced_signal(signal)
        
        # Process arbitrage signals
        for signal in all_signals.get('arbitrage_signals', []):
            if self._validate_arbitrage_signal(signal):
                self._process_arbitrage_signal(signal)
        
        # Traditional analysis for backup
        for symbol in self.SYMBOLS:
            for timeframe in self.TIMEFRAMES:
                try:
                    sniper_data = self.detect_sniper_entries(symbol, timeframe)
                    
                    if sniper_data:
                        signal = self.generate_trading_signal(sniper_data)
                        
                        if signal:
                            self.signals.append(signal)
                            self.signal_count += 1
                            
                            # Record signal in performance tracker
                            if Config.ENABLE_PERFORMANCE_TRACKING:
                                self.performance_tracker.record_signal(signal)
                            
                            self.send_telegram_signal(signal)
                            logger.info(f"Generated traditional signal for {symbol}: {signal['direction']}")
                
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Validate advanced signal"""
        try:
            # Check if signal is recent (within last 5 minutes)
            signal_time = signal.get('timestamp', datetime.now())
            if isinstance(signal_time, str):
                signal_time = datetime.fromisoformat(signal_time.replace('Z', '+00:00'))
            
            time_diff = (datetime.now() - signal_time).total_seconds() / 60
            if time_diff > 5:
                return False
            
            # Check confidence
            if signal.get('confidence', 0) < 70:
                return False
            
            # Check if already processed
            signal_id = f"{signal['symbol']}_{signal['type']}_{signal_time.strftime('%Y%m%d_%H%M')}"
            if signal_id in self.signal_cooldowns:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def _validate_arbitrage_signal(self, signal: Dict) -> bool:
        """Validate arbitrage signal"""
        try:
            # Check profit percentage
            if signal.get('profit_pct', 0) < 0.5:
                return False
            
            # Check if recent
            signal_time = signal.get('timestamp', datetime.now())
            if isinstance(signal_time, str):
                signal_time = datetime.fromisoformat(signal_time.replace('Z', '+00:00'))
            
            time_diff = (datetime.now() - signal_time).total_seconds() / 60
            if time_diff > 2:  # Arbitrage signals must be very recent
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating arbitrage signal: {e}")
            return False
    
    def _process_advanced_signal(self, signal: Dict):
        """Process advanced signal with chart"""
        try:
            # Get market data for chart
            exchange = signal.get('exchange', 'binance')
            symbol = signal['symbol']
            
            if exchange in self.z_plus_plus.market_data and symbol in self.z_plus_plus.market_data[exchange]:
                df = self.z_plus_plus.market_data[exchange][symbol]
                
                # Generate chart
                chart_image = self.chart_generator.generate_signal_chart(symbol, df, signal)
                
                # Add chart to signal
                signal['chart_image'] = chart_image
                
                # Add to signals list
                self.signals.append(signal)
                self.signal_count += 1
                
                # Record in performance tracker
                if Config.ENABLE_PERFORMANCE_TRACKING:
                    self.performance_tracker.record_signal(signal)
                
                # Send to Telegram
                self.send_advanced_telegram_signal(signal)
                
                # Update cooldown
                signal_id = f"{signal['symbol']}_{signal['type']}_{signal['timestamp'].strftime('%Y%m%d_%H%M')}"
                self.signal_cooldowns[signal_id] = datetime.now()
                
                logger.info(f"Generated advanced signal for {symbol}: {signal['type']}")
            
        except Exception as e:
            logger.error(f"Error processing advanced signal: {e}")
    
    def _process_arbitrage_signal(self, signal: Dict):
        """Process arbitrage signal"""
        try:
            # Generate arbitrage chart
            chart_image = self.chart_generator.generate_arbitrage_chart(signal)
            signal['chart_image'] = chart_image
            
            # Add to signals list
            self.signals.append(signal)
            self.signal_count += 1
            
            # Send to Telegram
            self.send_arbitrage_telegram_signal(signal)
            
            logger.info(f"Generated arbitrage signal for {signal['symbol']}: {signal['profit_pct']:.2f}% profit")
            
        except Exception as e:
            logger.error(f"Error processing arbitrage signal: {e}")
    
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
{direction_emoji} **CRYPTOSNIPERXPRO SIGNAL** {direction_emoji}

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
    
    def send_advanced_telegram_signal(self, signal: Dict):
        """Send advanced signal to Telegram with chart"""
        if not self.TELEGRAM_TOKEN or not self.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return
        
        try:
            emoji_map = {
                "MOMENTUM_LONG": "🚀",
                "SENTIMENT_LONG": "📈",
                "MOMENTUM_SHORT": "📉",
                "SENTIMENT_SHORT": "🔻"
            }
            
            signal_emoji = emoji_map.get(signal['type'], "📊")
            
            message = f"""
{signal_emoji} **CRYPTOSNIPERXPRO ADVANCED SIGNAL** {signal_emoji}

🎯 **Symbol:** {signal['symbol']}
📊 **Type:** {signal['type']}
💰 **Price:** ${signal['price']:.4f}
📈 **Confidence:** {signal['confidence']}%
⚡ **Strength:** {signal['strength']}
⏰ **Time:** {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

🔍 **Z+++ Analysis:**
• Momentum Score: {signal.get('indicators', {}).get('momentum_score', 0):.3f}
• Trend Strength: {signal.get('indicators', {}).get('trend_strength', 0):.3f}
• Volume Score: {signal.get('indicators', {}).get('volume_score', 0):.3f}
• Overall Score: {signal.get('indicators', {}).get('overall_score', 0):.3f}

⚠️ **Risk Warning:** This is not financial advice. Always do your own research and manage risk properly.
            """.strip()
            
            # Send text message
            requests.post(
                f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": self.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            # Send chart image if available
            if signal.get('chart_image'):
                try:
                    # Convert base64 to image file
                    import base64
                    img_data = signal['chart_image'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    
                    # Send photo
                    files = {'photo': ('chart.png', img_bytes, 'image/png')}
                    requests.post(
                        f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendPhoto",
                        data={"chat_id": self.TELEGRAM_CHAT_ID},
                        files=files
                    )
                except Exception as e:
                    logger.error(f"Error sending chart image: {e}")
            
            logger.info(f"Advanced Telegram signal sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending advanced Telegram signal: {e}")
    
    def send_arbitrage_telegram_signal(self, signal: Dict):
        """Send arbitrage signal to Telegram"""
        if not self.TELEGRAM_TOKEN or not self.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return
        
        try:
            message = f"""
💰 **CRYPTOSNIPERXPRO ARBITRAGE OPPORTUNITY** 💰

🎯 **Symbol:** {signal['symbol']}
📊 **Buy Exchange:** {signal['buy_exchange'].upper()}
📈 **Sell Exchange:** {signal['sell_exchange'].upper()}
💵 **Buy Price:** ${signal['buy_price']:.4f}
💸 **Sell Price:** ${signal['sell_price']:.4f}
📈 **Net Profit:** {signal['net_profit_pct']:.2f}%
⏰ **Time:** {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

🔍 **Arbitrage Analysis:**
• Price Difference: ${signal['sell_price'] - signal['buy_price']:.4f}
• Gross Profit: {signal['gross_profit_pct']:.2f}%
• Net Profit: {signal['net_profit_pct']:.2f}%
• Risk Score: {signal['risk_score']:.2f}
• Execution Speed: {signal['execution_speed']:.2f}
• Volume: {signal['volume']:.2f}

⚠️ **Important:** 
• Execute quickly as arbitrage opportunities disappear fast
• Consider trading fees in profit calculation
• Monitor for slippage during execution
• Check deposit/withdrawal status before trading

⚠️ **Risk Warning:** This is not financial advice. Arbitrage involves execution risk.
            """.strip()
            
            # Send text message
            requests.post(
                f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": self.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            # Send chart image if available
            if signal.get('chart_image'):
                try:
                    import base64
                    img_data = signal['chart_image'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    
                    files = {'photo': ('arbitrage.png', img_bytes, 'image/png')}
                    requests.post(
                        f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendPhoto",
                        data={"chat_id": self.TELEGRAM_CHAT_ID},
                        files=files
                    )
                except Exception as e:
                    logger.error(f"Error sending arbitrage chart: {e}")
            
            logger.info(f"Arbitrage Telegram signal sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending arbitrage Telegram signal: {e}")
    
    def monitor_arbitrage(self):
        """Monitor arbitrage opportunities"""
        try:
            # Get arbitrage signals from the advanced arbitrage system
            arbitrage_signals = self.arbitrage_system.get_arbitrage_signals()
            
            for signal in arbitrage_signals:
                # Validate arbitrage signal
                if self._validate_arbitrage_signal(signal):
                    # Process arbitrage signal
                    self._process_arbitrage_signal(signal)
                    
                    # Send Telegram notification
                    self.send_arbitrage_telegram_signal(signal)
            
            # Check for newly listed coins
            new_listings = self.arbitrage_system.get_new_listings()
            if new_listings:
                for listing in new_listings:
                    self._process_new_listing(listing)
            
            # Check exchange status
            exchange_status = self.arbitrage_system.get_exchange_status()
            if exchange_status:
                self._update_exchange_status(exchange_status)
                
        except Exception as e:
            logger.error(f"Error monitoring arbitrage: {e}")
    
    def _process_new_listing(self, listing: str):
        """Process newly listed coin"""
        try:
            signal = {
                'type': 'NEW_LISTING',
                'symbol': listing,
                'timestamp': datetime.now(),
                'message': f"🚀 New listing detected: {listing}",
                'priority': 'HIGH',
                'source': 'arbitrage_system'
            }
            
            # Send Telegram notification
            self.send_telegram_signal(signal)
            
            logger.info(f"New listing processed: {listing}")
            
        except Exception as e:
            logger.error(f"Error processing new listing {listing}: {e}")
    
    def _update_exchange_status(self, status: Dict):
        """Update exchange status information"""
        try:
            for exchange, info in status.items():
                if info.get('status') != 'operational':
                    logger.warning(f"Exchange {exchange} status: {info.get('status')}")
                    
        except Exception as e:
            logger.error(f"Error updating exchange status: {e}")
    
    def monitor_enhanced_signals(self):
        """Monitor enhanced trading signals (day trading, scalping, swing trading)"""
        try:
            for symbol in self.SYMBOLS:
                for timeframe in ['1h', '4h', '15m']:  # Different timeframes for different strategies
                    try:
                        # Get market data
                        if symbol in self.market_data and timeframe in self.market_data[symbol]:
                            df = self.market_data[symbol][timeframe]
                            
                            if not df.empty and len(df) > 50:  # Ensure enough data
                                # Generate enhanced signals
                                signals = self.enhanced_signals.generate_all_signals(df, symbol)
                                
                                for signal in signals:
                                    # Validate signal
                                    if self._validate_enhanced_signal(signal):
                                        # Process enhanced signal
                                        self._process_enhanced_signal(signal)
                                        
                                        # Send Telegram notification
                                        self.send_enhanced_telegram_signal(signal)
                                        
                    except Exception as e:
                        logger.error(f"Error monitoring enhanced signals for {symbol} {timeframe}: {e}")
                        
        except Exception as e:
            logger.error(f"Error monitoring enhanced signals: {e}")
    
    def _validate_enhanced_signal(self, signal: Dict) -> bool:
        """Validate enhanced trading signal"""
        try:
            # Check required fields
            required_fields = ['type', 'signal', 'symbol', 'price', 'confidence', 'leverage']
            for field in required_fields:
                if field not in signal:
                    return False
            
            # Check confidence threshold
            if signal['confidence'] < 50:
                return False
            
            # Check if signal is recent (within last 5 minutes)
            signal_time = signal.get('timestamp', datetime.now())
            if (datetime.now() - signal_time).total_seconds() > 300:
                return False
            
            # Check cooldown
            signal_key = f"{signal['symbol']}_{signal['type']}"
            if signal_key in self.signal_cooldowns:
                last_signal_time = self.signal_cooldowns[signal_key]
                if (datetime.now() - last_signal_time).total_seconds() < 1800:  # 30 minutes cooldown
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating enhanced signal: {e}")
            return False
    
    def _process_enhanced_signal(self, signal: Dict):
        """Process enhanced trading signal"""
        try:
            # Add to signals list
            self.signals.append(signal)
            
            # Update cooldown
            signal_key = f"{signal['symbol']}_{signal['type']}"
            self.signal_cooldowns[signal_key] = datetime.now()
            
            # Track performance
            if Config.ENABLE_PERFORMANCE_TRACKING:
                self.performance_tracker.record_signal(signal)
            
            logger.info(f"Enhanced signal processed: {signal['type']} {signal['signal']} {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error processing enhanced signal: {e}")
    
    def send_enhanced_telegram_signal(self, signal: Dict):
        """Send enhanced trading signal to Telegram"""
        if not self.TELEGRAM_TOKEN or not self.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return
        
        try:
            # Signal type emoji mapping
            emoji_map = {
                'DAY_TRADING': '📈',
                'SCALPING': '⚡',
                'SWING_TRADING': '📊'
            }
            
            signal_emoji = emoji_map.get(signal['type'], '📊')
            direction_emoji = '🟢' if signal['signal'] == 'LONG' else '🔴'
            
            # Support/Resistance levels
            levels = signal.get('support_resistance', {})
            support_levels = levels.get('support_levels', {})
            resistance_levels = levels.get('resistance_levels', {})
            
            # Leverage info
            leverage_info = signal.get('leverage', {})
            
            message = f"""
{signal_emoji} **CRYPTOSNIPERXPRO {signal['type'].replace('_', ' ')} SIGNAL** {signal_emoji}

{direction_emoji} **Signal**: {signal['signal']}
🎯 **Symbol**: {signal['symbol']}
💰 **Price**: ${signal['price']:.4f}
📊 **Confidence**: {signal['confidence']}%
⏰ **Timeframe**: {signal['timeframe']}
⏰ **Time**: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

🔧 **Smart Leverage System**:
• Leverage: {leverage_info.get('leverage', 1)}x
• Level: {leverage_info.get('level', 'LOW')}
• Max Leverage: {leverage_info.get('max_leverage', 1)}x

📊 **Support Levels**:
• S1: ${support_levels.get('s1', 0):.4f}
• S2: ${support_levels.get('s2', 0):.4f}
• MA20: ${support_levels.get('ma20', 0):.4f}
• MA50: ${support_levels.get('ma50', 0):.4f}

📈 **Resistance Levels**:
• R1: ${resistance_levels.get('r1', 0):.4f}
• R2: ${resistance_levels.get('r2', 0):.4f}
• R3: ${resistance_levels.get('r3', 0):.4f}

🔍 **Technical Indicators**:
• RSI: {signal.get('indicators', {}).get('rsi', 0):.2f}
• MACD: {signal.get('indicators', {}).get('macd', 0):.4f}
• Volume Ratio: {signal.get('indicators', {}).get('volume_ratio', 0):.2f}
• BB Position: {signal.get('indicators', {}).get('bb_position', 0):.2f}

⚠️ **Risk Management**:
• Use proper position sizing
• Set stop losses based on support/resistance
• Monitor leverage levels
• Follow risk-reward ratios

⚠️ **Risk Warning**: This is not financial advice. Always do your own research and manage risk properly.
            """.strip()
            
            # Send text message
            requests.post(
                f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": self.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            # Generate and send chart if available
            if Config.ENABLE_CHART_GENERATION:
                try:
                    chart_image = self.chart_generator.generate_signal_chart(
                        signal['symbol'], signal['timeframe'], signal
                    )
                    if chart_image:
                        import base64
                        img_data = chart_image.split(',')[1]
                        img_bytes = base64.b64decode(img_data)
                        
                        files = {'photo': ('signal.png', img_bytes, 'image/png')}
                        requests.post(
                            f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendPhoto",
                            data={"chat_id": self.TELEGRAM_CHAT_ID},
                            files=files
                        )
                except Exception as e:
                    logger.error(f"Error sending chart: {e}")
            
            logger.info(f"Enhanced Telegram signal sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending enhanced Telegram signal: {e}")
    
    def cleanup_old_data(self):
        """Clean up old market data and signals"""
        try:
            # Keep only last N signals
            if len(self.signals) > Config.MAX_SIGNALS_STORED:
                self.signals = self.signals[-Config.MAX_SIGNALS_STORED:]
            
            # Clean up old market data
            cutoff_time = datetime.now() - timedelta(hours=Config.MARKET_DATA_RETENTION_HOURS)
            for symbol in self.market_data:
                for timeframe in self.market_data[symbol]:
                    df = self.market_data[symbol][timeframe]
                    df = df[df['timestamp'] > cutoff_time]
                    self.market_data[symbol][timeframe] = df
            
            # Clean up performance data
            if Config.ENABLE_PERFORMANCE_TRACKING:
                self.performance_tracker.cleanup_old_data(Config.PERFORMANCE_HISTORY_DAYS)
            
            # Record bot statistics
            if Config.ENABLE_PERFORMANCE_TRACKING:
                stats = {
                    'symbols_monitored': len(self.SYMBOLS),
                    'signals_generated': len(self.signals),
                    'active_signals': len([s for s in self.signals if s.get('status') == 'ACTIVE']),
                    'market_data_points': sum(len(data) for data in self.market_data.values()),
                    'uptime_minutes': int((datetime.now() - self.start_time).total_seconds() / 60)
                }
                self.performance_tracker.record_bot_statistics(stats)
            
            logger.info("Cleaned up old data")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            # Start Flask app in a separate thread
            def run_flask():
                self.app.run(host=Config.HOST, port=Config.PORT)
            
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            
            logger.info(f"🚀 {Config.BOT_NAME} v{Config.BOT_VERSION} started successfully!")
            logger.info(f"📊 Monitoring {len(self.SYMBOLS)} symbols across {len(self.TIMEFRAMES)} timeframes")
            logger.info(f"🌐 Admin panel: http://localhost:{Config.PORT}/admin")
            logger.info(f"📡 API status: http://localhost:{Config.PORT}/api/status")
            logger.info(f"📈 Performance: http://localhost:{Config.PORT}/performance")
            logger.info(f"📋 Signals: http://localhost:{Config.PORT}/signals")
            
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
