"""
Advanced Institutional-Grade Z+++ Indicators for CryptoSniperXProBot
Features: Momentum Analysis, Sentiment Analysis, Arbitrage Detection, Multi-Exchange Integration
"""

import numpy as np
import pandas as pd
import requests
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import ccxt
import ta
from ta.trend import EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice
import logging

logger = logging.getLogger(__name__)

class InstitutionalZPlusPlus:
    """Institutional-grade Z+++ analysis with momentum and sentiment"""
    
    def __init__(self):
        self.exchanges = {}
        self.market_data = {}
        self.sentiment_data = {}
        self.arbitrage_opportunities = []
        self.momentum_signals = []
        self.consolidation_filter = True
        
        # Initialize exchanges
        self._init_exchanges()
        
        # Start data collection threads
        self._start_data_collection()
    
    def _init_exchanges(self):
        """Initialize multiple exchanges for arbitrage"""
        exchange_configs = {
            'binance': {'sandbox': False},
            'bybit': {'sandbox': False},
            'bitget': {'sandbox': False},
            'gate': {'sandbox': False},
            'kucoin': {'sandbox': False},
            'okx': {'sandbox': False},
            'mexc': {'sandbox': False}
        }
        
        for name, config in exchange_configs.items():
            try:
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class(config)
                logger.info(f"✅ {name.upper()} exchange initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {name}: {e}")
    
    def _start_data_collection(self):
        """Start real-time data collection threads"""
        threading.Thread(target=self._collect_market_data, daemon=True).start()
        threading.Thread(target=self._collect_sentiment_data, daemon=True).start()
        threading.Thread(target=self._detect_arbitrage, daemon=True).start()
    
    def _collect_market_data(self):
        """Collect real-time market data from all exchanges"""
        while True:
            try:
                for exchange_name, exchange in self.exchanges.items():
                    if exchange_name not in self.market_data:
                        self.market_data[exchange_name] = {}
                    
                    # Get top trading pairs
                    symbols = self._get_top_symbols()
                    
                    for symbol in symbols:
                        try:
                            # Get OHLCV data
                            ohlcv = exchange.fetch_ohlcv(symbol, '1m', limit=100)
                            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                            
                            # Calculate advanced indicators
                            df = self._calculate_z_plus_plus_indicators(df)
                            
                            self.market_data[exchange_name][symbol] = df
                            
                        except Exception as e:
                            logger.error(f"Error collecting data for {symbol} on {exchange_name}: {e}")
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Market data collection error: {e}")
                time.sleep(60)
    
    def _collect_sentiment_data(self):
        """Collect market sentiment data from multiple sources"""
        while True:
            try:
                # CoinGecko sentiment
                self._get_coingecko_sentiment()
                
                # CoinMarketCap sentiment
                self._get_cmc_sentiment()
                
                # CoinGlass sentiment
                self._get_coinglass_sentiment()
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Sentiment data collection error: {e}")
                time.sleep(120)
    
    def _get_coingecko_sentiment(self):
        """Get sentiment data from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for coin in data:
                    symbol = coin['symbol'].upper() + '/USDT'
                    self.sentiment_data[symbol] = {
                        'source': 'coingecko',
                        'market_cap_rank': coin.get('market_cap_rank'),
                        'price_change_24h': coin.get('price_change_percentage_24h'),
                        'volume_24h': coin.get('total_volume'),
                        'market_cap': coin.get('market_cap'),
                        'timestamp': datetime.now()
                    }
                    
        except Exception as e:
            logger.error(f"CoinGecko sentiment error: {e}")
    
    def _get_cmc_sentiment(self):
        """Get sentiment data from CoinMarketCap"""
        try:
            # Using free API endpoint
            url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
            params = {
                'start': 1,
                'limit': 50,
                'sortBy': 'market_cap',
                'sortType': 'desc',
                'convert': 'USD'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for coin in data.get('data', {}).get('cryptoCurrencyList', []):
                    symbol = coin['symbol'] + '/USDT'
                    self.sentiment_data[symbol] = {
                        'source': 'cmc',
                        'market_cap_rank': coin.get('cmcRank'),
                        'price_change_24h': coin.get('quote', {}).get('USD', {}).get('percentChange24h'),
                        'volume_24h': coin.get('quote', {}).get('USD', {}).get('volume24h'),
                        'market_cap': coin.get('quote', {}).get('USD', {}).get('marketCap'),
                        'timestamp': datetime.now()
                    }
                    
        except Exception as e:
            logger.error(f"CMC sentiment error: {e}")
    
    def _get_coinglass_sentiment(self):
        """Get sentiment data from CoinGlass"""
        try:
            url = "https://open-api.coinglass.com/public/v2/index"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('data', []):
                    symbol = item['symbol'] + '/USDT'
                    if symbol in self.sentiment_data:
                        self.sentiment_data[symbol].update({
                            'coinglass_fear_greed': item.get('fearGreedIndex'),
                            'coinglass_sentiment': item.get('sentiment'),
                            'timestamp': datetime.now()
                        })
                        
        except Exception as e:
            logger.error(f"CoinGlass sentiment error: {e}")
    
    def _get_top_symbols(self) -> List[str]:
        """Get top trading symbols"""
        return [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT",
            "XRP/USDT", "DOT/USDT", "LINK/USDT", "MATIC/USDT", "AVAX/USDT",
            "UNI/USDT", "ATOM/USDT", "LTC/USDT", "DOGE/USDT", "SHIB/USDT",
            "TRX/USDT", "NEAR/USDT", "FTM/USDT", "ALGO/USDT", "VET/USDT"
        ]
    
    def _calculate_z_plus_plus_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate institutional-grade Z+++ indicators"""
        try:
            # Basic indicators
            df['rsi'] = RSIIndicator(df['close']).rsi()
            df['macd'] = ta.trend.MACD(df['close']).macd()
            df['macd_signal'] = ta.trend.MACD(df['close']).macd_signal()
            df['bb_upper'] = BollingerBands(df['close']).bollinger_hband()
            df['bb_lower'] = BollingerBands(df['close']).bollinger_lband()
            df['bb_middle'] = BollingerBands(df['close']).bollinger_mavg()
            
            # Advanced momentum indicators
            df['ema_9'] = EMAIndicator(df['close'], window=9).ema_indicator()
            df['ema_21'] = EMAIndicator(df['close'], window=21).ema_indicator()
            df['ema_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
            df['sma_20'] = SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = SMAIndicator(df['close'], window=50).sma_indicator()
            
            # Volume indicators
            df['vwap'] = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume']).volume_weighted_average_price()
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Momentum indicators
            df['momentum'] = df['close'] - df['close'].shift(10)
            df['momentum_ma'] = df['momentum'].rolling(window=10).mean()
            df['momentum_strength'] = (df['momentum'] - df['momentum_ma']) / df['momentum_ma']
            
            # Volatility indicators
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            df['volatility'] = df['close'].rolling(window=20).std()
            
            # Trend strength indicators
            df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
            df['dmi_plus'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx_pos()
            df['dmi_minus'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx_neg()
            
            # Z+++ specific indicators
            df['z_momentum_score'] = self._calculate_z_momentum_score(df)
            df['z_trend_strength'] = self._calculate_z_trend_strength(df)
            df['z_volatility_score'] = self._calculate_z_volatility_score(df)
            df['z_volume_score'] = self._calculate_z_volume_score(df)
            df['z_overall_score'] = self._calculate_z_overall_score(df)
            
            # Consolidation filter
            df['is_consolidation'] = self._detect_consolidation(df)
            df['is_choppy'] = self._detect_choppy_market(df)
            df['is_sideways'] = self._detect_sideways_market(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Z+++ indicators: {e}")
            return df
    
    def _calculate_z_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Z+++ momentum score"""
        try:
            # Price momentum
            price_momentum = (df['close'] - df['close'].shift(5)) / df['close'].shift(5)
            
            # Volume momentum
            volume_momentum = (df['volume'] - df['volume'].shift(5)) / df['volume'].shift(5)
            
            # RSI momentum
            rsi_momentum = df['rsi'] - df['rsi'].shift(3)
            
            # MACD momentum
            macd_momentum = df['macd'] - df['macd'].shift(3)
            
            # Combined momentum score
            momentum_score = (
                price_momentum * 0.4 +
                volume_momentum * 0.2 +
                rsi_momentum * 0.2 +
                macd_momentum * 0.2
            )
            
            return momentum_score.rolling(window=5).mean()
            
        except Exception as e:
            logger.error(f"Error calculating momentum score: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_z_trend_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Z+++ trend strength"""
        try:
            # ADX strength
            adx_strength = df['adx'] / 100
            
            # EMA alignment
            ema_alignment = (
                (df['ema_9'] > df['ema_21']).astype(int) +
                (df['ema_21'] > df['ema_50']).astype(int)
            ) / 2
            
            # Price vs EMAs
            price_vs_ema = (df['close'] > df['ema_21']).astype(int)
            
            # Combined trend strength
            trend_strength = (
                adx_strength * 0.4 +
                ema_alignment * 0.3 +
                price_vs_ema * 0.3
            )
            
            return trend_strength.rolling(window=10).mean()
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_z_volatility_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Z+++ volatility score"""
        try:
            # ATR volatility
            atr_volatility = df['atr'] / df['close']
            
            # Bollinger Band width
            bb_width = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Price volatility
            price_volatility = df['close'].rolling(window=20).std() / df['close']
            
            # Combined volatility score
            volatility_score = (
                atr_volatility * 0.4 +
                bb_width * 0.3 +
                price_volatility * 0.3
            )
            
            return volatility_score.rolling(window=10).mean()
            
        except Exception as e:
            logger.error(f"Error calculating volatility score: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_z_volume_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Z+++ volume score"""
        try:
            # Volume ratio
            volume_ratio = df['volume_ratio']
            
            # Volume trend
            volume_trend = df['volume'].rolling(window=10).mean() / df['volume'].rolling(window=50).mean()
            
            # Volume momentum
            volume_momentum = df['volume'] / df['volume'].rolling(window=5).mean()
            
            # Combined volume score
            volume_score = (
                volume_ratio * 0.4 +
                volume_trend * 0.3 +
                volume_momentum * 0.3
            )
            
            return volume_score.rolling(window=5).mean()
            
        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return pd.Series(0, index=df.index)
    
    def _calculate_z_overall_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Z+++ overall score"""
        try:
            overall_score = (
                df['z_momentum_score'] * 0.3 +
                df['z_trend_strength'] * 0.3 +
                df['z_volatility_score'] * 0.2 +
                df['z_volume_score'] * 0.2
            )
            
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return pd.Series(0, index=df.index)
    
    def _detect_consolidation(self, df: pd.DataFrame) -> pd.Series:
        """Detect consolidation zones"""
        try:
            # Price range
            price_range = (df['high'].rolling(window=20).max() - df['low'].rolling(window=20).min()) / df['close']
            
            # Volume decline
            volume_decline = df['volume'] < df['volume'].rolling(window=20).mean() * 0.8
            
            # Low volatility
            low_volatility = df['atr'] < df['atr'].rolling(window=20).mean() * 0.7
            
            # Consolidation condition
            consolidation = (price_range < 0.05) & volume_decline & low_volatility
            
            return consolidation
            
        except Exception as e:
            logger.error(f"Error detecting consolidation: {e}")
            return pd.Series(False, index=df.index)
    
    def _detect_choppy_market(self, df: pd.DataFrame) -> pd.Series:
        """Detect choppy market conditions"""
        try:
            # Frequent direction changes
            price_changes = df['close'].diff().abs()
            frequent_changes = price_changes > price_changes.rolling(window=20).mean() * 1.5
            
            # Low trend strength
            low_trend = df['adx'] < 25
            
            # High volatility
            high_volatility = df['atr'] > df['atr'].rolling(window=20).mean() * 1.3
            
            # Choppy condition
            choppy = frequent_changes & low_trend & high_volatility
            
            return choppy
            
        except Exception as e:
            logger.error(f"Error detecting choppy market: {e}")
            return pd.Series(False, index=df.index)
    
    def _detect_sideways_market(self, df: pd.DataFrame) -> pd.Series:
        """Detect sideways market conditions"""
        try:
            # Flat moving averages
            ema_flat = abs(df['ema_21'] - df['ema_50']) / df['close'] < 0.02
            
            # Low momentum
            low_momentum = abs(df['z_momentum_score']) < 0.1
            
            # Low volume
            low_volume = df['volume'] < df['volume'].rolling(window=20).mean() * 0.9
            
            # Sideways condition
            sideways = ema_flat & low_momentum & low_volume
            
            return sideways
            
        except Exception as e:
            logger.error(f"Error detecting sideways market: {e}")
            return pd.Series(False, index=df.index)
    
    def _detect_arbitrage(self):
        """Detect arbitrage opportunities across exchanges"""
        while True:
            try:
                opportunities = []
                
                for symbol in self._get_top_symbols():
                    prices = {}
                    
                    # Get prices from all exchanges
                    for exchange_name, exchange in self.exchanges.items():
                        try:
                            ticker = exchange.fetch_ticker(symbol)
                            prices[exchange_name] = {
                                'bid': ticker['bid'],
                                'ask': ticker['ask'],
                                'last': ticker['last']
                            }
                        except Exception as e:
                            logger.error(f"Error getting {symbol} price from {exchange_name}: {e}")
                    
                    # Calculate arbitrage opportunities
                    if len(prices) >= 2:
                        arbitrage_opps = self._calculate_arbitrage_opportunities(symbol, prices)
                        opportunities.extend(arbitrage_opps)
                
                self.arbitrage_opportunities = opportunities
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Arbitrage detection error: {e}")
                time.sleep(120)
    
    def _calculate_arbitrage_opportunities(self, symbol: str, prices: Dict) -> List[Dict]:
        """Calculate arbitrage opportunities"""
        opportunities = []
        
        try:
            exchanges = list(prices.keys())
            
            for i in range(len(exchanges)):
                for j in range(i + 1, len(exchanges)):
                    ex1, ex2 = exchanges[i], exchanges[j]
                    
                    # Calculate potential profit
                    buy_price = prices[ex1]['ask']
                    sell_price = prices[ex2]['bid']
                    
                    if sell_price > buy_price:
                        profit_pct = ((sell_price - buy_price) / buy_price) * 100
                        
                        # Only consider profitable opportunities
                        if profit_pct > 0.5:  # 0.5% minimum profit
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': ex1,
                                'sell_exchange': ex2,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'profit_pct': profit_pct,
                                'timestamp': datetime.now()
                            }
                            opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage for {symbol}: {e}")
            return []
    
    def get_momentum_signals(self) -> List[Dict]:
        """Get momentum trading signals"""
        signals = []
        
        try:
            for exchange_name, exchange_data in self.market_data.items():
                for symbol, df in exchange_data.items():
                    if len(df) < 50:
                        continue
                    
                    current = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # Skip consolidation/choppy/sideways markets
                    if (current['is_consolidation'] or 
                        current['is_choppy'] or 
                        current['is_sideways']):
                        continue
                    
                    # Momentum signal conditions
                    momentum_signal = self._generate_momentum_signal(symbol, df, exchange_name)
                    if momentum_signal:
                        signals.append(momentum_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting momentum signals: {e}")
            return []
    
    def _generate_momentum_signal(self, symbol: str, df: pd.DataFrame, exchange: str) -> Optional[Dict]:
        """Generate momentum trading signal"""
        try:
            current = df.iloc[-1]
            
            # Strong momentum conditions
            strong_momentum = (
                current['z_momentum_score'] > 0.3 and
                current['z_trend_strength'] > 0.6 and
                current['z_volume_score'] > 1.2 and
                current['adx'] > 25
            )
            
            # Price action confirmation
            price_above_ema = current['close'] > current['ema_21']
            volume_spike = current['volume_ratio'] > 1.5
            
            # RSI conditions
            rsi_bullish = 30 < current['rsi'] < 70
            rsi_momentum = current['rsi'] > df['rsi'].iloc[-2]
            
            # MACD conditions
            macd_bullish = current['macd'] > current['macd_signal']
            macd_momentum = current['macd'] > df['macd'].iloc[-2]
            
            # Generate signal
            if (strong_momentum and price_above_ema and volume_spike and 
                rsi_bullish and rsi_momentum and macd_bullish and macd_momentum):
                
                return {
                    'symbol': symbol,
                    'exchange': exchange,
                    'type': 'MOMENTUM_LONG',
                    'price': current['close'],
                    'confidence': min(95, current['z_overall_score'] * 100),
                    'strength': 'STRONG',
                    'timestamp': current['timestamp'],
                    'indicators': {
                        'momentum_score': current['z_momentum_score'],
                        'trend_strength': current['z_trend_strength'],
                        'volume_score': current['z_volume_score'],
                        'overall_score': current['z_overall_score']
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating momentum signal for {symbol}: {e}")
            return None
    
    def get_sentiment_signals(self) -> List[Dict]:
        """Get sentiment-based trading signals"""
        signals = []
        
        try:
            for symbol, sentiment in self.sentiment_data.items():
                if symbol not in self.market_data.get('binance', {}):
                    continue
                
                df = self.market_data['binance'][symbol]
                if len(df) < 50:
                    continue
                
                current = df.iloc[-1]
                
                # Sentiment signal conditions
                sentiment_signal = self._generate_sentiment_signal(symbol, df, sentiment)
                if sentiment_signal:
                    signals.append(sentiment_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting sentiment signals: {e}")
            return []
    
    def _generate_sentiment_signal(self, symbol: str, df: pd.DataFrame, sentiment: Dict) -> Optional[Dict]:
        """Generate sentiment-based trading signal"""
        try:
            current = df.iloc[-1]
            
            # Sentiment conditions
            positive_sentiment = (
                sentiment.get('price_change_24h', 0) > 2 and
                sentiment.get('volume_24h', 0) > 1000000 and
                sentiment.get('market_cap_rank', 999) <= 100
            )
            
            # Technical confirmation
            technical_bullish = (
                current['z_momentum_score'] > 0.2 and
                current['z_trend_strength'] > 0.5 and
                current['close'] > current['ema_21']
            )
            
            # Generate signal
            if positive_sentiment and technical_bullish:
                return {
                    'symbol': symbol,
                    'type': 'SENTIMENT_LONG',
                    'price': current['close'],
                    'confidence': 85,
                    'strength': 'STRONG',
                    'timestamp': current['timestamp'],
                    'sentiment': sentiment
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating sentiment signal for {symbol}: {e}")
            return None
    
    def get_arbitrage_signals(self) -> List[Dict]:
        """Get arbitrage trading signals"""
        return self.arbitrage_opportunities
    
    def get_all_signals(self) -> Dict:
        """Get all types of signals"""
        return {
            'momentum_signals': self.get_momentum_signals(),
            'sentiment_signals': self.get_sentiment_signals(),
            'arbitrage_signals': self.get_arbitrage_signals(),
            'timestamp': datetime.now()
        }