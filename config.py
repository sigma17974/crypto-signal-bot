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
    MIN_CONFIDENCE = 40  # Minimum confidence percentage
    MAX_SIGNALS_PER_SYMBOL = 3  # Max signals per symbol per hour
    SIGNAL_COOLDOWN_MINUTES = 30  # Minutes between signals for same symbol
    
    # === ADVANCED FEATURES ===
    ENABLE_WHALE_TRACKING = True
    ENABLE_NEWS_SENTIMENT = False
    ENABLE_SOCIAL_SENTIMENT = False
    ENABLE_FUNDAMENTAL_ANALYSIS = False
    
    # === SCHEDULER ===
    MARKET_DATA_UPDATE_INTERVAL = 1  # minutes
    ANALYSIS_INTERVAL = 5  # minutes
    CLEANUP_INTERVAL = 60  # minutes
    SIGNAL_CHECK_INTERVAL = 2  # minutes
    
    # === NOTIFICATIONS ===
    ENABLE_TELEGRAM = True
    ENABLE_CONSOLE_LOGS = True
    ENABLE_EMAIL_ALERTS = False
    ENABLE_DISCORD_WEBHOOK = False
    
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