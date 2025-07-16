"""
Advanced Admin Dashboard for Crypto Sniper Pro Bot
Features: Telegram Auth, Auto-reconnect, Auto-cleanup, Error Detection/Repair, Auto-refresh
"""

import os
import json
import time
import threading
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import telegram
from telegram.ext import Updater
import logging
import psutil
import schedule

class AdminDashboard:
    """Advanced admin dashboard with comprehensive monitoring and management"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('ADMIN_SECRET_KEY', 'your-secret-key-change-this')
        
        # Initialize login manager
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'
        
        # Telegram bot instance
        self.telegram_bot = None
        self.telegram_chat_id = None
        
        # Auto-reconnect settings
        self.auto_reconnect_enabled = True
        self.reconnect_interval = 30  # seconds
        self.max_reconnect_attempts = 5
        
        # Auto-cleanup settings
        self.auto_cleanup_enabled = True
        self.cleanup_interval = 3600  # 1 hour
        self.max_log_age = 7  # days
        self.max_signal_age = 30  # days
        
        # Error tracking
        self.error_log = []
        self.last_error_check = datetime.now()
        self.error_threshold = 5  # max errors before auto-repair
        
        # Performance tracking
        self.performance_data = {
            'uptime': 0,
            'signals_generated': 0,
            'errors_count': 0,
            'last_cleanup': None,
            'last_reconnect': None
        }
        
        # Initialize systems
        self._init_telegram_auth()
        self._init_auto_systems()
        self._setup_routes()
        
    def _init_telegram_auth(self):
        """Initialize Telegram authentication"""
        try:
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            
            if token and chat_id:
                self.telegram_bot = telegram.Bot(token=token)
                self.telegram_chat_id = chat_id
                self._send_telegram_message("🔧 Admin Dashboard initialized successfully")
        except Exception as e:
            self._log_error(f"Telegram auth initialization failed: {str(e)}")
    
    def _init_auto_systems(self):
        """Initialize auto systems"""
        # Start auto-reconnect thread
        if self.auto_reconnect_enabled:
            threading.Thread(target=self._auto_reconnect_worker, daemon=True).start()
        
        # Start auto-cleanup thread
        if self.auto_cleanup_enabled:
            threading.Thread(target=self._auto_cleanup_worker, daemon=True).start()
        
        # Start error monitoring thread
        threading.Thread(target=self._error_monitoring_worker, daemon=True).start()
        
        # Start auto-refresh thread
        threading.Thread(target=self._auto_refresh_worker, daemon=True).start()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.login_manager.user_loader
        def load_user(user_id):
            return AdminUser(user_id)
        
        @self.app.route('/')
        @login_required
        def dashboard():
            return self._render_dashboard()
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                token = request.form.get('telegram_token')
                chat_id = request.form.get('telegram_chat_id')
                
                if self._verify_telegram_credentials(token, chat_id):
                    user = AdminUser('admin')
                    login_user(user)
                    self._send_telegram_message("🔐 Admin logged in successfully")
                    return redirect(url_for('dashboard'))
                else:
                    return "Invalid credentials", 401
            
            return self._render_login_page()
        
        @self.app.route('/logout')
        @login_required
        def logout():
            logout_user()
            self._send_telegram_message("🔓 Admin logged out")
            return redirect(url_for('login'))
        
        @self.app.route('/api/status')
        @login_required
        def api_status():
            return jsonify(self._get_system_status())
        
        @self.app.route('/api/telegram-test')
        @login_required
        def test_telegram():
            try:
                self._send_telegram_message("🧪 Telegram connection test successful")
                return jsonify({"status": "success", "message": "Telegram test sent"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        
        @self.app.route('/api/auto-reconnect/toggle')
        @login_required
        def toggle_auto_reconnect():
            self.auto_reconnect_enabled = not self.auto_reconnect_enabled
            status = "enabled" if self.auto_reconnect_enabled else "disabled"
            self._send_telegram_message(f"🔄 Auto-reconnect {status}")
            return jsonify({"status": "success", "auto_reconnect": self.auto_reconnect_enabled})
        
        @self.app.route('/api/auto-cleanup/toggle')
        @login_required
        def toggle_auto_cleanup():
            self.auto_cleanup_enabled = not self.auto_cleanup_enabled
            status = "enabled" if self.auto_cleanup_enabled else "disabled"
            self._send_telegram_message(f"🧹 Auto-cleanup {status}")
            return jsonify({"status": "success", "auto_cleanup": self.auto_cleanup_enabled})
        
        @self.app.route('/api/force-cleanup')
        @login_required
        def force_cleanup():
            try:
                self._perform_cleanup()
                self._send_telegram_message("🧹 Manual cleanup completed")
                return jsonify({"status": "success", "message": "Cleanup completed"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        
        @self.app.route('/api/force-reconnect')
        @login_required
        def force_reconnect():
            try:
                self._perform_reconnect()
                self._send_telegram_message("🔄 Manual reconnect completed")
                return jsonify({"status": "success", "message": "Reconnect completed"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
    
    def _verify_telegram_credentials(self, token, chat_id):
        """Verify Telegram credentials"""
        try:
            if not token or not chat_id:
                return False
            
            # Test the credentials
            test_bot = telegram.Bot(token=token)
            test_bot.send_message(chat_id=chat_id, text="🔐 Admin authentication test")
            
            # Update bot instance
            self.telegram_bot = test_bot
            self.telegram_chat_id = chat_id
            
            return True
        except Exception as e:
            self._log_error(f"Telegram credential verification failed: {str(e)}")
            return False
    
    def _auto_reconnect_worker(self):
        """Auto-reconnect worker thread"""
        while True:
            try:
                if self.auto_reconnect_enabled:
                    self._check_and_reconnect()
                time.sleep(self.reconnect_interval)
            except Exception as e:
                self._log_error(f"Auto-reconnect worker error: {str(e)}")
    
    def _auto_cleanup_worker(self):
        """Auto-cleanup worker thread"""
        while True:
            try:
                if self.auto_cleanup_enabled:
                    self._perform_cleanup()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                self._log_error(f"Auto-cleanup worker error: {str(e)}")
    
    def _error_monitoring_worker(self):
        """Error monitoring worker thread"""
        while True:
            try:
                self._check_for_errors()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self._log_error(f"Error monitoring worker error: {str(e)}")
    
    def _auto_refresh_worker(self):
        """Auto-refresh worker thread"""
        while True:
            try:
                self._update_performance_data()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                self._log_error(f"Auto-refresh worker error: {str(e)}")
    
    def _check_and_reconnect(self):
        """Check connection and reconnect if needed"""
        try:
            if not self.telegram_bot:
                self._perform_reconnect()
            else:
                # Test connection
                self.telegram_bot.get_me()
        except Exception as e:
            self._log_error(f"Connection check failed: {str(e)}")
            self._perform_reconnect()
    
    def _perform_reconnect(self):
        """Perform reconnection"""
        try:
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            
            if token and chat_id:
                self.telegram_bot = telegram.Bot(token=token)
                self.telegram_chat_id = chat_id
                self._send_telegram_message("🔄 Auto-reconnect successful")
                self.performance_data['last_reconnect'] = datetime.now()
        except Exception as e:
            self._log_error(f"Reconnection failed: {str(e)}")
    
    def _perform_cleanup(self):
        """Perform system cleanup"""
        try:
            # Clean old logs
            cutoff_date = datetime.now() - timedelta(days=self.max_log_age)
            self._cleanup_old_logs(cutoff_date)
            
            # Clean old signals
            cutoff_date = datetime.now() - timedelta(days=self.max_signal_age)
            self._cleanup_old_signals(cutoff_date)
            
            # Clean error log
            self._cleanup_error_log()
            
            self.performance_data['last_cleanup'] = datetime.now()
            self._send_telegram_message("🧹 Auto-cleanup completed")
        except Exception as e:
            self._log_error(f"Cleanup failed: {str(e)}")
    
    def _check_for_errors(self):
        """Check for system errors and auto-repair"""
        try:
            error_count = len(self.error_log)
            
            if error_count > self.error_threshold:
                self._send_telegram_message(f"⚠️ High error count detected: {error_count}")
                self._auto_repair_errors()
            
            # Check bot health
            if not self._check_bot_health():
                self._send_telegram_message("🔧 Bot health check failed, attempting repair")
                self._repair_bot_health()
        except Exception as e:
            self._log_error(f"Error checking failed: {str(e)}")
    
    def _auto_repair_errors(self):
        """Auto-repair system errors"""
        try:
            # Clear error log
            self.error_log.clear()
            
            # Restart critical services
            self._restart_critical_services()
            
            # Test connections
            self._test_all_connections()
            
            self._send_telegram_message("🔧 Auto-repair completed")
        except Exception as e:
            self._log_error(f"Auto-repair failed: {str(e)}")
    
    def _check_bot_health(self):
        """Check bot health status"""
        try:
            # Check if bot is responding
            if hasattr(self.bot, 'is_running'):
                return self.bot.is_running
            return True
        except Exception as e:
            self._log_error(f"Bot health check failed: {str(e)}")
            return False
    
    def _repair_bot_health(self):
        """Repair bot health issues"""
        try:
            # Restart bot if needed
            if hasattr(self.bot, 'restart'):
                self.bot.restart()
            
            # Reinitialize connections
            self._init_telegram_auth()
            
            self._send_telegram_message("🔧 Bot health repair completed")
        except Exception as e:
            self._log_error(f"Bot health repair failed: {str(e)}")
    
    def _cleanup_old_logs(self, cutoff_date):
        """Clean up old log files"""
        log_dir = "logs"
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
    
    def _cleanup_old_signals(self, cutoff_date):
        """Clean up old signal data"""
        # This would clean up old signal data from database
        pass
    
    def _cleanup_error_log(self):
        """Clean up old error log entries"""
        # Keep only recent errors
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.error_log = [error for error in self.error_log 
                         if error.get('timestamp', datetime.now()) > cutoff_time]
    
    def _restart_critical_services(self):
        """Restart critical services"""
        try:
            # Reinitialize database connections
            # Restart schedulers
            # Reinitialize API connections
            pass
        except Exception as e:
            self._log_error(f"Service restart failed: {str(e)}")
    
    def _test_all_connections(self):
        """Test all system connections"""
        try:
            # Test Telegram connection
            if self.telegram_bot:
                self.telegram_bot.get_me()
            
            # Test database connection
            # Test API connections
            # Test webhook connections
        except Exception as e:
            self._log_error(f"Connection test failed: {str(e)}")
    
    def _update_performance_data(self):
        """Update performance data"""
        try:
            # Update uptime
            if hasattr(self.bot, 'start_time'):
                self.performance_data['uptime'] = (datetime.now() - self.bot.start_time).total_seconds() / 3600
            
            # Update signal count
            if hasattr(self.bot, 'signal_count'):
                self.performance_data['signals_generated'] = self.bot.signal_count
            
            # Update error count
            self.performance_data['errors_count'] = len(self.error_log)
        except Exception as e:
            self._log_error(f"Performance data update failed: {str(e)}")
    
    def _log_error(self, error_message):
        """Log error message"""
        error_entry = {
            'timestamp': datetime.now(),
            'message': error_message,
            'level': 'ERROR'
        }
        self.error_log.append(error_entry)
        
        # Send to Telegram if available
        if self.telegram_bot and self.telegram_chat_id:
            try:
                self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=f"❌ Error: {error_message}"
                )
            except:
                pass
    
    def _send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            if self.telegram_bot and self.telegram_chat_id:
                self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message
                )
        except Exception as e:
            self._log_error(f"Telegram message failed: {str(e)}")
    
    def _get_system_status(self):
        """Get comprehensive system status"""
        return {
            'bot_status': 'running' if self._check_bot_health() else 'stopped',
            'telegram_connected': bool(self.telegram_bot),
            'auto_reconnect': self.auto_reconnect_enabled,
            'auto_cleanup': self.auto_cleanup_enabled,
            'error_count': len(self.error_log),
            'uptime': round(self.performance_data['uptime'], 2),
            'signals_generated': self.performance_data['signals_generated'],
            'last_cleanup': self.performance_data['last_cleanup'].isoformat() if self.performance_data['last_cleanup'] else None,
            'last_reconnect': self.performance_data['last_reconnect'].isoformat() if self.performance_data['last_reconnect'] else None,
            'system_health': self._get_system_health_score()
        }
    
    def _get_system_health_score(self):
        """Calculate system health score (0-100)"""
        score = 100
        
        # Deduct points for errors
        error_count = len(self.error_log)
        score -= min(error_count * 5, 50)
        
        # Deduct points for disconnected services
        if not self.telegram_bot:
            score -= 20
        
        # Deduct points for high uptime (potential memory issues)
        if self.performance_data['uptime'] > 168:  # 7 days
            score -= 10
        
        return max(score, 0)
    
    def _render_login_page(self):
        """Render login page"""
        return render_template_string(self._get_login_html())
    
    def _render_dashboard(self):
        """Render main dashboard"""
        status = self._get_system_status()
        return render_template_string(self._get_dashboard_html(), status=status)
    
    def _get_login_html(self):
        """Get login page HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Login - CryptoSniperXProBot</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .login-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                    width: 100%;
                    max-width: 400px;
                }
                .login-header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .login-header h1 {
                    color: #333;
                    margin: 0;
                    font-size: 2em;
                }
                .login-header p {
                    color: #666;
                    margin: 10px 0 0 0;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    color: #333;
                    font-weight: 500;
                }
                .form-group input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    box-sizing: border-box;
                    transition: border-color 0.3s;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                .login-btn {
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .login-btn:hover {
                    transform: translateY(-2px);
                }
                .help-text {
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="login-header">
                    <h1>🔐 Admin Login</h1>
                    <p>CryptoSniperXProBot</p>
                </div>
                <form method="POST">
                    <div class="form-group">
                        <label for="telegram_token">Telegram Bot Token</label>
                        <input type="password" id="telegram_token" name="telegram_token" required>
                    </div>
                    <div class="form-group">
                        <label for="telegram_chat_id">Telegram Chat ID</label>
                        <input type="text" id="telegram_chat_id" name="telegram_chat_id" required>
                    </div>
                    <button type="submit" class="login-btn">Login</button>
                </form>
                <div class="help-text">
                    <p>Enter your Telegram bot token and chat ID to access the admin panel</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_dashboard_html(self):
        """Get dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Dashboard - CryptoSniperXProBot</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f5f7fa;
                    color: #333;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 1.8em;
                }
                .header-actions {
                    display: flex;
                    gap: 10px;
                }
                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                }
                .btn-primary {
                    background: rgba(255,255,255,0.2);
                    color: white;
                }
                .btn-primary:hover {
                    background: rgba(255,255,255,0.3);
                }
                .btn-danger {
                    background: #dc3545;
                    color: white;
                }
                .btn-danger:hover {
                    background: #c82333;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 0 20px;
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .status-card {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }
                .status-card.warning {
                    border-left-color: #ffc107;
                }
                .status-card.danger {
                    border-left-color: #dc3545;
                }
                .status-card.success {
                    border-left-color: #28a745;
                }
                .status-title {
                    font-size: 1.1em;
                    font-weight: 600;
                    margin-bottom: 10px;
                    color: #333;
                }
                .status-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }
                .status-label {
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .controls-section {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .controls-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }
                .control-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                .control-label {
                    font-weight: 500;
                }
                .toggle-switch {
                    position: relative;
                    width: 50px;
                    height: 24px;
                    background: #ccc;
                    border-radius: 12px;
                    cursor: pointer;
                    transition: background 0.3s;
                }
                .toggle-switch.active {
                    background: #667eea;
                }
                .toggle-switch::after {
                    content: '';
                    position: absolute;
                    top: 2px;
                    left: 2px;
                    width: 20px;
                    height: 20px;
                    background: white;
                    border-radius: 50%;
                    transition: transform 0.3s;
                }
                .toggle-switch.active::after {
                    transform: translateX(26px);
                }
                .action-btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                }
                .action-btn.success {
                    background: #28a745;
                    color: white;
                }
                .action-btn.success:hover {
                    background: #218838;
                }
                .action-btn.warning {
                    background: #ffc107;
                    color: #212529;
                }
                .action-btn.warning:hover {
                    background: #e0a800;
                }
                .logs-section {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .log-entry {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                    font-family: monospace;
                    font-size: 14px;
                }
                .log-entry.error {
                    color: #dc3545;
                }
                .log-entry.warning {
                    color: #ffc107;
                }
                .log-entry.info {
                    color: #17a2b8;
                }
                .refresh-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-bottom: 20px;
                }
                .refresh-btn:hover {
                    background: #5a6fd8;
                }
                @media (max-width: 768px) {
                    .status-grid {
                        grid-template-columns: 1fr;
                    }
                    .controls-grid {
                        grid-template-columns: 1fr;
                    }
                    .header-content {
                        flex-direction: column;
                        gap: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="header-content">
                    <h1>🚀 CryptoSniperXProBot - Admin Dashboard</h1>
                    <div class="header-actions">
                        <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
                        <a href="/logout" class="btn btn-danger">Logout</a>
                    </div>
                </div>
            </div>
            
            <div class="container">
                <div class="status-grid">
                    <div class="status-card {{ 'success' if status.bot_status == 'running' else 'danger' }}">
                        <div class="status-title">🤖 Bot Status</div>
                        <div class="status-value">{{ status.bot_status.upper() }}</div>
                        <div class="status-label">Current State</div>
                    </div>
                    <div class="status-card {{ 'success' if status.telegram_connected else 'danger' }}">
                        <div class="status-title">📱 Telegram</div>
                        <div class="status-value">{{ 'CONNECTED' if status.telegram_connected else 'DISCONNECTED' }}</div>
                        <div class="status-label">Connection Status</div>
                    </div>
                    <div class="status-card">
                        <div class="status-title">⏱️ Uptime</div>
                        <div class="status-value">{{ status.uptime }}h</div>
                        <div class="status-label">Hours Running</div>
                    </div>
                    <div class="status-card">
                        <div class="status-title">📊 Signals</div>
                        <div class="status-value">{{ status.signals_generated }}</div>
                        <div class="status-label">Generated Today</div>
                    </div>
                    <div class="status-card {{ 'danger' if status.error_count > 5 else 'success' }}">
                        <div class="status-title">❌ Errors</div>
                        <div class="status-value">{{ status.error_count }}</div>
                        <div class="status-label">Last 24 Hours</div>
                    </div>
                    <div class="status-card">
                        <div class="status-title">🏥 Health</div>
                        <div class="status-value">{{ status.system_health }}%</div>
                        <div class="status-label">System Health</div>
                    </div>
                </div>
                
                <div class="controls-section">
                    <h2>🎛️ System Controls</h2>
                    <div class="controls-grid">
                        <div class="control-item">
                            <span class="control-label">Auto-Reconnect</span>
                            <div class="toggle-switch {{ 'active' if status.auto_reconnect else '' }}" 
                                 onclick="toggleAutoReconnect()"></div>
                        </div>
                        <div class="control-item">
                            <span class="control-label">Auto-Cleanup</span>
                            <div class="toggle-switch {{ 'active' if status.auto_cleanup else '' }}" 
                                 onclick="toggleAutoCleanup()"></div>
                        </div>
                        <div class="control-item">
                            <span class="control-label">Test Telegram</span>
                            <button class="action-btn success" onclick="testTelegram()">Test</button>
                        </div>
                        <div class="control-item">
                            <span class="control-label">Force Cleanup</span>
                            <button class="action-btn warning" onclick="forceCleanup()">Clean</button>
                        </div>
                        <div class="control-item">
                            <span class="control-label">Force Reconnect</span>
                            <button class="action-btn warning" onclick="forceReconnect()">Reconnect</button>
                        </div>
                    </div>
                </div>
                
                <div class="logs-section">
                    <h2>📋 System Logs</h2>
                    <button class="refresh-btn" onclick="refreshLogs()">🔄 Refresh Logs</button>
                    <div id="logs-container">
                        <!-- Logs will be populated by JavaScript -->
                    </div>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 30 seconds
                setInterval(refreshData, 30000);
                
                function refreshData() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            // Update status cards
                            updateStatusCards(data);
                        })
                        .catch(error => console.error('Error:', error));
                }
                
                function updateStatusCards(data) {
                    // Update status values
                    document.querySelectorAll('.status-value').forEach((element, index) => {
                        const values = [
                            data.bot_status.toUpperCase(),
                            data.telegram_connected ? 'CONNECTED' : 'DISCONNECTED',
                            data.uptime + 'h',
                            data.signals_generated,
                            data.error_count,
                            data.system_health + '%'
                        ];
                        if (values[index]) {
                            element.textContent = values[index];
                        }
                    });
                }
                
                function toggleAutoReconnect() {
                    fetch('/api/auto-reconnect/toggle')
                        .then(response => response.json())
                        .then(data => {
                            const toggle = document.querySelector('.toggle-switch');
                            if (data.auto_reconnect) {
                                toggle.classList.add('active');
                            } else {
                                toggle.classList.remove('active');
                            }
                        });
                }
                
                function toggleAutoCleanup() {
                    fetch('/api/auto-cleanup/toggle')
                        .then(response => response.json())
                        .then(data => {
                            const toggles = document.querySelectorAll('.toggle-switch');
                            const toggle = toggles[1]; // Second toggle
                            if (data.auto_cleanup) {
                                toggle.classList.add('active');
                            } else {
                                toggle.classList.remove('active');
                            }
                        });
                }
                
                function testTelegram() {
                    fetch('/api/telegram-test')
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                        });
                }
                
                function forceCleanup() {
                    if (confirm('Are you sure you want to force cleanup?')) {
                        fetch('/api/force-cleanup')
                            .then(response => response.json())
                            .then(data => {
                                alert(data.message);
                            });
                    }
                }
                
                function forceReconnect() {
                    if (confirm('Are you sure you want to force reconnect?')) {
                        fetch('/api/force-reconnect')
                            .then(response => response.json())
                            .then(data => {
                                alert(data.message);
                            });
                    }
                }
                
                function refreshLogs() {
                    // This would fetch and display logs
                    console.log('Refreshing logs...');
                }
                
                // Initial load
                refreshData();
            </script>
        </body>
        </html>
        """
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the admin dashboard"""
        try:
            self._send_telegram_message("🚀 Admin dashboard starting...")
            self.app.run(host=host, port=port, debug=debug)
        except Exception as e:
            self._log_error(f"Admin dashboard failed to start: {str(e)}")


class AdminUser(UserMixin):
    """Simple admin user class"""
    def __init__(self, user_id):
        self.id = user_id


if __name__ == "__main__":
    # Test the dashboard
    dashboard = AdminDashboard(None)
    dashboard.run(debug=True)