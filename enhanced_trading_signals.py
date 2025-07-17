"""
Enhanced Trading Signals System for CryptoSniperXProBot
Features: Day Trading, Scalping, Swing Trading, Support/Resistance, Smart Leverage
"""

import os
import time
import json
import asyncio
import threading
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import numpy as np
import pandas as pd
import ta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Local imports
from config import Config
from utils import TechnicalAnalysis, SignalGenerator, DataValidator
from advanced_indicators import InstitutionalZPlusPlus

logger = logging.getLogger(__name__)

class SmartAITradingLogic:
    """Advanced AI logic for trading decisions"""
    
    def __init__(self):
        self.momentum_threshold = 0.6
        self.volatility_threshold = 0.4
        self.trend_strength_threshold = 0.7
        self.risk_score_threshold = 0.3
        
    def analyze_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze market momentum using multiple indicators"""
        try:
            # RSI momentum
            rsi = ta.momentum.RSIIndicator(df['close']).rsi()
            rsi_momentum = (rsi.iloc[-1] - 50) / 50  # Normalize to -1 to 1
            
            # MACD momentum
            macd = ta.trend.MACD(df['close'])
            macd_line = macd.macd()
            signal_line = macd.macd_signal()
            macd_momentum = (macd_line.iloc[-1] - signal_line.iloc[-1]) / df['close'].iloc[-1]
            
            # Stochastic momentum
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            stoch_k = stoch.stoch()
            stoch_momentum = (stoch_k.iloc[-1] - 50) / 50
            
            # Williams %R momentum
            williams_r = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close'])
            williams_r_value = williams_r.williams_r()
            williams_momentum = (williams_r_value.iloc[-1] + 100) / 100  # Normalize to 0 to 1
            
            # Volume momentum
            volume_sma = df['volume'].rolling(20).mean()
            volume_momentum = (df['volume'].iloc[-1] - volume_sma.iloc[-1]) / volume_sma.iloc[-1]
            
            # Combined momentum score
            momentum_score = (
                rsi_momentum * 0.25 +
                macd_momentum * 0.25 +
                stoch_momentum * 0.2 +
                williams_momentum * 0.2 +
                volume_momentum * 0.1
            )
            
            return {
                'overall_momentum': momentum_score,
                'rsi_momentum': rsi_momentum,
                'macd_momentum': macd_momentum,
                'stoch_momentum': stoch_momentum,
                'williams_momentum': williams_momentum,
                'volume_momentum': volume_momentum,
                'is_bullish': momentum_score > self.momentum_threshold,
                'is_bearish': momentum_score < -self.momentum_threshold
            }
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {e}")
            return {'overall_momentum': 0, 'is_bullish': False, 'is_bearish': False}
    
    def calculate_smart_tp_sl(self, entry_price: float, signal_type: str, 
                             volatility: float, momentum: float) -> Dict[str, float]:
        """Calculate smart Take Profit and Stop Loss levels"""
        try:
            # Base percentages based on signal type
            base_tp_percent = 0.03  # 3% base TP
            base_sl_percent = 0.02  # 2% base SL
            
            # Adjust based on volatility
            volatility_multiplier = 1 + (volatility * 2)
            
            # Adjust based on momentum strength
            momentum_multiplier = 1 + abs(momentum)
            
            # Calculate TP/SL levels
            if signal_type == 'LONG':
                take_profit = entry_price * (1 + (base_tp_percent * volatility_multiplier * momentum_multiplier))
                stop_loss = entry_price * (1 - (base_sl_percent * volatility_multiplier))
            else:  # SHORT
                take_profit = entry_price * (1 - (base_tp_percent * volatility_multiplier * momentum_multiplier))
                stop_loss = entry_price * (1 + (base_sl_percent * volatility_multiplier))
            
            # Ensure minimum risk/reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if reward / risk < Config.MIN_RISK_REWARD_RATIO:
                # Adjust TP to meet minimum R/R ratio
                if signal_type == 'LONG':
                    take_profit = entry_price + (risk * Config.MIN_RISK_REWARD_RATIO)
                else:
                    take_profit = entry_price - (risk * Config.MIN_RISK_REWARD_RATIO)
            
            return {
                'take_profit': round(take_profit, 6),
                'stop_loss': round(stop_loss, 6),
                'risk_reward_ratio': round(reward / risk, 2),
                'risk_amount': round(risk, 6),
                'reward_amount': round(reward, 6)
            }
            
        except Exception as e:
            logger.error(f"Error calculating TP/SL: {e}")
            return {
                'take_profit': entry_price * 1.03,
                'stop_loss': entry_price * 0.98,
                'risk_reward_ratio': 1.5,
                'risk_amount': entry_price * 0.02,
                'reward_amount': entry_price * 0.03
            }
    
    def calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate market volatility"""
        try:
            # ATR-based volatility
            atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'])
            atr_value = atr.average_true_range()
            
            # Price volatility
            returns = df['close'].pct_change()
            price_volatility = returns.std()
            
            # Volume volatility
            volume_volatility = df['volume'].pct_change().std()
            
            # Combined volatility score
            volatility_score = (
                (atr_value.iloc[-1] / df['close'].iloc[-1]) * 0.5 +
                price_volatility * 0.3 +
                volume_volatility * 0.2
            )
            
            return min(volatility_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.1
    
    def calculate_risk_score(self, signal_data: Dict) -> float:
        """Calculate comprehensive risk score"""
        try:
            risk_factors = []
            
            # Volatility risk
            volatility_risk = signal_data.get('volatility', 0.1)
            risk_factors.append(volatility_risk * 0.3)
            
            # Momentum risk (inverse relationship)
            momentum = abs(signal_data.get('momentum', {}).get('overall_momentum', 0))
            momentum_risk = 1 - momentum
            risk_factors.append(momentum_risk * 0.2)
            
            # Volume risk
            volume_ratio = signal_data.get('volume_ratio', 1.0)
            volume_risk = 1 / max(volume_ratio, 0.1)
            risk_factors.append(volume_risk * 0.2)
            
            # Trend strength risk
            trend_strength = signal_data.get('trend_strength', 0.5)
            trend_risk = 1 - trend_strength
            risk_factors.append(trend_risk * 0.2)
            
            # Market condition risk
            market_condition = signal_data.get('market_condition', 'neutral')
            market_risk = 0.5 if market_condition == 'neutral' else 0.3
            risk_factors.append(market_risk * 0.1)
            
            # Calculate weighted average risk score
            total_risk = sum(risk_factors)
            
            return min(total_risk, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5

class DynamicMarketScanner:
    """Dynamic market scanning system"""
    
    def __init__(self):
        self.scan_interval = 30  # seconds
        self.last_scan_time = {}
        self.scan_results = {}
        self.active_scans = set()
        
    def should_scan_symbol(self, symbol: str) -> bool:
        """Determine if symbol should be scanned"""
        current_time = time.time()
        last_scan = self.last_scan_time.get(symbol, 0)
        
        # Scan if enough time has passed
        if current_time - last_scan >= self.scan_interval:
            self.last_scan_time[symbol] = current_time
            return True
        
        return False
    
    def scan_market_conditions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Scan current market conditions"""
        try:
            # Market trend analysis
            sma_20 = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
            sma_50 = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
            
            current_price = df['close'].iloc[-1]
            trend_direction = 'bullish' if current_price > sma_20.iloc[-1] > sma_50.iloc[-1] else 'bearish'
            
            # Volatility analysis
            atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'])
            current_atr = atr.average_true_range().iloc[-1]
            avg_atr = atr.average_true_range().rolling(20).mean().iloc[-1]
            volatility_regime = 'high' if current_atr > avg_atr * 1.5 else 'low' if current_atr < avg_atr * 0.5 else 'normal'
            
            # Volume analysis
            volume_sma = df['volume'].rolling(20).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_sma.iloc[-1]
            
            # Support/Resistance levels
            support_levels = self._find_support_levels(df)
            resistance_levels = self._find_resistance_levels(df)
            
            return {
                'trend_direction': trend_direction,
                'volatility_regime': volatility_regime,
                'volume_ratio': volume_ratio,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'current_price': current_price,
                'sma_20': sma_20.iloc[-1],
                'sma_50': sma_50.iloc[-1],
                'atr': current_atr,
                'avg_atr': avg_atr
            }
            
        except Exception as e:
            logger.error(f"Error scanning market conditions: {e}")
            return {
                'trend_direction': 'neutral',
                'volatility_regime': 'normal',
                'volume_ratio': 1.0,
                'support_levels': [],
                'resistance_levels': [],
                'current_price': df['close'].iloc[-1] if len(df) > 0 else 0
            }
    
    def _find_support_levels(self, df: pd.DataFrame) -> List[float]:
        """Find support levels using pivot points"""
        try:
            pivots = ta.trend.PSARIndicator(df['high'], df['low'], df['close'])
            pivot_points = pivots.psar()
            
            # Find local minima
            support_levels = []
            for i in range(2, len(df) - 2):
                if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                    df['low'].iloc[i] < df['low'].iloc[i-2] and
                    df['low'].iloc[i] < df['low'].iloc[i+1] and
                    df['low'].iloc[i] < df['low'].iloc[i+2]):
                    support_levels.append(df['low'].iloc[i])
            
            # Return unique levels within 1% of each other
            unique_levels = []
            for level in sorted(support_levels):
                if not any(abs(level - existing) / existing < 0.01 for existing in unique_levels):
                    unique_levels.append(level)
            
            return unique_levels[-3:]  # Return last 3 support levels
            
        except Exception as e:
            logger.error(f"Error finding support levels: {e}")
            return []
    
    def _find_resistance_levels(self, df: pd.DataFrame) -> List[float]:
        """Find resistance levels using pivot points"""
        try:
            # Find local maxima
            resistance_levels = []
            for i in range(2, len(df) - 2):
                if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                    df['high'].iloc[i] > df['high'].iloc[i-2] and
                    df['high'].iloc[i] > df['high'].iloc[i+1] and
                    df['high'].iloc[i] > df['high'].iloc[i+2]):
                    resistance_levels.append(df['high'].iloc[i])
            
            # Return unique levels within 1% of each other
            unique_levels = []
            for level in sorted(resistance_levels):
                if not any(abs(level - existing) / existing < 0.01 for existing in unique_levels):
                    unique_levels.append(level)
            
            return unique_levels[-3:]  # Return last 3 resistance levels
            
        except Exception as e:
            logger.error(f"Error finding resistance levels: {e}")
            return []

class EmailNotifier:
    """Email notification system"""
    
    def __init__(self):
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.recipient_email = Config.RECIPIENT_EMAIL
        
    def send_signal_email(self, signal: Dict):
        """Send trading signal via email"""
        try:
            if not all([self.smtp_server, self.email_address, self.email_password, self.recipient_email]):
                logger.warning("Email configuration incomplete, skipping email notification")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = f"🚨 {signal['signal_type']} Signal: {signal['symbol']}"
            
            # Create HTML body
            html_body = self._create_signal_email_html(signal)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Signal email sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending signal email: {e}")
    
    def _create_signal_email_html(self, signal: Dict) -> str:
        """Create HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .signal-card {{ 
                    border: 2px solid #007bff; 
                    border-radius: 10px; 
                    padding: 20px; 
                    margin: 10px 0; 
                    background-color: #f8f9fa;
                }}
                .signal-type {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: {'#28a745' if signal['signal_type'] == 'LONG' else '#dc3545'};
                }}
                .symbol {{ font-size: 20px; font-weight: bold; color: #007bff; }}
                .price {{ font-size: 18px; color: #6c757d; }}
                .tp-sl {{ 
                    background-color: #e9ecef; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }}
                .momentum {{ 
                    background-color: #d4edda; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }}
                .risk {{ 
                    background-color: #f8d7da; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="signal-card">
                <div class="signal-type">📈 {signal['signal_type']} SIGNAL</div>
                <div class="symbol">🎯 {signal['symbol']}</div>
                <div class="price">💰 Entry Price: ${signal['entry_price']:,.6f}</div>
                
                <div class="tp-sl">
                    <h3>🎯 Take Profit & Stop Loss</h3>
                    <p>📈 Take Profit: ${signal.get('take_profit', 0):,.6f}</p>
                    <p>🛑 Stop Loss: ${signal.get('stop_loss', 0):,.6f}</p>
                    <p>⚖️ Risk/Reward Ratio: {signal.get('risk_reward_ratio', 0):.2f}</p>
                </div>
                
                <div class="momentum">
                    <h3>📊 Momentum Analysis</h3>
                    <p>🎯 Overall Momentum: {signal.get('momentum', {}).get('overall_momentum', 0):.3f}</p>
                    <p>📈 Trend Direction: {signal.get('market_conditions', {}).get('trend_direction', 'Unknown')}</p>
                    <p>📊 Volatility: {signal.get('market_conditions', {}).get('volatility_regime', 'Unknown')}</p>
                </div>
                
                <div class="risk">
                    <h3>⚠️ Risk Assessment</h3>
                    <p>🎯 Risk Score: {signal.get('risk_score', 0):.3f}</p>
                    <p>💰 Risk Amount: ${signal.get('risk_amount', 0):,.6f}</p>
                    <p>💎 Reward Amount: ${signal.get('reward_amount', 0):,.6f}</p>
                </div>
                
                <p><strong>⏰ Signal Time:</strong> {signal.get('timestamp', 'Unknown')}</p>
                <p><strong>🔍 Timeframe:</strong> {signal.get('timeframe', 'Unknown')}</p>
            </div>
        </body>
        </html>
        """
        return html

class EnhancedTradingSignals:
    """Enhanced trading signals with TP/SL, momentum-based logic, and smart AI"""
    
    def __init__(self):
        self.ai_logic = SmartAITradingLogic()
        self.market_scanner = DynamicMarketScanner()
        self.email_notifier = EmailNotifier()
        self.z_plus_plus = InstitutionalZPlusPlus()
        
        # Signal tracking
        self.signal_history = []
        self.last_signal_time = {}
        self.signal_cooldown = 300  # 5 minutes between signals per symbol
        
    def generate_enhanced_signal(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Optional[Dict]:
        """Generate enhanced trading signal with TP/SL and momentum analysis"""
        try:
            # Check cooldown
            current_time = time.time()
            last_signal = self.last_signal_time.get(f"{symbol}_{timeframe}", 0)
            if current_time - last_signal < self.signal_cooldown:
                return None
            
            # Validate data
            if not DataValidator.validate_ohlcv_data(df):
                logger.warning(f"Invalid data for {symbol} {timeframe}")
                return None
            
            # Market scanning
            market_conditions = self.market_scanner.scan_market_conditions(df)
            
            # Momentum analysis
            momentum_analysis = self.ai_logic.analyze_momentum(df)
            
            # Volatility calculation
            volatility = self.ai_logic.calculate_volatility(df)
            
            # Z+++ institutional analysis
            z_plus_analysis = self.z_plus_plus.analyze_symbol(df)
            
            # Determine signal type based on momentum
            signal_type = None
            if momentum_analysis['is_bullish'] and momentum_analysis['overall_momentum'] > self.ai_logic.momentum_threshold:
                signal_type = 'LONG'
            elif momentum_analysis['is_bearish'] and momentum_analysis['overall_momentum'] < -self.ai_logic.momentum_threshold:
                signal_type = 'SHORT'
            
            if not signal_type:
                return None
            
            # Current price
            current_price = df['close'].iloc[-1]
            
            # Calculate smart TP/SL
            tp_sl_data = self.ai_logic.calculate_smart_tp_sl(
                current_price, signal_type, volatility, momentum_analysis['overall_momentum']
            )
            
            # Calculate risk score
            signal_data = {
                'volatility': volatility,
                'momentum': momentum_analysis,
                'volume_ratio': market_conditions['volume_ratio'],
                'trend_strength': abs(momentum_analysis['overall_momentum']),
                'market_condition': market_conditions['trend_direction']
            }
            risk_score = self.ai_logic.calculate_risk_score(signal_data)
            
            # Create enhanced signal
            signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': signal_type,
                'entry_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'take_profit': tp_sl_data['take_profit'],
                'stop_loss': tp_sl_data['stop_loss'],
                'risk_reward_ratio': tp_sl_data['risk_reward_ratio'],
                'risk_amount': tp_sl_data['risk_amount'],
                'reward_amount': tp_sl_data['reward_amount'],
                'momentum': momentum_analysis,
                'market_conditions': market_conditions,
                'volatility': volatility,
                'risk_score': risk_score,
                'z_plus_analysis': z_plus_analysis,
                'confidence_score': self._calculate_confidence_score(momentum_analysis, risk_score, z_plus_analysis)
            }
            
            # Update tracking
            self.last_signal_time[f"{symbol}_{timeframe}"] = current_time
            self.signal_history.append(signal)
            
            # Send notifications
            self._send_notifications(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating enhanced signal for {symbol}: {e}")
            return None
    
    def _calculate_confidence_score(self, momentum: Dict, risk_score: float, z_plus_analysis: Dict) -> float:
        """Calculate confidence score for the signal"""
        try:
            # Momentum confidence (0-1)
            momentum_confidence = abs(momentum.get('overall_momentum', 0))
            
            # Risk confidence (inverse of risk score)
            risk_confidence = 1 - risk_score
            
            # Z+++ confidence
            z_plus_confidence = z_plus_analysis.get('confidence', 0.5)
            
            # Weighted average
            confidence_score = (
                momentum_confidence * 0.4 +
                risk_confidence * 0.3 +
                z_plus_confidence * 0.3
            )
            
            return min(confidence_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def _send_notifications(self, signal: Dict):
        """Send notifications via Telegram and Email"""
        try:
            # Send email notification
            self.email_notifier.send_signal_email(signal)
            
            logger.info(f"Enhanced signal notifications sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def get_signal_history(self, limit: int = 50) -> List[Dict]:
        """Get recent signal history"""
        return self.signal_history[-limit:]
    
    def get_signal_stats(self) -> Dict:
        """Get signal statistics"""
        if not self.signal_history:
            return {}
        
        total_signals = len(self.signal_history)
        long_signals = len([s for s in self.signal_history if s['signal_type'] == 'LONG'])
        short_signals = len([s for s in self.signal_history if s['signal_type'] == 'SHORT'])
        
        avg_confidence = sum(s.get('confidence_score', 0) for s in self.signal_history) / total_signals
        avg_risk_reward = sum(s.get('risk_reward_ratio', 0) for s in self.signal_history) / total_signals
        
        return {
            'total_signals': total_signals,
            'long_signals': long_signals,
            'short_signals': short_signals,
            'avg_confidence': avg_confidence,
            'avg_risk_reward': avg_risk_reward,
            'last_signal_time': self.signal_history[-1]['timestamp'] if self.signal_history else None
        }