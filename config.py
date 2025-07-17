"""
Configuration file for Crypto Sniper Bot
"""

import os
from typing import List

class Config:
    """Bot configuration settings"""
    
    # === BOT IDENTITY ===
    BOT_NAME = "CryptoSniperXProBot"
    BOT_VERSION = "2.1.0"
    BOT_DESCRIPTION = "Advanced Crypto Trading Bot with Real-time Sniper Entry Detection"
    
    # === TELEGRAM SETTINGS ===
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_BOT_USERNAME = "crypto_sniper_pro_bot"  # Your bot username
    
    # === EXCHANGE SETTINGS ===
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    EXCHANGE_SANDBOX = False  # Set to True for testing
    
    # === TRADING PAIRS ===
    SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", 
        "ADA/USDT", "DOT/USDT", "LINK/USDT", "MATIC/USDT",
        "AVAX/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT",
        "XRP/USDT", "DOGE/USDT", "SHIB/USDT", "TRX/USDT",
        "NEAR/USDT", "FTM/USDT", "ALGO/USDT", "VET/USDT"
    ]
    
    # === TIMEFRAMES ===
    TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h"]
    
    # === RISK MANAGEMENT ===
    MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))  # 2%
    MIN_RISK_REWARD_RATIO = float(os.getenv("MIN_RISK_REWARD_RATIO", "2.0"))
    MAX_SIGNALS_PER_HOUR = 10
    MAX_DAILY_SIGNALS = 50
    
    # === TECHNICAL INDICATORS ===
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BB_PERIOD = 20
    BB_STD = 2
    
    STOCH_K = 14
    STOCH_D = 3
    
    # === SNIPER DETECTION ===
    VOLUME_SPIKE_THRESHOLD = 2.0  # Volume 2x average
    PRICE_MOMENTUM_THRESHOLD = 0.02  # 2% price change
    BB_SQUEEZE_THRESHOLD = 0.1  # Tight squeeze
    
    # === SIGNAL FILTERS ===
    MIN_CONFIDENCE = 70  # Minimum confidence percentage - Increased for Z+++ quality
    MAX_SIGNALS_PER_SYMBOL = 3  # Max signals per symbol per hour
    SIGNAL_COOLDOWN_MINUTES = 30  # Minutes between signals for same symbol
    
    # === Z+++ ADVANCED SETTINGS ===
    ENABLE_Z_PLUS_PLUS = True  # Enable institutional-grade Z+++ indicators
    ENABLE_MOMENTUM_SIGNALS = True  # Enable momentum trading signals
    ENABLE_SENTIMENT_SIGNALS = True  # Enable sentiment-based signals
    ENABLE_ARBITRAGE_SIGNALS = True  # Enable arbitrage detection
    MIN_ARBITRAGE_PROFIT = 0.5  # Minimum arbitrage profit percentage
    ENABLE_CHARTS = True  # Enable real-time chart generation
    CONSOLIDATION_FILTER = True  # Filter out consolidation zones
    CHOPPY_MARKET_FILTER = True  # Filter out choppy markets
    SIDEWAYS_MARKET_FILTER = True  # Filter out sideways markets
    
    # === ADVANCED FEATURES ===
    ENABLE_WHALE_TRACKING = True
    ENABLE_NEWS_SENTIMENT = False
    ENABLE_SOCIAL_SENTIMENT = False
    ENABLE_FUNDAMENTAL_ANALYSIS = False
    ENABLE_ARBITRAGE_SYSTEM = True
    
    # === ARBITRAGE SYSTEM SETTINGS ===
    ARBITRAGE_MIN_PROFIT_PCT = 0.3  # Minimum 0.3% profit
    ARBITRAGE_MAX_RISK_SCORE = 0.7  # Maximum 70% risk
    ARBITRAGE_MIN_VOLUME = 1000  # Minimum volume
    ARBITRAGE_MIN_EXECUTION_SPEED = 0.2  # Minimum execution speed
    ARBITRAGE_CHECK_INTERVAL = 1  # Check every minute
    ARBITRAGE_MAX_OPPORTUNITIES = 20  # Maximum opportunities to track
    ARBITRAGE_ENABLE_DEPOSIT_WITHDRAWAL_CHECK = True  # Check deposit/withdrawal status
    ARBITRAGE_ENABLE_BAD_TRADE_PROTECTION = True  # Enable bad trade protection
    ARBITRAGE_ENABLE_NEW_LISTING_DETECTION = True  # Enable new listing detection
    
    # === SCHEDULER ===
    MARKET_DATA_UPDATE_INTERVAL = 1  # minutes
    ANALYSIS_INTERVAL = 5  # minutes
    CLEANUP_INTERVAL = 60  # minutes
    SIGNAL_CHECK_INTERVAL = 2  # minutes
    
    # === NOTIFICATIONS ===
    ENABLE_TELEGRAM = True
    ENABLE_CONSOLE_LOGS = True
    ENABLE_EMAIL_ALERTS = True
    ENABLE_DISCORD_WEBHOOK = False
    
    # === EMAIL SETTINGS ===
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    
    # === DATA RETENTION ===
    MAX_SIGNALS_STORED = 100
    MARKET_DATA_RETENTION_HOURS = 24
    PERFORMANCE_HISTORY_DAYS = 30
    
    # === WEBSERVER ===
    PORT = int(os.getenv("PORT", 5000))
    HOST = "0.0.0.0"
    
    # === LOGGING ===
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # === PERFORMANCE TRACKING ===
    ENABLE_PERFORMANCE_TRACKING = True
    TRACK_SIGNAL_ACCURACY = True
    TRACK_PROFIT_LOSS = True
    
    # === ADVANCED SIGNAL TYPES ===
    SIGNAL_TYPES = {
        "LONG": [
            "RSI_OVERSOLD_REVERSAL",
            "MACD_BULLISH_CROSS", 
            "GOLDEN_CROSS",
            "BB_SQUEEZE_BREAKOUT",
            "VOLUME_SPIKE_MOMENTUM",
            "RESISTANCE_BREAK",
            "STOCH_OVERSOLD_REVERSAL",
            "VWAP_BOUNCE",
            "FIBONACCI_RETRACEMENT",
            "SUPPORT_BOUNCE",
            "BREAKOUT_CONFIRMATION",
            "MOMENTUM_ACCELERATION"
        ],
        "SHORT": [
            "RSI_OVERBOUGHT_REVERSAL",
            "MACD_BEARISH_CROSS",
            "DEATH_CROSS", 
            "SUPPORT_BREAK",
            "BB_SQUEEZE_BREAKDOWN",
            "VOLUME_SPIKE_DUMP",
            "FIBONACCI_EXTENSION",
            "RESISTANCE_REJECTION",
            "MOMENTUM_DECELERATION"
        ]
    }
    
    # === MARKET CONDITIONS ===
    MARKET_CONDITIONS = {
        "BULL_MARKET": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        "BEAR_MARKET": ["BTC/USDT", "ETH/USDT"],
        "SIDEWAYS": ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    }
    
    # === MANUAL COIN MANAGEMENT ===
    ENABLE_MANUAL_COIN_MANAGEMENT = True
    MANUAL_COINS_FILE = "manual_coins.json"
    MAX_MANUAL_COINS = 50
    MIN_COIN_VOLUME = 1000000  # Minimum 24h volume for manual coins
    
    # === DYNAMIC TIMEFRAMES ===
    ENABLE_DYNAMIC_TIMEFRAMES = True
    DYNAMIC_TIMEFRAMES_FILE = "dynamic_timeframes.json"
    AVAILABLE_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
    
    # === TRADING SESSIONS ===
    ENABLE_TRADING_SESSIONS = True
    SESSIONS_CONFIG_FILE = "trading_sessions.json"
    
    # Session types
    SESSION_TYPES = {
        "SCALPING": {
            "timeframes": ["1m", "5m"],
            "max_hold_time": 30,  # minutes
            "risk_per_trade": 0.01,  # 1%
            "target_profit": 0.005,  # 0.5%
            "enabled": True
        },
        "DAY_TRADING": {
            "timeframes": ["15m", "1h"],
            "max_hold_time": 480,  # 8 hours
            "risk_per_trade": 0.02,  # 2%
            "target_profit": 0.02,  # 2%
            "enabled": True
        },
        "SWING_TRADING": {
            "timeframes": ["4h", "1d"],
            "max_hold_time": 10080,  # 7 days
            "risk_per_trade": 0.03,  # 3%
            "target_profit": 0.05,  # 5%
            "enabled": True
        }
    }
    
    # === DYNAMIC COIN SCANNING ===
    ENABLE_DYNAMIC_COIN_SCANNING = True
    DYNAMIC_SCAN_INTERVAL = 300  # 5 minutes
    MIN_COIN_PRICE = 0.000001  # Minimum coin price
    MAX_COIN_PRICE = 100000  # Maximum coin price
    MIN_MARKET_CAP = 1000000  # Minimum market cap
    MIN_24H_VOLUME = 500000  # Minimum 24h volume
    MIN_24H_CHANGE = -50  # Minimum 24h price change %
    MAX_24H_CHANGE = 200  # Maximum 24h price change %
    
    # === DUPLICATE SIGNAL PREVENTION ===
    ENABLE_DUPLICATE_PREVENTION = True
    SIGNAL_COOLDOWN_PER_COIN = 3600  # 1 hour between signals for same coin
    MIN_PROFIT_THRESHOLD = 0.5  # Minimum profit % to send duplicate signal
    SIGNAL_HISTORY_SIZE = 1000  # Number of signals to keep in history
    
    # === COLOR CUSTOMIZATION ===
    ENABLE_COLOR_CUSTOMIZATION = True
    COLORS_CONFIG_FILE = "dashboard_colors.json"
    
    # Default colors
    DEFAULT_COLORS = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40",
        "background": "#ffffff",
        "text": "#212529",
        "border": "#dee2e6",
        "chart_up": "#28a745",
        "chart_down": "#dc3545",
        "signal_long": "#28a745",
        "signal_short": "#dc3545",
        "profit": "#28a745",
        "loss": "#dc3545"
    }
    
    # === AUTO SESSION SWITCHING ===
    ENABLE_AUTO_SESSION_SWITCHING = True
    SESSION_SWITCH_INTERVAL = 3600  # 1 hour
    MARKET_CONDITION_CHECK_INTERVAL = 300  # 5 minutes
    
    # Market condition thresholds
    BULL_MARKET_THRESHOLD = 0.05  # 5% average gain
    BEAR_MARKET_THRESHOLD = -0.05  # -5% average loss
    SIDEWAYS_MARKET_THRESHOLD = 0.02  # ±2% range
    
    # === DYNAMIC CONFIGURATION ===
    DYNAMIC_SYMBOLS = SYMBOLS.copy()
    DYNAMIC_TIMEFRAMES = TIMEFRAMES.copy()
    SESSION_MODES = ['auto', 'manual']
    ACTIVE_SESSION = 'auto'  # or 'manual', or session name
    COLOR_THEMES = ['light', 'dark', 'dynamic', 'custom']
    ACTIVE_COLOR_THEME = 'dynamic'
    CUSTOM_COLORS = {
        'background': '#181818',
        'card': '#23272e',
        'text': '#ffffff',
        'accent': '#00ff99'
    }

    @classmethod
    def add_symbol(cls, symbol: str):
        if symbol not in cls.DYNAMIC_SYMBOLS:
            cls.DYNAMIC_SYMBOLS.append(symbol)
    
    @classmethod
    def remove_symbol(cls, symbol: str):
        if symbol in cls.DYNAMIC_SYMBOLS:
            cls.DYNAMIC_SYMBOLS.remove(symbol)
    
    @classmethod
    def add_timeframe(cls, tf: str):
        if tf not in cls.DYNAMIC_TIMEFRAMES:
            cls.DYNAMIC_TIMEFRAMES.append(tf)
    
    @classmethod
    def remove_timeframe(cls, tf: str):
        if tf in cls.DYNAMIC_TIMEFRAMES:
            cls.DYNAMIC_TIMEFRAMES.remove(tf)
    
    @classmethod
    def set_session(cls, session: str):
        if session in cls.SESSION_MODES or session in ['asian', 'london', 'newyork']:
            cls.ACTIVE_SESSION = session
    
    @classmethod
    def set_color_theme(cls, theme: str):
        if theme in cls.COLOR_THEMES:
            cls.ACTIVE_COLOR_THEME = theme
    
    @classmethod
    def set_custom_colors(cls, colors: dict):
        cls.CUSTOM_COLORS.update(colors)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN is required")
        
        if not cls.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID is required")
        
        if cls.MAX_RISK_PER_TRADE <= 0 or cls.MAX_RISK_PER_TRADE > 0.1:
            errors.append("MAX_RISK_PER_TRADE must be between 0 and 0.1 (10%)")
        
        if cls.MIN_RISK_REWARD_RATIO < 1.0:
            errors.append("MIN_RISK_REWARD_RATIO must be >= 1.0")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True