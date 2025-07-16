"""
Configuration file for Crypto Sniper Bot
"""

import os
from typing import List

class Config:
    """Bot configuration settings"""
    
    # === TELEGRAM SETTINGS ===
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # === EXCHANGE SETTINGS ===
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    EXCHANGE_SANDBOX = False  # Set to True for testing
    
    # === TRADING PAIRS ===
    SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", 
        "ADA/USDT", "DOT/USDT", "LINK/USDT", "MATIC/USDT",
        "AVAX/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT",
        "XRP/USDT", "DOGE/USDT", "SHIB/USDT", "TRX/USDT"
    ]
    
    # === TIMEFRAMES ===
    TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h"]
    
    # === RISK MANAGEMENT ===
    MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))  # 2%
    MIN_RISK_REWARD_RATIO = float(os.getenv("MIN_RISK_REWARD_RATIO", "2.0"))
    MAX_SIGNALS_PER_HOUR = 10
    
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
    
    # === SCHEDULER ===
    MARKET_DATA_UPDATE_INTERVAL = 1  # minutes
    ANALYSIS_INTERVAL = 5  # minutes
    CLEANUP_INTERVAL = 60  # minutes
    
    # === NOTIFICATIONS ===
    ENABLE_TELEGRAM = True
    ENABLE_CONSOLE_LOGS = True
    
    # === DATA RETENTION ===
    MAX_SIGNALS_STORED = 100
    MARKET_DATA_RETENTION_HOURS = 24
    
    # === WEBSERVER ===
    PORT = int(os.getenv("PORT", 5000))
    HOST = "0.0.0.0"
    
    # === LOGGING ===
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
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