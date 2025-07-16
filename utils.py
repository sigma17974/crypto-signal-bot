"""
Utility functions for Crypto Sniper Bot
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    """Advanced technical analysis utilities"""
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        try:
            # Trend indicators
            df = TechnicalAnalysis._add_moving_averages(df)
            df = TechnicalAnalysis._add_macd(df)
            df = TechnicalAnalysis._add_bollinger_bands(df)
            df = TechnicalAnalysis._add_ichimoku(df)
            
            # Momentum indicators
            df = TechnicalAnalysis._add_rsi(df)
            df = TechnicalAnalysis._add_stochastic(df)
            df = TechnicalAnalysis._add_williams_r(df)
            df = TechnicalAnalysis._add_cci(df)
            
            # Volume indicators
            df = TechnicalAnalysis._add_volume_indicators(df)
            df = TechnicalAnalysis._add_obv(df)
            df = TechnicalAnalysis._add_vwap(df)
            
            # Volatility indicators
            df = TechnicalAnalysis._add_atr(df)
            df = TechnicalAnalysis._add_keltner_channels(df)
            
            # Price action
            df = TechnicalAnalysis._add_price_patterns(df)
            df = TechnicalAnalysis._add_support_resistance(df)
            
            # Advanced indicators
            df = TechnicalAnalysis._add_fibonacci_levels(df)
            df = TechnicalAnalysis._add_momentum_indicators(df)
            df = TechnicalAnalysis._add_divergence_detection(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    @staticmethod
    def _add_fibonacci_levels(df: pd.DataFrame) -> pd.DataFrame:
        """Add Fibonacci retracement levels"""
        try:
            # Calculate swing high and low
            window = 20
            df['swing_high'] = df['high'].rolling(window=window).max()
            df['swing_low'] = df['low'].rolling(window=window).min()
            
            # Fibonacci levels
            df['fib_0'] = df['swing_low']
            df['fib_236'] = df['swing_low'] + 0.236 * (df['swing_high'] - df['swing_low'])
            df['fib_382'] = df['swing_low'] + 0.382 * (df['swing_high'] - df['swing_low'])
            df['fib_500'] = df['swing_low'] + 0.500 * (df['swing_high'] - df['swing_low'])
            df['fib_618'] = df['swing_low'] + 0.618 * (df['swing_high'] - df['swing_low'])
            df['fib_786'] = df['swing_low'] + 0.786 * (df['swing_high'] - df['swing_low'])
            df['fib_100'] = df['swing_high']
            
            # Fibonacci signals
            df['fib_support'] = (df['close'] >= df['fib_382']) & (df['close'] <= df['fib_618'])
            df['fib_resistance'] = (df['close'] >= df['fib_618']) & (df['close'] <= df['fib_786'])
            
        except Exception as e:
            logger.error(f"Error adding Fibonacci levels: {e}")
        
        return df
    
    @staticmethod
    def _add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced momentum indicators"""
        try:
            # Rate of Change
            df['roc'] = ta.momentum.ROCIndicator(df['close']).roc()
            
            # Money Flow Index
            df['mfi'] = ta.volume.MFIIndicator(df['high'], df['low'], df['close'], df['volume']).money_flow_index()
            
            # True Strength Index
            df['tsi'] = ta.momentum.TSIIndicator(df['close']).tsi()
            
            # Ultimate Oscillator
            df['uo'] = ta.momentum.UltimateOscillator(df['high'], df['low'], df['close']).ultimate_oscillator()
            
            # Momentum signals
            df['momentum_bullish'] = (df['roc'] > 0) & (df['mfi'] > 50) & (df['tsi'] > 0)
            df['momentum_bearish'] = (df['roc'] < 0) & (df['mfi'] < 50) & (df['tsi'] < 0)
            
        except Exception as e:
            logger.error(f"Error adding momentum indicators: {e}")
        
        return df
    
    @staticmethod
    def _add_divergence_detection(df: pd.DataFrame) -> pd.DataFrame:
        """Detect RSI and price divergences"""
        try:
            # RSI divergence detection
            df['rsi_higher_high'] = (df['rsi'] > df['rsi'].shift(1)) & (df['rsi'].shift(1) > df['rsi'].shift(2))
            df['rsi_lower_low'] = (df['rsi'] < df['rsi'].shift(1)) & (df['rsi'].shift(1) < df['rsi'].shift(2))
            
            df['price_higher_high'] = (df['close'] > df['close'].shift(1)) & (df['close'].shift(1) > df['close'].shift(2))
            df['price_lower_low'] = (df['close'] < df['close'].shift(1)) & (df['close'].shift(1) < df['close'].shift(2))
            
            # Bullish divergence: Price makes lower low, RSI makes higher low
            df['bullish_divergence'] = df['price_lower_low'] & df['rsi_higher_high']
            
            # Bearish divergence: Price makes higher high, RSI makes lower high
            df['bearish_divergence'] = df['price_higher_high'] & df['rsi_lower_low']
            
        except Exception as e:
            logger.error(f"Error adding divergence detection: {e}")
        
        return df
    
    @staticmethod
    def _add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
        """Add moving averages"""
        try:
            df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
            df['sma_200'] = ta.trend.SMAIndicator(df['close'], window=200).sma_indicator()
            
            df['ema_12'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
            df['ema_26'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
            
            # Golden/Death cross detection
            df['golden_cross'] = (df['sma_20'] > df['sma_50']) & (df['sma_20'].shift(1) <= df['sma_50'].shift(1))
            df['death_cross'] = (df['sma_20'] < df['sma_50']) & (df['sma_20'].shift(1) >= df['sma_50'].shift(1))
            
        except Exception as e:
            logger.error(f"Error adding moving averages: {e}")
        
        return df
    
    @staticmethod
    def _add_macd(df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD indicators"""
        try:
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # MACD crossover detection
            df['macd_bullish_cross'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
            df['macd_bearish_cross'] = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
            
        except Exception as e:
            logger.error(f"Error adding MACD: {e}")
        
        return df
    
    @staticmethod
    def _add_bollinger_bands(df: pd.DataFrame) -> pd.DataFrame:
        """Add Bollinger Bands"""
        try:
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
        except Exception as e:
            logger.error(f"Error adding Bollinger Bands: {e}")
        
        return df
    
    @staticmethod
    def _add_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
        """Add Ichimoku Cloud"""
        try:
            ichimoku = ta.trend.IchimokuIndicator(df['high'], df['low'])
            df['ichimoku_a'] = ichimoku.ichimoku_a()
            df['ichimoku_b'] = ichimoku.ichimoku_b()
            df['ichimoku_base'] = ichimoku.ichimoku_base_line()
            df['ichimoku_conversion'] = ichimoku.ichimoku_conversion_line()
            
        except Exception as e:
            logger.error(f"Error adding Ichimoku: {e}")
        
        return df
    
    @staticmethod
    def _add_rsi(df: pd.DataFrame) -> pd.DataFrame:
        """Add RSI"""
        try:
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
            
            # RSI divergence detection
            df['rsi_oversold'] = df['rsi'] < 30
            df['rsi_overbought'] = df['rsi'] > 70
            
        except Exception as e:
            logger.error(f"Error adding RSI: {e}")
        
        return df
    
    @staticmethod
    def _add_stochastic(df: pd.DataFrame) -> pd.DataFrame:
        """Add Stochastic Oscillator"""
        try:
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Stochastic signals
            df['stoch_oversold'] = df['stoch_k'] < 20
            df['stoch_overbought'] = df['stoch_k'] > 80
            
        except Exception as e:
            logger.error(f"Error adding Stochastic: {e}")
        
        return df
    
    @staticmethod
    def _add_williams_r(df: pd.DataFrame) -> pd.DataFrame:
        """Add Williams %R"""
        try:
            df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
            
        except Exception as e:
            logger.error(f"Error adding Williams %R: {e}")
        
        return df
    
    @staticmethod
    def _add_cci(df: pd.DataFrame) -> pd.DataFrame:
        """Add Commodity Channel Index"""
        try:
            df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
            
        except Exception as e:
            logger.error(f"Error adding CCI: {e}")
        
        return df
    
    @staticmethod
    def _add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add volume indicators"""
        try:
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['volume_spike'] = df['volume_ratio'] > 2.0
            
            # Volume Price Trend
            df['vpt'] = ta.volume.VolumePriceTrendIndicator(df['close'], df['volume']).volume_price_trend()
            
            # Money Flow Index
            df['mfi'] = ta.volume.MFIIndicator(df['high'], df['low'], df['close'], df['volume']).money_flow_index()
            
        except Exception as e:
            logger.error(f"Error adding volume indicators: {e}")
        
        return df
    
    @staticmethod
    def _add_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Add On Balance Volume"""
        try:
            df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            
        except Exception as e:
            logger.error(f"Error adding OBV: {e}")
        
        return df
    
    @staticmethod
    def _add_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Add VWAP"""
        try:
            df['vwap'] = ta.volume.VolumeWeightedAveragePrice(df['high'], df['low'], df['close'], df['volume']).volume_weighted_average_price()
            
        except Exception as e:
            logger.error(f"Error adding VWAP: {e}")
        
        return df
    
    @staticmethod
    def _add_atr(df: pd.DataFrame) -> pd.DataFrame:
        """Add Average True Range"""
        try:
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            
        except Exception as e:
            logger.error(f"Error adding ATR: {e}")
        
        return df
    
    @staticmethod
    def _add_keltner_channels(df: pd.DataFrame) -> pd.DataFrame:
        """Add Keltner Channels"""
        try:
            keltner = ta.volatility.KeltnerChannel(df['high'], df['low'], df['close'])
            df['keltner_upper'] = keltner.keltner_channel_hband()
            df['keltner_lower'] = keltner.keltner_channel_lband()
            df['keltner_middle'] = keltner.keltner_channel_mband()
            
        except Exception as e:
            logger.error(f"Error adding Keltner Channels: {e}")
        
        return df
    
    @staticmethod
    def _add_price_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """Add price action patterns"""
        try:
            # Price change
            df['price_change'] = df['close'].pct_change()
            df['price_change_ma'] = df['price_change'].rolling(window=20).mean()
            
            # High/Low analysis
            df['higher_high'] = df['high'] > df['high'].shift(1)
            df['lower_low'] = df['low'] < df['low'].shift(1)
            
            # Gap detection
            df['gap_up'] = df['open'] > df['close'].shift(1)
            df['gap_down'] = df['open'] < df['close'].shift(1)
            
            # Doji detection
            body_size = abs(df['close'] - df['open'])
            total_range = df['high'] - df['low']
            df['doji'] = (body_size / total_range) < 0.1
            
        except Exception as e:
            logger.error(f"Error adding price patterns: {e}")
        
        return df
    
    @staticmethod
    def _add_support_resistance(df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels"""
        try:
            # Pivot points
            df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
            df['r1'] = 2 * df['pivot'] - df['low']
            df['s1'] = 2 * df['pivot'] - df['high']
            df['r2'] = df['pivot'] + (df['high'] - df['low'])
            df['s2'] = df['pivot'] - (df['high'] - df['low'])
            
            # Support/Resistance breaks
            df['resistance_break'] = df['close'] > df['r1']
            df['support_break'] = df['close'] < df['s1']
            
        except Exception as e:
            logger.error(f"Error adding support/resistance: {e}")
        
        return df

class SignalGenerator:
    """Advanced signal generation utilities"""
    
    @staticmethod
    def detect_sniper_entries(df: pd.DataFrame) -> List[Dict]:
        """Detect multiple sniper entry opportunities"""
        signals = []
        
        try:
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 1. Strong momentum signals
            if (current['rsi'] < 30 and prev['rsi'] >= 30 and 
                current['volume_ratio'] > 1.5):
                signals.append({
                    "type": "RSI_OVERSOLD_REVERSAL",
                    "strength": "STRONG",
                    "confidence": 85
                })
            
            # 2. MACD bullish crossover with volume
            if (current['macd_bullish_cross'] and 
                current['volume_ratio'] > 1.2):
                signals.append({
                    "type": "MACD_BULLISH_CROSS",
                    "strength": "MEDIUM",
                    "confidence": 75
                })
            
            # 3. Bollinger Band squeeze breakout
            if (current['bb_width'] < 0.1 and 
                current['close'] > current['bb_upper'] and
                current['volume_ratio'] > 1.5):
                signals.append({
                    "type": "BB_SQUEEZE_BREAKOUT",
                    "strength": "STRONG",
                    "confidence": 90
                })
            
            # 4. Golden cross with momentum
            if (current['golden_cross'] and 
                current['price_change'] > 0.01):
                signals.append({
                    "type": "GOLDEN_CROSS",
                    "strength": "MEDIUM",
                    "confidence": 70
                })
            
            # 5. Volume spike with price action
            if (current['volume_spike'] and 
                current['price_change'] > 0.02):
                signals.append({
                    "type": "VOLUME_SPIKE_MOMENTUM",
                    "strength": "STRONG",
                    "confidence": 80
                })
            
            # 6. Support/Resistance break with confirmation
            if (current['resistance_break'] and 
                current['volume_ratio'] > 1.3):
                signals.append({
                    "type": "RESISTANCE_BREAK",
                    "strength": "STRONG",
                    "confidence": 85
                })
            
            # 7. Stochastic oversold reversal
            if (current['stoch_oversold'] and 
                current['stoch_k'] > current['stoch_d'] and
                prev['stoch_k'] <= prev['stoch_d']):
                signals.append({
                    "type": "STOCH_OVERSOLD_REVERSAL",
                    "strength": "MEDIUM",
                    "confidence": 75
                })
            
            # 8. VWAP bounce
            if (current['close'] > current['vwap'] and 
                prev['close'] <= prev['vwap'] and
                current['volume_ratio'] > 1.2):
                signals.append({
                    "type": "VWAP_BOUNCE",
                    "strength": "MEDIUM",
                    "confidence": 70
                })
            
            # 9. Fibonacci retracement bounce
            if (current['fib_support'] and 
                current['volume_ratio'] > 1.2):
                signals.append({
                    "type": "FIBONACCI_RETRACEMENT",
                    "strength": "MEDIUM",
                    "confidence": 75
                })
            
            # 10. Bullish divergence
            if (current['bullish_divergence'] and 
                current['volume_ratio'] > 1.3):
                signals.append({
                    "type": "BULLISH_DIVERGENCE",
                    "strength": "STRONG",
                    "confidence": 85
                })
            
            # 11. Momentum acceleration
            if (current['momentum_bullish'] and 
                current['price_change'] > 0.015):
                signals.append({
                    "type": "MOMENTUM_ACCELERATION",
                    "strength": "MEDIUM",
                    "confidence": 70
                })
            
            # 12. Breakout confirmation
            if (current['close'] > current['sma_20'] and 
                current['close'] > current['sma_50'] and
                current['volume_ratio'] > 1.4):
                signals.append({
                    "type": "BREAKOUT_CONFIRMATION",
                    "strength": "STRONG",
                    "confidence": 80
                })
            
        except Exception as e:
            logger.error(f"Error detecting sniper entries: {e}")
        
        return signals
    
    @staticmethod
    def calculate_risk_levels(entry_price: float, atr: float, direction: str) -> Dict:
        """Calculate dynamic risk levels based on ATR"""
        try:
            if direction == "LONG":
                stop_loss = entry_price - (atr * 2)  # 2 ATR below entry
                take_profit = entry_price + (atr * 4)  # 4 ATR above entry
            else:
                stop_loss = entry_price + (atr * 2)  # 2 ATR above entry
                take_profit = entry_price - (atr * 4)  # 4 ATR below entry
            
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            ratio = reward / risk if risk > 0 else 0
            
            return {
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk": risk,
                "reward": reward,
                "ratio": ratio,
                "risk_percentage": (risk / entry_price) * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk levels: {e}")
            return {}

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_ohlcv_data(df: pd.DataFrame) -> bool:
        """Validate OHLCV data quality"""
        try:
            # Check for required columns
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                return False
            
            # Check for null values
            if df[required_cols].isnull().any().any():
                return False
            
            # Check for negative values
            if (df[['open', 'high', 'low', 'close', 'volume']] < 0).any().any():
                return False
            
            # Check for logical errors (high < low, etc.)
            if (df['high'] < df['low']).any():
                return False
            
            if (df['high'] < df['open']).any() or (df['high'] < df['close']).any():
                return False
            
            if (df['low'] > df['open']).any() or (df['low'] > df['close']).any():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating OHLCV data: {e}")
            return False
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data"""
        try:
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Forward fill missing values
            df = df.fillna(method='ffill')
            
            # Remove outliers (optional)
            # df = df[df['volume'] > 0]  # Remove zero volume candles
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return df