import os
import time
import json
import logging
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Local imports
from config import Config
from trading_signals import TradingSignals
from arbitrage_detector import ArbitrageDetector
from chart_generator import ChartGenerator
from performance_tracker import PerformanceTracker
from admin_dashboard import AdminDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoSniperXProBot:
    """Advanced Crypto Sniper Bot with Institutional Features"""
    def __init__(self):
        self.start_time = datetime.now()
        self.is_running = False
        
        # Initialize components
        self.trading_signals = TradingSignals()
        self.arbitrage_detector = ArbitrageDetector()
        self.chart_generator = ChartGenerator()
        self.performance_tracker = PerformanceTracker()
        
        # Data storage
        self.signals = []
        self.market_data = {}
        self.active_signals = {}
        self.signal_cooldowns = {}
        
        # Initialize Telegram bot
        self.telegram_bot = None
        self.telegram_chat_id = None
        self._init_telegram()
        
        # Initialize scheduler
        self.scheduler = BackgroundScheduler()
        self._setup_scheduler()
        
        # Initialize admin dashboard
        self.admin_dashboard = AdminDashboard(self)
        self.app = Flask(__name__)
        self._setup_flask_routes()
        
        # Dynamic scanning
        self.scanning_enabled = True
        self.last_scan_time = datetime.now()
        
        logger.info(f"🎯 {Config.BOT_NAME} v{Config.BOT_VERSION} initialized")
    
    def _init_telegram(self):
        """Initialize Telegram bot"""
        try:
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if token and chat_id:
                self.telegram_bot = telegram.Bot(token=token)
                self.telegram_chat_id = chat_id
                logger.info("📱 Telegram bot initialized successfully")
                self._send_telegram_message("🚀 CryptoSniperXProBot started successfully!")
            else:
                logger.warning("⚠️ Telegram credentials not found")
        except Exception as e:
            logger.error(f"❌ Telegram initialization failed: {e}")
    
    def _setup_scheduler(self):
        """Setup APScheduler with dynamic intervals"""
        try:
            # Market data updates
            self.scheduler.add_job(
                self._update_market_data,
                CronTrigger(minute='*/1'),  # Every minute
                id='market_data_update'
            )
            
            # Signal scanning
            self.scheduler.add_job(
                self._scan_for_signals,
                CronTrigger(minute='*/2'), # Every 2 minutes
                id='signal_scanning'
            )
            
            # Arbitrage detection
            self.scheduler.add_job(
                self._detect_arbitrage,
                CronTrigger(minute='*/3'), # Every 3 minutes
                id='arbitrage_detection'
            )
            
            # Performance tracking
            self.scheduler.add_job(
                self._update_performance,
                CronTrigger(minute='*/5'), # Every 5 minutes
                id='performance_update'
            )
            
            # Admin dashboard updates
            self.scheduler.add_job(
                self._update_admin_dashboard,
                CronTrigger(minute='*/1'),  # Every minute
                id='admin_dashboard_update'
            )
            
            logger.info("⏰ Scheduler configured successfully")
        except Exception as e:
            logger.error(f"❌ Scheduler setup failed: {e}")
    
    def _setup_flask_routes(self):
        """Setup Flask REST API routes"""
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self._get_bot_status())
        
        @self.app.route('/api/add-symbol', methods=['POST'])
        def add_symbol():
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            if symbol and symbol not in Config.DYNAMIC_SYMBOLS:
                Config.DYNAMIC_SYMBOLS.append(symbol)
                self._save_config()
                logger.info(f"✅ Added symbol: {symbol}")
                return jsonify({'status': 'ok', 'message': f'Symbol {symbol} added'})
            return jsonify({'status': 'error', 'message': 'Invalid symbol'})
        
        @self.app.route('/api/remove-symbol', methods=['POST'])
        def remove_symbol():
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            if symbol in Config.DYNAMIC_SYMBOLS:
                Config.DYNAMIC_SYMBOLS.remove(symbol)
                self._save_config()
                logger.info(f"❌ Removed symbol: {symbol}")
                return jsonify({'status': 'ok', 'message': f'Symbol {symbol} removed'})
            return jsonify({'status': 'error', 'message': 'Symbol not found'})
        
        @self.app.route('/api/add-timeframe', methods=['POST'])
        def add_timeframe():
            data = request.get_json()
            timeframe = data.get('timeframe', '').lower()
            if timeframe and timeframe not in Config.DYNAMIC_TIMEFRAMES:
                Config.DYNAMIC_TIMEFRAMES.append(timeframe)
                self._save_config()
                logger.info(f"✅ Added timeframe: {timeframe}")
                return jsonify({'status': 'ok', 'message': f'Timeframe {timeframe} added'})
            return jsonify({'status': 'error', 'message': 'Invalid timeframe'})
        
        @self.app.route('/api/remove-timeframe', methods=['POST'])
        def remove_timeframe():
            data = request.get_json()
            timeframe = data.get('timeframe', '').lower()
            if timeframe in Config.DYNAMIC_TIMEFRAMES:
                Config.DYNAMIC_TIMEFRAMES.remove(timeframe)
                self._save_config()
                logger.info(f"❌ Removed timeframe: {timeframe}")
                return jsonify({'status': 'ok', 'message': f'Timeframe {timeframe} removed'})
            return jsonify({'status': 'error', 'message': 'Timeframe not found'})
        
        @self.app.route('/api/set-session', methods=['POST'])
        def set_session():
            data = request.get_json()
            session = data.get('session', 'auto')
            if session in ['auto', 'manual', 'asian', 'london', 'newyork']:
                Config.ACTIVE_SESSION = session
                self._save_config()
                logger.info(f"🌍 Session changed to: {session}")
                return jsonify({'status': 'ok', 'message': f'Session set to {session}'})
            return jsonify({'status': 'error', 'message': 'Invalid session'})
        
        @self.app.route('/api/set-color-theme', methods=['POST'])
        def set_color_theme():
            data = request.get_json()
            theme = data.get('theme', 'dynamic')
            if theme in ['dynamic', 'light', 'dark', 'custom']:
                Config.ACTIVE_COLOR_THEME = theme
                self._save_config()
                logger.info(f"🎨 Theme changed to: {theme}")
                return jsonify({'status': 'ok', 'message': f'Theme set to {theme}'})
            return jsonify({'status': 'error', 'message': 'Invalid theme'})
        
        @self.app.route('/api/set-custom-colors', methods=['POST'])
        def set_custom_colors():
            data = request.get_json()
            colors = data.get('colors', {})
            if colors:
                Config.CUSTOM_COLORS = colors
                self._save_config()
                logger.info("🎨 Custom colors updated")
                return jsonify({'status': 'ok', 'message': 'Custom colors updated'})
            return jsonify({'status': 'error', 'message': 'Invalid colors'})
        
        @self.app.route('/api/send-test-signal', methods=['POST'])
        def send_test_signal():
            try:
                self._send_test_signal()
                return jsonify({'status': 'ok', 'message': 'Test signal sent'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/toggle-scanning', methods=['POST'])
        def toggle_scanning():
            self.scanning_enabled = not self.scanning_enabled
            status = "enabled" if self.scanning_enabled else "disabled"
            logger.info(f"🔍 Signal scanning {status}")
            return jsonify({'status': 'ok', 'scanning': self.scanning_enabled})
        
        @self.app.route('/admin')
        def admin_dashboard_page():
            return self.admin_dashboard._render_dashboard()
        
        @self.app.route('/admin/login', methods=['GET', 'POST'])
        def admin_login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if username == 'admin' and password == 'admin123':
                    return redirect('/admin')
                else:
                    return "Invalid credentials", 401
            return self.admin_dashboard._render_login_page()
    
    def _save_config(self):
        """Save configuration changes"""
        try:
            config_data = {
                'DYNAMIC_SYMBOLS': Config.DYNAMIC_SYMBOLS,
                'DYNAMIC_TIMEFRAMES': Config.DYNAMIC_TIMEFRAMES,
                'ACTIVE_SESSION': Config.ACTIVE_SESSION,
                'ACTIVE_COLOR_THEME': Config.ACTIVE_COLOR_THEME,
                'CUSTOM_COLORS': Config.CUSTOM_COLORS
            }
            
            with open('config_backup.json', 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("💾 Configuration saved")
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
    
    def _update_market_data(self):
        """Update market data for all symbols"""
        try:
            for symbol in Config.DYNAMIC_SYMBOLS:
                for timeframe in Config.DYNAMIC_TIMEFRAMES:
                    data = self._fetch_market_data(symbol, timeframe)
                    if data:
                        self.market_data[f"{symbol}_{timeframe}"] = data
            
            logger.debug(f"📊 Updated market data for {len(Config.DYNAMIC_SYMBOLS)} symbols")
        except Exception as e:
            logger.error(f"❌ Market data update failed: {e}")
    
    def _fetch_market_data(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Fetch market data from exchange"""
        try:
            # Simulate market data fetch
            import random
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'price': random.uniform(0.1, 1000),
                'volume': random.uniform(1000, 1000000),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {symbol}: {e}")
            return None
    
    def _scan_for_signals(self):
        """Scan for trading signals"""
        if not self.scanning_enabled:
            return
        
        try:
            for symbol in Config.DYNAMIC_SYMBOLS:
                # Check cooldown
                if self._is_in_cooldown(symbol):
                    continue
                
                for timeframe in Config.DYNAMIC_TIMEFRAMES:
                    signal = self.trading_signals.generate_signal(symbol, timeframe)
                    if signal and self._validate_signal(signal):
                        self._process_signal(signal)
                        self._set_cooldown(symbol)
                        break
            
            self.last_scan_time = datetime.now()
        except Exception as e:
            logger.error(f"❌ Signal scanning failed: {e}")
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown"""
        if symbol not in self.signal_cooldowns:
            return False
        
        cooldown_time = self.signal_cooldowns[symbol]
        return datetime.now() < cooldown_time
    
    def _set_cooldown(self, symbol: str):
        """Set cooldown for symbol"""
        cooldown_duration = timedelta(minutes=Config.SIGNAL_COOLDOWN_MINUTES)
        self.signal_cooldowns[symbol] = datetime.now() + cooldown_duration
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Validate trading signal"""
        try:
            # Check if signal is profitable
            if signal.get('profit_potential', 0) < Config.MIN_PROFIT_POTENTIAL:
                return False
            
            # Check risk score
            if signal.get('risk_score', 0) > Config.MAX_RISK_SCORE:
                return False
            
            # Check if signal is recent
            signal_time = datetime.fromisoformat(signal.get('timestamp', ''))
            if datetime.now() - signal_time > timedelta(minutes=5):
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Signal validation failed: {e}")
            return False
    
    def _process_signal(self, signal: Dict):
        """Process and send trading signal"""
        try:
            # Add to signals list
            self.signals.append(signal)
            self.active_signals[signal['symbol']] = signal
            
            # Generate chart
            chart_path = self.chart_generator.generate_chart(signal)
            
            # Send Telegram notification
            self._send_signal_notification(signal, chart_path)
            
            # Update performance tracker
            self.performance_tracker.record_signal(signal)
            
            logger.info(f"📊 Signal processed: {signal['symbol']} {signal['signal_type']}")
        except Exception as e:
            logger.error(f"❌ Signal processing failed: {e}")
    
    def _detect_arbitrage(self):
        """Detect arbitrage opportunities"""
        try:
            opportunities = self.arbitrage_detector.scan_opportunities()
            for opp in opportunities:
                if opp.get('profit_percentage', 0) >= Config.MIN_ARBITRAGE_PROFIT:
                    self._send_arbitrage_notification(opp)
        except Exception as e:
            logger.error(f"❌ Arbitrage detection failed: {e}")
    
    def _update_performance(self):
        """Update performance statistics"""
        try:
            self.performance_tracker.update_stats()
            logger.debug("📈 Performance updated")
        except Exception as e:
            logger.error(f"❌ Performance update failed: {e}")
    
    def _update_admin_dashboard(self):
        """Update admin dashboard data"""
        try:
            # Update dashboard data
            self.admin_dashboard._update_dashboard_data()
        except Exception as e:
            logger.error(f"❌ Admin dashboard update failed: {e}")
    
    def _send_signal_notification(self, signal: Dict, chart_path: Optional[str] = None):
        """Send signal notification to Telegram"""
        try:
            if not self.telegram_bot or not self.telegram_chat_id:
                return
            
            # Create message
            emoji = "🟢" if signal['signal_type'] == 'LONG' else "🔴"
            message = f"""{emoji} **{signal['signal_type']} SIGNAL** {emoji}

📊 **Symbol:** {signal['symbol']}
⏰ **Timeframe:** {signal['timeframe']}
💰 **Entry Price:** ${signal['entry_price']:.6f}
🎯 **Take Profit:** ${signal['take_profit']:.6f}
🛑 **Stop Loss:** ${signal['stop_loss']:.6f}
📈 **Profit Potential:** {signal['profit_potential']:.2f}%
⚠️ **Risk Score:** {signal['risk_score']}/10
🔍 **Analysis:**
{signal.get('analysis', 'No analysis available')}

⏰ **Time:** {signal['timestamp']}
      ip()
            
            # Send message
            self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # Send chart if available
            if chart_path and os.path.exists(chart_path):
                with open(chart_path, 'rb') as chart:
                    self.telegram_bot.send_photo(
                        chat_id=self.telegram_chat_id,
                        photo=chart,
                        caption=f"📈 Chart for {signal['symbol']}"
                    )
            
            logger.info(f"📱 Signal notification sent for {signal['symbol']}")
        except Exception as e:
            logger.error(f"❌ Signal notification failed: {e}")
    
    def _send_arbitrage_notification(self, opportunity: Dict):
        """Send arbitrage notification to Telegram"""
        try:
            if not self.telegram_bot or not self.telegram_chat_id:
                return
            
            message = f"""💰**ARBITRAGE OPPORTUNITY** 💰

🔄 **Symbol:** {opportunity['symbol']}
📈 **Profit:** {opportunity.get('profit_percentage', 0):.2f}%
💵 **Profit Amount:** ${opportunity.get('profit_amount', 0):.2f}

🏪 **Exchanges:**
• Buy: {opportunity.get('buy_exchange', 'N/A')} @ ${opportunity.get('buy_price', 0):.6f}
• Sell: {opportunity.get('sell_exchange', 'N/A')} @ ${opportunity.get('sell_price', 0):.6f}

⏱️ **Execution Time:** {opportunity.get('execution_time', 0):.2f}s
⚠️ **Risk Level:** {opportunity.get('risk_level', 0)}/10

⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
      ip()
            
            self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"💰 Arbitrage notification sent for {opportunity['symbol']}")
        except Exception as e:
            logger.error(f"❌ Arbitrage notification failed: {e}")
    
    def _send_telegram_message(self, message: str):
        """Send simple message to Telegram"""
        try:
            if self.telegram_bot and self.telegram_chat_id:
                self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message
                )
        except Exception as e:
            logger.error(f"❌ Telegram message failed: {e}")
    
    def _send_test_signal(self):
        """Send test signal"""
        test_signal = {
            'symbol': 'BTC/USDT',
            'signal_type': 'LONG',
            'timeframe': 1,
            'entry_price': 45000,
            'take_profit': 46500,
            'stop_loss': 44000,
            'profit_potential': 30.33,
            'risk_score': 3,
            'analysis': 'Test signal for system verification',
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_signal_notification(test_signal)
    
    def _get_bot_status(self) -> Dict[str, Any]:
        """Get comprehensive bot status"""
        try:
            return {
                'bot_name': Config.BOT_NAME,
                'bot_version': Config.BOT_VERSION,
                'status': 'running' if self.is_running else 'stopped',
                'uptime': str(datetime.now() - self.start_time),
                'symbols_monitored': len(Config.DYNAMIC_SYMBOLS),
                'timeframes_monitored': len(Config.DYNAMIC_TIMEFRAMES),
                'signals_generated': len(self.signals),
                'active_signals': len(self.active_signals),
                'scanning_enabled': self.scanning_enabled,
                'last_scan_time': self.last_scan_time.isoformat(),
                'telegram_connected': bool(self.telegram_bot),
                'performance_stats': self.performance_tracker.get_performance_stats(30)
            }
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {'error': str(e)}
    
    def start(self):
        """Start the bot"""
        try:
            self.is_running = True      
            # Start scheduler
            self.scheduler.start()
            logger.info("⏰ Scheduler started")
            
            # Start Flask app
            threading.Thread(
                target=lambda: self.app.run(
                    host='0.0.0.0',
                    port=5000,
                    debug=False
                ),
                daemon=True
            ).start()
            logger.info("🌐 Flask server started on port 5000")
            # Send startup notification
            self._send_telegram_message("🚀 CryptoSniperXProBot is now running!")
            
            logger.info(f"🎯 {Config.BOT_NAME} started successfully")
            
            # Keep main thread alive
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        try:
            self.is_running = False
            
            # Stop scheduler
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("⏰ Scheduler stopped")
            
            # Send shutdown notification
            self._send_telegram_message("🛑 CryptoSniperXProBot is shutting down")
            
            logger.info(f"🛑 {Config.BOT_NAME} stopped")
        except Exception as e:
            logger.error(f"❌ Bot shutdown failed: {e}")


if __name__ == "__main__":
    bot = CryptoSniperXProBot()
    bot.start()