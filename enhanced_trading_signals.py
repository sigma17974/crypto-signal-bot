"""
Enhanced Trading Signals System for CryptoSniperXProBot
Features: Day Trading, Scalping, Swing Trading, Support/Resistance, Smart Leverage
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import ta
import math

logger = logging.getLogger(__name__)

class EnhancedTradingSignals:
    """Enhanced trading signals with multiple strategies"""
    
    def __init__(self):
        self.signal_types = {
            'DAY_TRADING': 'day_trading',
            'SCALPING': 'scalping', 
            'SWING_TRADING': 'swing_trading'
        }
        
        self.leverage_levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'AGGRESSIVE': 5
        }
        
        self.timeframes = {
            'SCALPING': ['1m', '5m'],
            'DAY_TRADING': ['15m', '1h'],
            'SWING_TRADING': ['4h', '1d']
        }
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Calculate support and resistance levels"""
        try:
            # Pivot points
            high = df['high'].max()
            low = df['low'].min()
            close = df['close'].iloc[-1]
            
            # Pivot point
            pivot = (high + low + close) / 3
            
            # Support levels
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)
            
            # Resistance levels
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)
            
            # Dynamic support/resistance using moving averages
            ma20 = df['close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['close'].rolling(window=50).mean().iloc[-1]
            ma200 = df['close'].rolling(window=200).mean().iloc[-1]
            
            # Fibonacci retracement levels
            swing_high = df['high'].max()
            swing_low = df['low'].min()
            diff = swing_high - swing_low
            
            fib_levels = {
                '0.236': swing_high - 0.236 * diff,
                '0.382': swing_high - 0.382 * diff,
                '0.500': swing_high - 0.500 * diff,
                '0.618': swing_high - 0.618 * diff,
                '0.786': swing_high - 0.786 * diff
            }
            
            return {
                'pivot': pivot,
                'support_levels': {
                    's1': s1,
                    's2': s2,
                    's3': s3,
                    'ma20': ma20,
                    'ma50': ma50,
                    'ma200': ma200
                },
                'resistance_levels': {
                    'r1': r1,
                    'r2': r2,
                    'r3': r3
                },
                'fibonacci': fib_levels,
                'current_price': close,
                'swing_high': swing_high,
                'swing_low': swing_low
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {}
    
    def calculate_smart_leverage(self, signal_type: str, confidence: float, 
                                risk_score: float, volatility: float) -> Dict:
        """Calculate smart leverage based on multiple factors"""
        try:
            # Base leverage by signal type
            base_leverage = {
                'SCALPING': 3,
                'DAY_TRADING': 2,
                'SWING_TRADING': 1
            }
            
            # Confidence multiplier (0.5 to 1.5)
            confidence_multiplier = 0.5 + (confidence / 100)
            
            # Risk adjustment (lower risk = higher leverage)
            risk_multiplier = 1.0 - (risk_score * 0.5)
            
            # Volatility adjustment
            volatility_multiplier = 1.0
            if volatility < 0.02:  # Low volatility
                volatility_multiplier = 1.2
            elif volatility > 0.05:  # High volatility
                volatility_multiplier = 0.8
            
            # Calculate final leverage
            final_leverage = base_leverage.get(signal_type, 1) * \
                           confidence_multiplier * \
                           risk_multiplier * \
                           volatility_multiplier
            
            # Cap leverage
            max_leverage = {
                'SCALPING': 5,
                'DAY_TRADING': 3,
                'SWING_TRADING': 2
            }
            
            final_leverage = min(final_leverage, max_leverage.get(signal_type, 1))
            final_leverage = max(final_leverage, 1)  # Minimum leverage of 1
            
            # Determine leverage level
            if final_leverage <= 1.5:
                level = 'LOW'
            elif final_leverage <= 2.5:
                level = 'MEDIUM'
            elif final_leverage <= 3.5:
                level = 'HIGH'
            else:
                level = 'AGGRESSIVE'
            
            return {
                'leverage': round(final_leverage, 2),
                'level': level,
                'confidence_multiplier': confidence_multiplier,
                'risk_multiplier': risk_multiplier,
                'volatility_multiplier': volatility_multiplier,
                'max_leverage': max_leverage.get(signal_type, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating smart leverage: {e}")
            return {'leverage': 1, 'level': 'LOW'}
    
    def generate_day_trading_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Generate day trading signals"""
        try:
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Get support/resistance levels
            levels = self.calculate_support_resistance(df)
            
            # Day trading specific analysis
            current_price = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]
            volume_ratio = df['volume_ratio'].iloc[-1]
            
            # Signal conditions
            bullish_conditions = [
                rsi < 40 and rsi > 30,  # Oversold but not extreme
                df['macd'].iloc[-1] > macd_signal,  # MACD bullish
                volume_ratio > 1.5,  # High volume
                current_price > df['sma_20'].iloc[-1],  # Above 20 SMA
                df['bb_position'].iloc[-1] < 0.8  # Not overbought
            ]
            
            bearish_conditions = [
                rsi > 60 and rsi < 70,  # Overbought but not extreme
                df['macd'].iloc[-1] < macd_signal,  # MACD bearish
                volume_ratio > 1.5,  # High volume
                current_price < df['sma_20'].iloc[-1],  # Below 20 SMA
                df['bb_position'].iloc[-1] > 0.2  # Not oversold
            ]
            
            confidence = 0
            signal_type = None
            
            if sum(bullish_conditions) >= 4:
                signal_type = 'LONG'
                confidence = sum(bullish_conditions) * 20
            elif sum(bearish_conditions) >= 4:
                signal_type = 'SHORT'
                confidence = sum(bearish_conditions) * 20
            
            if signal_type and confidence >= 60:
                # Calculate leverage
                volatility = df['atr'].iloc[-1] / current_price
                leverage_info = self.calculate_smart_leverage(
                    'DAY_TRADING', confidence, 0.3, volatility
                )
                
                return {
                    'type': 'DAY_TRADING',
                    'signal': signal_type,
                    'symbol': symbol,
                    'price': current_price,
                    'confidence': confidence,
                    'timeframe': '1h',
                    'support_resistance': levels,
                    'leverage': leverage_info,
                    'indicators': {
                        'rsi': rsi,
                        'macd': df['macd'].iloc[-1],
                        'volume_ratio': volume_ratio,
                        'bb_position': df['bb_position'].iloc[-1]
                    },
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating day trading signal: {e}")
            return None
    
    def generate_scalping_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Generate scalping signals"""
        try:
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Get support/resistance levels
            levels = self.calculate_support_resistance(df)
            
            # Scalping specific analysis
            current_price = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            stoch_k = df['stoch_k'].iloc[-1]
            stoch_d = df['stoch_d'].iloc[-1]
            volume_ratio = df['volume_ratio'].iloc[-1]
            
            # Scalping conditions (more sensitive)
            bullish_conditions = [
                rsi < 35,  # More oversold
                stoch_k > stoch_d and stoch_k < 80,  # Stochastic bullish
                volume_ratio > 2.0,  # Very high volume
                current_price > df['ema_9'].iloc[-1],  # Above 9 EMA
                df['bb_position'].iloc[-1] < 0.3  # Near lower BB
            ]
            
            bearish_conditions = [
                rsi > 65,  # More overbought
                stoch_k < stoch_d and stoch_k > 20,  # Stochastic bearish
                volume_ratio > 2.0,  # Very high volume
                current_price < df['ema_9'].iloc[-1],  # Below 9 EMA
                df['bb_position'].iloc[-1] > 0.7  # Near upper BB
            ]
            
            confidence = 0
            signal_type = None
            
            if sum(bullish_conditions) >= 4:
                signal_type = 'LONG'
                confidence = sum(bullish_conditions) * 20
            elif sum(bearish_conditions) >= 4:
                signal_type = 'SHORT'
                confidence = sum(bearish_conditions) * 20
            
            if signal_type and confidence >= 70:  # Higher confidence for scalping
                # Calculate leverage
                volatility = df['atr'].iloc[-1] / current_price
                leverage_info = self.calculate_smart_leverage(
                    'SCALPING', confidence, 0.4, volatility
                )
                
                return {
                    'type': 'SCALPING',
                    'signal': signal_type,
                    'symbol': symbol,
                    'price': current_price,
                    'confidence': confidence,
                    'timeframe': '5m',
                    'support_resistance': levels,
                    'leverage': leverage_info,
                    'indicators': {
                        'rsi': rsi,
                        'stoch_k': stoch_k,
                        'stoch_d': stoch_d,
                        'volume_ratio': volume_ratio,
                        'bb_position': df['bb_position'].iloc[-1]
                    },
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating scalping signal: {e}")
            return None
    
    def generate_swing_trading_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Generate swing trading signals"""
        try:
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Get support/resistance levels
            levels = self.calculate_support_resistance(df)
            
            # Swing trading specific analysis
            current_price = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]
            volume_ratio = df['volume_ratio'].iloc[-1]
            
            # Swing trading conditions (longer-term)
            bullish_conditions = [
                rsi < 45,  # Less oversold for swing
                df['macd'].iloc[-1] > macd_signal,  # MACD bullish
                volume_ratio > 1.2,  # Moderate volume
                current_price > df['sma_50'].iloc[-1],  # Above 50 SMA
                df['bb_position'].iloc[-1] < 0.4,  # Not overbought
                df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]  # Golden cross
            ]
            
            bearish_conditions = [
                rsi > 55,  # Less overbought for swing
                df['macd'].iloc[-1] < macd_signal,  # MACD bearish
                volume_ratio > 1.2,  # Moderate volume
                current_price < df['sma_50'].iloc[-1],  # Below 50 SMA
                df['bb_position'].iloc[-1] > 0.6,  # Not oversold
                df['sma_20'].iloc[-1] < df['sma_50'].iloc[-1]  # Death cross
            ]
            
            confidence = 0
            signal_type = None
            
            if sum(bullish_conditions) >= 4:
                signal_type = 'LONG'
                confidence = sum(bullish_conditions) * 15
            elif sum(bearish_conditions) >= 4:
                signal_type = 'SHORT'
                confidence = sum(bearish_conditions) * 15
            
            if signal_type and confidence >= 50:  # Lower confidence for swing
                # Calculate leverage
                volatility = df['atr'].iloc[-1] / current_price
                leverage_info = self.calculate_smart_leverage(
                    'SWING_TRADING', confidence, 0.2, volatility
                )
                
                return {
                    'type': 'SWING_TRADING',
                    'signal': signal_type,
                    'symbol': symbol,
                    'price': current_price,
                    'confidence': confidence,
                    'timeframe': '4h',
                    'support_resistance': levels,
                    'leverage': leverage_info,
                    'indicators': {
                        'rsi': rsi,
                        'macd': df['macd'].iloc[-1],
                        'volume_ratio': volume_ratio,
                        'bb_position': df['bb_position'].iloc[-1],
                        'sma_20': df['sma_20'].iloc[-1],
                        'sma_50': df['sma_50'].iloc[-1]
                    },
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating swing trading signal: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        try:
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Moving Averages
            df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
            df['ema_9'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
            
            # ATR for volatility
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            
            # Volume ratio
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def generate_all_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate all types of trading signals"""
        signals = []
        
        try:
            # Generate day trading signal
            day_signal = self.generate_day_trading_signal(df, symbol)
            if day_signal:
                signals.append(day_signal)
            
            # Generate scalping signal
            scalping_signal = self.generate_scalping_signal(df, symbol)
            if scalping_signal:
                signals.append(scalping_signal)
            
            # Generate swing trading signal
            swing_signal = self.generate_swing_trading_signal(df, symbol)
            if swing_signal:
                signals.append(swing_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating all signals: {e}")
            return signals