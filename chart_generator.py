"""
Real-time Chart Generator for CryptoSniperXProBot
Features: Institutional-grade charts with Z+++ indicators, multiple timeframes, and signal overlays
"""

import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
import io
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generate institutional-grade charts with real-time data"""
    
    def __init__(self):
        self.chart_cache = {}
        self.chart_style = {
            'background_color': '#1e1e1e',
            'text_color': '#ffffff',
            'grid_color': '#2d2d2d',
            'up_color': '#00ff88',
            'down_color': '#ff4444',
            'volume_color': '#4a90e2'
        }
    
    def generate_signal_chart(self, symbol: str, df: pd.DataFrame, signal: Dict) -> str:
        """Generate comprehensive chart for trading signal"""
        try:
            # Create subplot layout
            fig = sp.make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.2, 0.15, 0.15],
                subplot_titles=(
                    f'{symbol} - {signal["type"]} Signal',
                    'Volume & Momentum',
                    'RSI & MACD',
                    'Z+++ Indicators'
                )
            )
            
            # Main price chart
            self._add_candlestick_chart(fig, df, row=1)
            self._add_indicators_main(fig, df, row=1)
            
            # Volume and momentum
            self._add_volume_chart(fig, df, row=2)
            self._add_momentum_indicators(fig, df, row=2)
            
            # RSI and MACD
            self._add_rsi_chart(fig, df, row=3)
            self._add_macd_chart(fig, df, row=3)
            
            # Z+++ indicators
            self._add_z_indicators(fig, df, row=4)
            
            # Add signal markers
            self._add_signal_markers(fig, df, signal)
            
            # Update layout
            self._update_chart_layout(fig, symbol, signal)
            
            # Convert to image
            return self._chart_to_image(fig)
            
        except Exception as e:
            logger.error(f"Error generating signal chart: {e}")
            return self._generate_error_chart(symbol, signal)
    
    def _add_candlestick_chart(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add candlestick chart"""
        try:
            # Candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price',
                    increasing_line_color=self.chart_style['up_color'],
                    decreasing_line_color=self.chart_style['down_color']
                ),
                row=row, col=1
            )
            
            # EMAs
            if 'ema_9' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_9'],
                        name='EMA 9',
                        line=dict(color='#ff6b6b', width=1)
                    ),
                    row=row, col=1
                )
            
            if 'ema_21' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_21'],
                        name='EMA 21',
                        line=dict(color='#4ecdc4', width=1)
                    ),
                    row=row, col=1
                )
            
            if 'ema_50' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_50'],
                        name='EMA 50',
                        line=dict(color='#45b7d1', width=1)
                    ),
                    row=row, col=1
                )
            
            # VWAP
            if 'vwap' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['vwap'],
                        name='VWAP',
                        line=dict(color='#f39c12', width=1, dash='dash')
                    ),
                    row=row, col=1
                )
            
        except Exception as e:
            logger.error(f"Error adding candlestick chart: {e}")
    
    def _add_indicators_main(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add main chart indicators"""
        try:
            # Bollinger Bands
            if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['bb_upper'],
                        name='BB Upper',
                        line=dict(color='rgba(255,255,255,0.3)', width=1),
                        showlegend=False
                    ),
                    row=row, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['bb_lower'],
                        name='BB Lower',
                        line=dict(color='rgba(255,255,255,0.3)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(255,255,255,0.1)',
                        showlegend=False
                    ),
                    row=row, col=1
                )
            
            # Support and Resistance levels
            self._add_support_resistance(fig, df, row)
            
        except Exception as e:
            logger.error(f"Error adding main indicators: {e}")
    
    def _add_support_resistance(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add support and resistance levels"""
        try:
            # Calculate recent support and resistance
            recent_high = df['high'].tail(20).max()
            recent_low = df['low'].tail(20).min()
            current_price = df['close'].iloc[-1]
            
            # Add horizontal lines
            fig.add_hline(
                y=recent_high,
                line_dash="dash",
                line_color="red",
                annotation_text="Resistance",
                row=row, col=1
            )
            
            fig.add_hline(
                y=recent_low,
                line_dash="dash",
                line_color="green",
                annotation_text="Support",
                row=row, col=1
            )
            
        except Exception as e:
            logger.error(f"Error adding support/resistance: {e}")
    
    def _add_volume_chart(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add volume chart"""
        try:
            # Volume bars
            colors = [self.chart_style['up_color'] if close > open else self.chart_style['down_color'] 
                     for close, open in zip(df['close'], df['open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=row, col=1
            )
            
            # Volume SMA
            if 'volume_sma' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['volume_sma'],
                        name='Volume SMA',
                        line=dict(color='#ffffff', width=1)
                    ),
                    row=row, col=1
                )
            
        except Exception as e:
            logger.error(f"Error adding volume chart: {e}")
    
    def _add_momentum_indicators(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add momentum indicators"""
        try:
            # Momentum score
            if 'z_momentum_score' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['z_momentum_score'],
                        name='Momentum Score',
                        line=dict(color='#ff6b6b', width=2),
                        yaxis='y2'
                    ),
                    row=row, col=1
                )
            
            # Volume ratio
            if 'volume_ratio' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['volume_ratio'],
                        name='Volume Ratio',
                        line=dict(color='#4ecdc4', width=1),
                        yaxis='y3'
                    ),
                    row=row, col=1
                )
            
        except Exception as e:
            logger.error(f"Error adding momentum indicators: {e}")
    
    def _add_rsi_chart(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add RSI chart"""
        try:
            if 'rsi' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['rsi'],
                        name='RSI',
                        line=dict(color='#ff6b6b', width=2)
                    ),
                    row=row, col=1
                )
                
                # Overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="white", row=row, col=1)
                
        except Exception as e:
            logger.error(f"Error adding RSI chart: {e}")
    
    def _add_macd_chart(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add MACD chart"""
        try:
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['macd'],
                        name='MACD',
                        line=dict(color='#4ecdc4', width=2)
                    ),
                    row=row, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['macd_signal'],
                        name='MACD Signal',
                        line=dict(color='#ff6b6b', width=2)
                    ),
                    row=row, col=1
                )
                
                # MACD histogram
                macd_hist = df['macd'] - df['macd_signal']
                colors = ['green' if val > 0 else 'red' for val in macd_hist]
                
                fig.add_trace(
                    go.Bar(
                        x=df['timestamp'],
                        y=macd_hist,
                        name='MACD Histogram',
                        marker_color=colors,
                        opacity=0.7
                    ),
                    row=row, col=1
                )
                
        except Exception as e:
            logger.error(f"Error adding MACD chart: {e}")
    
    def _add_z_indicators(self, fig: go.Figure, df: pd.DataFrame, row: int):
        """Add Z+++ indicators"""
        try:
            # Trend strength
            if 'z_trend_strength' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['z_trend_strength'],
                        name='Trend Strength',
                        line=dict(color='#45b7d1', width=2)
                    ),
                    row=row, col=1
                )
            
            # Overall score
            if 'z_overall_score' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['z_overall_score'],
                        name='Z+++ Score',
                        line=dict(color='#f39c12', width=2)
                    ),
                    row=row, col=1
                )
            
            # Volatility score
            if 'z_volatility_score' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['z_volatility_score'],
                        name='Volatility Score',
                        line=dict(color='#e74c3c', width=1)
                    ),
                    row=row, col=1
                )
            
        except Exception as e:
            logger.error(f"Error adding Z indicators: {e}")
    
    def _add_signal_markers(self, fig: go.Figure, df: pd.DataFrame, signal: Dict):
        """Add signal markers to chart"""
        try:
            signal_time = signal.get('timestamp', df['timestamp'].iloc[-1])
            signal_price = signal.get('price', df['close'].iloc[-1])
            
            # Add signal marker
            fig.add_trace(
                go.Scatter(
                    x=[signal_time],
                    y=[signal_price],
                    mode='markers',
                    marker=dict(
                        symbol='star',
                        size=15,
                        color='yellow',
                        line=dict(color='black', width=2)
                    ),
                    name=f"{signal['type']} Signal",
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Add signal annotation
            fig.add_annotation(
                x=signal_time,
                y=signal_price,
                text=f"{signal['type']}<br>Confidence: {signal.get('confidence', 0)}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='yellow',
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='yellow',
                borderwidth=1,
                font=dict(color='white', size=10)
            )
            
        except Exception as e:
            logger.error(f"Error adding signal markers: {e}")
    
    def _update_chart_layout(self, fig: go.Figure, symbol: str, signal: Dict):
        """Update chart layout"""
        try:
            fig.update_layout(
                title=dict(
                    text=f"{symbol} - {signal['type']} Signal Analysis",
                    x=0.5,
                    font=dict(size=16, color=self.chart_style['text_color'])
                ),
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color']),
                xaxis=dict(
                    gridcolor=self.chart_style['grid_color'],
                    showgrid=True
                ),
                yaxis=dict(
                    gridcolor=self.chart_style['grid_color'],
                    showgrid=True
                ),
                legend=dict(
                    bgcolor='rgba(0,0,0,0.8)',
                    bordercolor='white',
                    borderwidth=1
                ),
                height=800,
                width=1200
            )
            
            # Update all subplot axes
            for i in range(1, 5):
                fig.update_xaxes(
                    gridcolor=self.chart_style['grid_color'],
                    showgrid=True,
                    row=i, col=1
                )
                fig.update_yaxes(
                    gridcolor=self.chart_style['grid_color'],
                    showgrid=True,
                    row=i, col=1
                )
            
        except Exception as e:
            logger.error(f"Error updating chart layout: {e}")
    
    def _chart_to_image(self, fig: go.Figure) -> str:
        """Convert chart to base64 image"""
        try:
            # Convert to image
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error converting chart to image: {e}")
            return ""
    
    def _generate_error_chart(self, symbol: str, signal: Dict) -> str:
        """Generate error chart when main chart fails"""
        try:
            fig = go.Figure()
            
            fig.add_annotation(
                text=f"Chart generation failed for {symbol}<br>Signal: {signal['type']}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="red")
            )
            
            fig.update_layout(
                title=f"Error - {symbol} Chart",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                height=400,
                width=600
            )
            
            return self._chart_to_image(fig)
            
        except Exception as e:
            logger.error(f"Error generating error chart: {e}")
            return ""
    
    def generate_arbitrage_chart(self, opportunity: Dict) -> str:
        """Generate arbitrage opportunity chart"""
        try:
            fig = go.Figure()
            
            # Create price comparison
            exchanges = [opportunity['buy_exchange'], opportunity['sell_exchange']]
            prices = [opportunity['buy_price'], opportunity['sell_price']]
            colors = ['red', 'green']
            
            fig.add_trace(
                go.Bar(
                    x=exchanges,
                    y=prices,
                    marker_color=colors,
                    name='Prices',
                    text=[f"${p:.4f}" for p in prices],
                    textposition='auto'
                )
            )
            
            fig.update_layout(
                title=f"Arbitrage Opportunity - {opportunity['symbol']}<br>Profit: {opportunity['profit_pct']:.2f}%",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color']),
                height=400,
                width=600
            )
            
            return self._chart_to_image(fig)
            
        except Exception as e:
            logger.error(f"Error generating arbitrage chart: {e}")
            return ""
    
    def generate_multi_timeframe_chart(self, symbol: str, data_dict: Dict) -> str:
        """Generate multi-timeframe analysis chart"""
        try:
            fig = sp.make_subplots(
                rows=len(data_dict), cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=[f"{symbol} - {tf}" for tf in data_dict.keys()]
            )
            
            row = 1
            for timeframe, df in data_dict.items():
                # Add candlestick for each timeframe
                fig.add_trace(
                    go.Candlestick(
                        x=df['timestamp'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=timeframe,
                        increasing_line_color=self.chart_style['up_color'],
                        decreasing_line_color=self.chart_style['down_color']
                    ),
                    row=row, col=1
                )
                
                # Add EMAs
                if 'ema_21' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['ema_21'],
                            name=f'EMA 21 ({timeframe})',
                            line=dict(color='#4ecdc4', width=1)
                        ),
                        row=row, col=1
                    )
                
                row += 1
            
            fig.update_layout(
                title=f"{symbol} - Multi-Timeframe Analysis",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color']),
                height=800,
                width=1200
            )
            
            return self._chart_to_image(fig)
            
        except Exception as e:
            logger.error(f"Error generating multi-timeframe chart: {e}")
            return ""