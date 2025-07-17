#!/usr/bin/env python3
CryptoSniperXProBot Deployment Script
Comprehensive deployment with admin dashboard display
"""

import os
import sys
import time
import json
import subprocess
import threading
import requests
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

class BotDeployer:
    """Comprehensive bot deployment with monitoring"""
    def __init__(self):
        self.bot_process = None
        self.admin_dashboard_url = "http://localhost:5000/admin"
        self.api_status_url = "http://localhost:5000/api/status"
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Deployment message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        self.log("Checking dependencies...")
        
        required_packages = [
            'flask', 'apscheduler', 'python-telegram-bot', 'requests',
            'python-dotenv', 'matplotlib', 'pandas', 'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
            self.log("Installing missing packages...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                self.log("Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                self.log(f"Failed to install dependencies: {e}", "ERROR")
                return False
        else:
            self.log("All dependencies are installed")
        
        return True 
    def validate_config(self):
        """Bot configuration"""
        self.log("Validating configuration...")
        
        errors = Config.validate_config()
        if errors:
            self.log("Configuration errors found:", "ERROR")
            for error in errors:
                self.log(f"  - {error}", "ERROR")
            return False
        
        self.log("Configuration is valid")
        return True   
    def create_directories(self):
        """Essary directories"""
        self.log("Creating directories...")
        
        directories = [
            'logs',
            'charts',
            'data',
            'backups'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            self.log(f"  Created {directory}/")
    
    def start_bot(self):
        """Bot in background"""
        self.log("Starting CryptoSniperXProBot...")
        
        try:
            # Start bot in background
            self.bot_process = subprocess.Popen([
                sys.executable, 'crypto_sniper_bot.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for startup
            time.sleep(5)
            
            if self.bot_process.poll() is None:
                self.log("Bot started successfully")
                return True
            else:
                stdout, stderr = self.bot_process.communicate()
                self.log(f"Bot failed to start: {stderr.decode()}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Failed to start bot: {e}", "ERROR")
            return False
    
    def wait_for_bot_ready(self, timeout: int = 60):
        """Wait for bot to be ready"""
        self.log("Waiting for bot to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.api_status_url, timeout=5)
                if response.status_code == 200:
                    self.log("Bot is ready and responding")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        self.log("Bot did not become ready in time", "ERROR")
        return False  
    def display_admin_dashboard_info(self):
        """Display admin dashboard information"""
        self.log("Admin Dashboard Information")
        self.log("=" * 50)
        
        dashboard_info = f"""
dmin Dashboard URL: {self.admin_dashboard_url}
Login Credentials:
   Username: admin
   Password: admin123

Available Features:
   • Dynamic Symbol Management
   • Timeframe Configuration
   • Trading Session Control
   • Color Theme Customization
   • Real-time Signal Monitoring
   • Performance Statistics
   • Arbitrage Detection
   • Chart Generation

Bot Status:
   • Name: {Config.BOT_NAME}
   • Version: {Config.BOT_VERSION}
   • Symbols: {len(Config.DYNAMIC_SYMBOLS)}
   • Timeframes: {len(Config.DYNAMIC_TIMEFRAMES)}
   • Active Session: {Config.ACTIVE_SESSION}
   • Color Theme: {Config.ACTIVE_COLOR_THEME}

Telegram Integration:
   • Bot Token: {'✅ Set' if Config.TELEGRAM_BOT_TOKEN else '❌ Not Set'}
   • Chat ID: {'✅ Set' if Config.TELEGRAM_CHAT_ID else '❌ Not Set'}

API Endpoints:
   • Status: http://localhost:5000/status
   • Add Symbol: POST /api/add-symbol
   • Remove Symbol: POST /api/remove-symbol
   • Add Timeframe: POST /api/add-timeframe
   • Remove Timeframe: POST /api/remove-timeframe
   • Set Session: POST /api/set-session
   • Set Theme: POST /api/set-color-theme
   • Test Signal: POST /api/send-test-signal
   • Toggle Scanning: POST /api/toggle-scanning

Monitoring:
   • Logs: bot.log
   • Performance: performance.db
   • Charts: charts/
   • Backups: backups/

Management Commands:
   • View logs: tail -f bot.log
   • Check status: curl http://localhost:5000/status
   • Send test signal: curl -X POST http://localhost:5000/api/send-test-signal
   • Stop bot: Ctrl+C or kill process
       
        print(dashboard_info)
        self.log("=" * 50)
    
    def send_test_notifications(self):
        """Test notifications"""
        self.log("Sending test notifications...")
        
        try:
            # Test API status
            response = requests.get(self.api_status_url, timeout=10)
            if response.status_code == 200:
                self.log("API status endpoint working")
            else:
                self.log("API status endpoint failed", "ERROR")
            
            # Test signal endpoint
            response = requests.post(
                "http://localhost:5000/api/send-test-signal",
                timeout=10
            )
            if response.status_code == 200:
                self.log("Test signal sent successfully")
            else:
                self.log("Test signal failed", "ERROR")
                
        except Exception as e:
            self.log(f"Test notifications failed: {e}", "ERROR")
    
    def monitor_bot(self, duration: int = 300):
        """Monitor bot for specified duration"""
        self.log(f"Monitoring bot for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                response = requests.get(self.api_status_url, timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    self.log(f"Bot running - Signals: {status.get('signals_generated', 0)}")
                else:
                    self.log("Bot not responding", "WARNING")
            except Exception as e:
                self.log(f"Monitoring error: {e}", "ERROR")
            
            time.sleep(30)  # Check every 30 seconds
    
    def cleanup(self):
        """Clean up on exit"""
        self.log("Cleaning up...")
        
        if self.bot_process:
            self.log("Stopping bot...")
            self.bot_process.terminate()
            try:
                self.bot_process.wait(timeout=10)
                self.log("Bot stopped gracefully")
            except subprocess.TimeoutExpired:
                self.log("Force killing bot...", "WARNING")
                self.bot_process.kill()
    
    def deploy(self):
        """Deployment process"""
        self.log("Starting CryptoSniperXProBot deployment...")
        self.log("=" * 60)
        
        try:
            # Step 1: Check dependencies
            if not self.check_dependencies():
                return False
            
            # Step 2: Validate configuration
            if not self.validate_config():
                return False
            
            # Step 3: Create directories
            self.create_directories()
            
            # Step 4: Start bot
            if not self.start_bot():
                return False
            
            # Step 5: Wait for bot to be ready
            if not self.wait_for_bot_ready():
                return False
            
            # Step 6: Display admin dashboard info
            self.display_admin_dashboard_info()
            
            # Step 7: Send test notifications
            self.send_test_notifications()
            
            # Step 8: Monitor bot
            self.log("Bot deployment completed successfully!")
            self.log("Check your Telegram for startup notifications")
            self.log("Access admin dashboard at: http://localhost:5000/admin")
            
            # Keep monitoring
            try:
                self.monitor_bot()
            except KeyboardInterrupt:
                self.log("Monitoring stopped by user")
            
        except KeyboardInterrupt:
            self.log("Deployment interrupted by user")
        except Exception as e:
            self.log(f"Deployment failed: {e}", "ERROR")
            return False
        finally:
            self.cleanup()
        
        return True
    
    def save_deployment_log(self):
        """Save deployment log to file"""
        log_file = f"deployment_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"
        with open(log_file, 'w') as f:
            f.write("CryptoSniperXProBot Deployment Log\n")
            f.write("=" * 50 + "\n")
            f.write(f"Deployment Time: {datetime.now()}\n")
            f.write(f"Bot Version: {Config.BOT_VERSION}\n")
            f.write("=" * 50 + "\n\n")
            
            for log_entry in self.deployment_log:
                f.write(log_entry + "\n")
        
        self.log(f"Deployment log saved to: {log_file}")


def main():
    """Deployment function"""
    print("CryptoSniperXProBot Deployment")
    print("=" * 60)
    
    deployer = BotDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            print("\nDeployment completed successfully!")
            print("Access admin dashboard: http://localhost:5000/admin")
            print("Check Telegram for notifications")
        else:
            print("\nDeployment failed!")
            print("Check deployment logs for details")
    except KeyboardInterrupt:
        print("\nDeployment interrupted")
    finally:
        deployer.save_deployment_log()


if __name__ == "__main__":
    main()