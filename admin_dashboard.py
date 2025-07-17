"""
Advanced Admin Dashboard for Crypto Sniper Pro Bot
Features: Telegram Auth, Auto-reconnect, Auto-cleanup, Error Detection/Repair, Auto-refresh
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import requests
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv

# Local imports
from config import Config

load_dotenv()
logger = logging.getLogger(__name__)

class AdminDashboard:
    """Advanced admin dashboard with Dynamic Controls"""
    def __init__(self, bot):
        self.bot = bot
        self.last_update = datetime.now()
        self.update_interval = 5  # seconds
        
        # Dynamic tracking
        self.active_signals = {} # Dictionary to store active signals per symbol
        self.signal_history = []
        self.performance_stats = {}
        
        # Start background updates
        self._start_background_updates()
    
    def _start_background_updates(self):
        """Start background update thread"""
        def update_loop():
            while True:
                try:
                    self._update_dashboard_data()
                    time.sleep(self.update_interval)
                except Exception as e:
                    logger.error(f"Dashboard update error: {e}")
                    time.sleep(10)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def _update_dashboard_data(self):
        """Update dashboard data"""
        try:
            # Update active signals
            if hasattr(self.bot, 'signals'):
                for signal in self.bot.signals[-10:]:  # Last 10 signals
                    symbol = signal.get('symbol')
                    if symbol:
                        self.active_signals[symbol] = signal
            
            # Update performance stats
            if hasattr(self.bot, 'performance_tracker'):
                self.performance_stats = self.bot.performance_tracker.get_performance_stats(30)
            
            self.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def _render_login_page(self):
        """Render login page with dynamic theme"""
        theme = Config.ACTIVE_COLOR_THEME
        colors = self._get_theme_colors(theme)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CryptoSniperXProBot - Admin Login</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Segoe UI, Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: {colors['background']};
                    color: {colors['text']};
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .login-container {{
                    background: {colors['card']};
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30 rgba(0,0,0,0.3);
                    width: 400px;
                    text-align: center;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 30px;
                    color: {colors['accent']};
                }}
                .form-group {{
                    margin-bottom: 20px;
                    text-align: left;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 500;
                }}
                input[type="text"], input[type="password"] {{
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #444;
                    border-radius: 8px;
                    background: {colors['background']};
                    color: {colors['text']};
                    font-size: 16px;
                    box-sizing: border-box;
                }}
                input[type="text"]:focus, input[type="password"]:focus {{
                    border-color: {colors['accent']};
                    outline: none;
                }}
                .login-btn {{
                    width: 100%;
                    padding: 15px;
                    background: {colors['accent']};
                    color: #000;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .login-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0px 15px rgba(0,255,153,0.3);
                }}
                .error {{
                    color: #ff6b6b;
                    margin-top: 10px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">🎛️ CryptoSniperXProBot</div>
                <form method="POST" action="/admin/login">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="login-btn">Login to Admin Panel</button>
                </form>
                <div style="margin-top:20px; font-size: 12; opacity: 0.7;">
                    Default: admin / admin123
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _get_theme_colors(self, theme: str) -> Dict[str, str]:
        """Get colors for theme"""
        if theme == 'light':
            return {
                'background': '#f5f5f5',
                'card': '#ffffff',
                'text': '#333333',
                'accent': '#0099ff'
            }
        elif theme == 'dark':
            return {
                'background': '#1a1a1a',
                'card': '#2d2d2d',
                'text': '#ffffff',
                'accent': '#0099ff'
            }
        elif theme == 'custom':
            return Config.CUSTOM_COLORS
        else:  # dynamic
            return {
                'background': '#181818',
                'card': '#23272e',
                'text': '#ffffff',
                'accent': '#0099ff'
            }
    
    def _render_dashboard(self):
        """Render main dashboard with all controls"""
        theme = Config.ACTIVE_COLOR_THEME
        colors = self._get_theme_colors(theme)
        
        # Get current data
        symbols = Config.DYNAMIC_SYMBOLS
        timeframes = Config.DYNAMIC_TIMEFRAMES
        active_session = Config.ACTIVE_SESSION
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CryptoSniperXProBot - Admin Dashboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Segoe UI, Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: {colors['background']};
                    color: {colors['text']};
                    min-height: 100vh;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom:2px solid {colors['accent']};
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    color: {colors['accent']};
                }}
                .status {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .status-indicator {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #00ff99;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                   0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: {colors['card']};
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15 rgba(0,0,0,0.2);
                }}
                .card h3 {{
                    margin-top: 0;
                    color: {colors['accent']};
                    border-bottom:2px solid {colors['accent']};
                    padding-bottom: 10px;
                }}
                .form-group {{
                    margin-bottom: 15px;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 500;
                }}
                input[type="text"], select {{
                    width: 100%;
                    padding: 10px;
                    border: 2px solid #444;
                    border-radius: 8px;
                    background: {colors['background']};
                    color: {colors['text']};
                    font-size: 14px;
                    box-sizing: border-box;
                }}
                .btn {{
                    padding: 10px 20px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                    margin-right: 10px;
                    margin-bottom: 10px;
                }}
                .btn-primary {{
                    background: {colors['accent']};
                    color: #000;
                }}
                .btn-danger {{
                    background: #ff6b6b;
                    color: white;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15 rgba(0,0,0,0.3);
                }}
                .list-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    background: {colors['background']};
                    margin-bottom: 5px;
                    border-radius: 5px;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }}
                .stat {{
                    text-align: center;
                    padding: 15px;
                    background: {colors['background']};
                    border-radius: 8px;
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: {colors['accent']};
                }}
                .stat-label {{
                    font-size: 12px;
                    opacity: 0.7;
                    margin-top: 5px;
                }}
                .color-picker {{
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                }}
                .color-input {{
                    width: 50px;
                    height: 40px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                .session-controls {{
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                }}
                .session-btn {{
                    padding: 8px 15px;
                    border:2px solid {colors['accent']};
                    background: transparent;
                    color: {colors['accent']};
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .session-btn.active {{
                    background: {colors['accent']};
                    color: #000;
                }}
                .session-btn:hover {{
                    background: {colors['accent']};
                    color: #000;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🎛️ CryptoSniperXProBot Admin</div>
                <div class="status">
                    <div class="status-indicator"></div>
                    <span>Bot Running</span>
                </div>
            </div>
            
            <div class="grid">              <!-- Symbol Management -->
                <div class="card">
                    <h3>📊 Symbol Management</h3>
                    <div class="form-group">
                        <label>Add New Symbol:</label>
                        <input type="text" id="newSymbol" placeholder="e.g., DOGE/USDT">
                        <button class="btn btn-primary" onclick="addSymbol()">Add Symbol</button>
                    </div>
                    <div class="form-group">
                        <label>Current Symbols ({len(symbols)}):</label>
                        <div id="symbolsList">
                            {self._render_symbols_list(symbols)}
                        </div>
                    </div>
                </div>
                
                <!-- Timeframe Management -->
                <div class="card">
                    <h3>⏰ Timeframe Management</h3>
                    <div class="form-group">
                        <label>Add New Timeframe:</label>
                        <input type="text" id="newTimeframe" placeholder="e.g., 30m">
                        <button class="btn btn-primary" onclick="addTimeframe()">Add Timeframe</button>
                    </div>
                    <div class="form-group">
                        <label>Current Timeframes ({len(timeframes)}):</label>
                        <div id="timeframesList">
                            {self._render_timeframes_list(timeframes)}
                        </div>
                    </div>
                </div>
                
                <!-- Session Control -->
                <div class="card">
                    <h3>🌍 Trading Session Control</h3>
                    <div class="session-controls">
                        <button class="session-btn {'active' if active_session == 'auto' else ''}" onclick="setSession('auto')">Auto</button>
                        <button class="session-btn {'active' if active_session == 'manual' else ''}" onclick="setSession('manual')">Manual</button>
                        <button class="session-btn {'active' if active_session == 'asian' else ''}" onclick="setSession('asian')">Asian</button>
                        <button class="session-btn {'active' if active_session == 'london' else ''}" onclick="setSession('london')">London</button>
                        <button class="session-btn {'active' if active_session == 'newyork' else ''}" onclick="setSession('newyork')">New York</button>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong>Current Session:</strong> {active_session.upper()}
                    </div>
                </div>
                
                <!-- Color Theme Control -->
                <div class="card">
                    <h3>🎨 Color Theme Control</h3>
                    <div class="form-group">
                        <label>Theme:</label>
                        <select id="themeSelect" onchange="setTheme(this.value)">
                            <option value="dynamic" {'selected' if theme == 'dynamic' else ''}>Dynamic</option>
                            <option value="light" {'selected' if theme == 'light' else ''}>Light</option>
                            <option value="dark" {'selected' if theme == 'dark' else ''}>Dark</option>
                            <option value="custom" {'selected' if theme == 'custom' else ''}>Custom</option>
                        </select>
                    </div>
                    <div id="customColors" style="display: {'block' if theme == 'custom' else 'none'}">
                        <label>Custom Colors:</label>
                        <div class="color-picker">
                            <input type="color" id="bgColor" class="color-input" value={Config.CUSTOM_COLORS.get('background', '#181818')} onchange="updateCustomColors()">
                            <input type="color" id="cardColor" class="color-input" value={Config.CUSTOM_COLORS.get('card', '#23272e')} onchange="updateCustomColors()">
                            <input type="color" id="textColor" class="color-input" value={Config.CUSTOM_COLORS.get('text', '#ffffff')} onchange="updateCustomColors()">
                            <input type="color" id="accentColor" class="color-input" value={Config.CUSTOM_COLORS.get('accent', '#0099ff')} onchange="updateCustomColors()">
                        </div>
                        <div style="font-size: 12px; margin-top: 5px;">
                            Background | Card | Text | Accent
                        </div>
                    </div>
                </div>
                
                <!-- Bot Statistics -->
                <div class="card">
                    <h3>📈 Bot Statistics</h3>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{len(symbols)}</div>
                            <div class="stat-label">Symbols</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(timeframes)}</div>
                            <div class="stat-label">Timeframes</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(self.active_signals)}</div>
                            <div class="stat-label">Active Signals</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(self.signal_history)}</div>
                            <div class="stat-label">Total Signals</div>
                        </div>
                    </div>
                </div>
                
                <!-- Active Signals -->
                <div class="card">
                    <h3>📊 Active Signals</h3>
                    <div id="activeSignals">
                        {self._render_active_signals()}
                    </div>
                </div>
            </div>
            
            <script>
                function addSymbol() {
                    const symbol = document.getElementById('newSymbol').value;
                    if (symbol) {
                        fetch('/api/add-symbol', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({symbol: symbol})
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                location.reload();
                            }
                        });
                    }
                }
                
                function removeSymbol(symbol) {
                    fetch('/api/remove-symbol', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol: symbol})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            location.reload();
                        }
                    });
                }
                
                function addTimeframe() {
                    const timeframe = document.getElementById('newTimeframe').value;
                    if (timeframe) {
                        fetch('/api/add-timeframe', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({timeframe: timeframe})
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                location.reload();
                            }
                        });
                    }
                }
                
                function removeTimeframe(timeframe) {
                    fetch('/api/remove-timeframe', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({timeframe: timeframe})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            location.reload();
                        }
                    });
                }
                
                function setSession(session) {
                    fetch('/api/set-session', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({session: session})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            location.reload();
                        }
                    });
                }
                
                function setTheme(theme) {
                    fetch('/api/set-color-theme', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({theme: theme})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            location.reload();
                        }
                    });
                }
                
                function updateCustomColors() {
                    const colors = {
                        background: document.getElementById('bgColor').value,
                        card: document.getElementById('cardColor').value,
                        text: document.getElementById('textColor').value,
                        accent: document.getElementById('accentColor').value
                    };
                    
                    fetch('/api/set-custom-colors', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({colors: colors})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            location.reload();
                        }
                    });
                }
                
                // Auto-refresh every 30 seconds
                setInterval(() => {
                    location.reload();
                }, 30000);
            </script>
        </body>
        </html>
        """
        return html
    
    def _render_symbols_list(self, symbols: List[str]) -> str:
        """Render symbols list HTML"""
        html = ""
        for symbol in symbols:
            html += f"""
            <div class="list-item">
                <span>{symbol}</span>
                <button class="btn btn-danger" onclick="removeSymbol('{symbol}')">Remove</button>
            </div>
            """
        return html
    
    def _render_timeframes_list(self, timeframes: List[str]) -> str:
        """Render timeframes list HTML"""
        html = ""
        for tf in timeframes:
            html += f"""
            <div class="list-item">
                <span>{tf}</span>
                <button class="btn btn-danger" onclick="removeTimeframe('{tf}')">Remove</button>
            </div>
            """
        return html
    
    def _render_active_signals(self) -> str:
        """Render active signals HTML"""
        if not self.active_signals:
            return "<p>No active signals</p>"
        html = ""
        for symbol, signal in self.active_signals.items():
            signal_type = signal.get('signal_type', 'Unknown')
            entry_price = signal.get('entry_price', 0)
            timestamp = signal.get('timestamp', 'Unknown')
            
            emoji = "🟢" if signal_type == "LONG" else "🔴"
            html += f"""
            <div class="list-item">
                <div>
                    <strong>{emoji} {symbol}</strong><br>
                    <small>{signal_type} @ ${entry_price:.6f}</small><br>
                    <small>{timestamp}</small>
                </div>
            </div>
            """
        return html
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            return {
                'bot_name': Config.BOT_NAME,
                'bot_version': Config.BOT_VERSION,
                'uptime': str(datetime.now() - self.bot.start_time),
                'symbols_monitored': len(Config.DYNAMIC_SYMBOLS),
                'timeframes_monitored': len(Config.DYNAMIC_TIMEFRAMES),
                'signals_generated': len(self.bot.signals) if hasattr(self.bot, 'signals') else 0,
                'active_signals': len(self.active_signals),
                'market_data_points': sum(len(data) for data in self.bot.market_data.values()) if hasattr(self.bot, 'market_data') else 0,
                'active_session': Config.ACTIVE_SESSION,
                'color_theme': Config.ACTIVE_COLOR_THEME,
                'last_update': self.last_update.isoformat(),
                'performance_stats': self.performance_stats
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}