"""
Enhanced Admin Panel for Crypto Sniper Bot
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from performance import PerformanceTracker, PerformanceAnalyzer
from config import Config

class AdminPanel:
    """Enhanced admin panel with performance tracking"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.performance_tracker = PerformanceTracker()
        
    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Crypto Sniper Pro Bot - Admin Panel</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }
                .header p {
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    padding: 30px;
                }
                .stat-card {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }
                .stat-card h3 {
                    margin: 0 0 10px 0;
                    color: #667eea;
                    font-size: 1.2em;
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #333;
                }
                .stat-label {
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .section {
                    padding: 30px;
                    border-bottom: 1px solid #eee;
                }
                .section h2 {
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 1.5em;
                }
                .signal-list {
                    max-height: 400px;
                    overflow-y: auto;
                }
                .signal-item {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-left: 4px solid #28a745;
                }
                .signal-item.short {
                    border-left-color: #dc3545;
                }
                .signal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .signal-symbol {
                    font-weight: bold;
                    font-size: 1.1em;
                }
                .signal-direction {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                    font-weight: bold;
                }
                .signal-direction.long {
                    background: #d4edda;
                    color: #155724;
                }
                .signal-direction.short {
                    background: #f8d7da;
                    color: #721c24;
                }
                .signal-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    font-size: 0.9em;
                }
                .detail-item {
                    display: flex;
                    justify-content: space-between;
                }
                .detail-label {
                    color: #666;
                }
                .detail-value {
                    font-weight: bold;
                }
                .performance-chart {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                }
                .chart-container {
                    height: 300px;
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    border: 1px solid #ddd;
                }
                .refresh-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1em;
                    margin-bottom: 20px;
                }
                .refresh-btn:hover {
                    background: #5a6fd8;
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .status-online {
                    background: #28a745;
                }
                .status-offline {
                    background: #dc3545;
                }
                @media (max-width: 768px) {
                    .stats-grid {
                        grid-template-columns: 1fr;
                    }
                    .signal-details {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Crypto Sniper Pro Bot</h1>
                    <p>Advanced Trading Bot with Real-time Performance Tracking</p>
                    <p>Version {{ version }} | Last Updated: {{ last_update }}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>📊 Total Signals</h3>
                        <div class="stat-value">{{ stats.total_signals }}</div>
                        <div class="stat-label">Generated Today</div>
                    </div>
                    <div class="stat-card">
                        <h3>🎯 Accuracy</h3>
                        <div class="stat-value">{{ stats.accuracy }}%</div>
                        <div class="stat-label">Last 30 Days</div>
                    </div>
                    <div class="stat-card">
                        <h3>💰 Avg Profit/Loss</h3>
                        <div class="stat-value">{{ stats.avg_profit_loss }}</div>
                        <div class="stat-label">Per Signal</div>
                    </div>
                    <div class="stat-card">
                        <h3>⚡ Active Signals</h3>
                        <div class="stat-value">{{ stats.active_signals }}</div>
                        <div class="stat-label">Currently Open</div>
                    </div>
                    <div class="stat-card">
                        <h3>📈 Win Rate</h3>
                        <div class="stat-value">{{ stats.win_rate }}%</div>
                        <div class="stat-label">Last 30 Days</div>
                    </div>
                    <div class="stat-card">
                        <h3>🕐 Uptime</h3>
                        <div class="stat-value">{{ stats.uptime }}</div>
                        <div class="stat-label">Hours Running</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Recent Signals</h2>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                    <div class="signal-list">
                        {% for signal in recent_signals %}
                        <div class="signal-item {{ 'short' if signal.direction == 'SHORT' else '' }}">
                            <div class="signal-header">
                                <span class="signal-symbol">{{ signal.symbol }}</span>
                                <span class="signal-direction {{ signal.direction.lower() }}">{{ signal.direction }}</span>
                            </div>
                            <div class="signal-details">
                                <div class="detail-item">
                                    <span class="detail-label">Entry Price:</span>
                                    <span class="detail-value">${{ "%.4f"|format(signal.entry_price) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Stop Loss:</span>
                                    <span class="detail-value">${{ "%.4f"|format(signal.stop_loss) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Take Profit:</span>
                                    <span class="detail-value">${{ "%.4f"|format(signal.take_profit) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Confidence:</span>
                                    <span class="detail-value">{{ signal.confidence }}%</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Risk/Reward:</span>
                                    <span class="detail-value">1:{{ "%.1f"|format(signal.risk_reward.ratio) }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Time:</span>
                                    <span class="detail-value">{{ signal.timestamp.strftime('%H:%M:%S') }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Performance Analytics</h2>
                    <div class="performance-chart">
                        <h3>Best Performing Symbols (Last 30 Days)</h3>
                        <div class="chart-container">
                            {% for symbol in best_symbols %}
                            <div style="margin-bottom: 10px;">
                                <strong>{{ symbol.symbol }}</strong>: {{ "%.1f"|format(symbol.accuracy) }}% accuracy
                                ({{ symbol.total_signals }} signals)
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>⚙️ System Status</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <strong>Bot Status:</strong>
                            <span class="status-indicator status-online"></span>Online
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <strong>Monitored Pairs:</strong> {{ system_status.symbols_monitored }}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <strong>Data Points:</strong> {{ system_status.market_data_points }}
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <strong>Memory Usage:</strong> {{ system_status.memory_usage }}
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(function() {
                    location.reload();
                }, 30000);
            </script>
        </body>
        </html>
        """
    
    def get_dashboard_data(self):
        """Get dashboard data"""
        try:
            # Get performance stats
            performance_stats = self.performance_tracker.get_performance_stats(30)
            
            # Get recent signals
            recent_signals = self.performance_tracker.get_signal_history(10)
            
            # Get best performing symbols
            best_symbols = []
            for symbol in self.bot.SYMBOLS[:5]:  # Top 5 symbols
                symbol_stats = self.performance_tracker.get_symbol_performance(symbol, 30)
                if symbol_stats['total_signals'] > 0:
                    best_symbols.append(symbol_stats)
            
            # Sort by accuracy
            best_symbols.sort(key=lambda x: x['accuracy_percentage'], reverse=True)
            
            # Calculate uptime
            uptime_hours = int((datetime.now() - self.bot.start_time).total_seconds() / 3600)
            
            # System status
            system_status = {
                'symbols_monitored': len(self.bot.SYMBOLS),
                'market_data_points': sum(len(data) for data in self.bot.market_data.values()),
                'memory_usage': f"{len(self.bot.signals)} signals stored"
            }
            
            return {
                'version': Config.BOT_VERSION,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stats': {
                    'total_signals': len(self.bot.signals),
                    'accuracy': performance_stats.get('accuracy_percentage', 0),
                    'avg_profit_loss': performance_stats.get('avg_profit_loss', 0),
                    'active_signals': len([s for s in recent_signals if s['status'] == 'ACTIVE']),
                    'win_rate': performance_stats.get('win_rate', 0),
                    'uptime': uptime_hours
                },
                'recent_signals': recent_signals,
                'best_symbols': best_symbols,
                'system_status': system_status
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                'version': Config.BOT_VERSION,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stats': {
                    'total_signals': 0,
                    'accuracy': 0,
                    'avg_profit_loss': 0,
                    'active_signals': 0,
                    'win_rate': 0,
                    'uptime': 0
                },
                'recent_signals': [],
                'best_symbols': [],
                'system_status': {
                    'symbols_monitored': 0,
                    'market_data_points': 0,
                    'memory_usage': '0 signals stored'
                }
            }
    
    def render_dashboard(self):
        """Render the dashboard"""
        data = self.get_dashboard_data()
        template = self.get_dashboard_html()
        return render_template_string(template, **data)
    
    def get_api_data(self):
        """Get API data for external access"""
        try:
            performance_stats = self.performance_tracker.get_performance_stats(30)
            recent_signals = self.performance_tracker.get_signal_history(20)
            
            return {
                'bot_info': {
                    'name': Config.BOT_NAME,
                    'version': Config.BOT_VERSION,
                    'uptime_hours': int((datetime.now() - self.bot.start_time).total_seconds() / 3600)
                },
                'performance': performance_stats,
                'recent_signals': recent_signals,
                'system_status': {
                    'symbols_monitored': len(self.bot.SYMBOLS),
                    'active_signals': len([s for s in recent_signals if s['status'] == 'ACTIVE']),
                    'total_signals_generated': len(self.bot.signals)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting API data: {e}")
            return {'error': str(e)}