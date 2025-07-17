from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.core.window import Window
import requests
import json
from datetime import datetime
import threading
import os

class CryptoSniperApp(App):
    def __init__(self):
        super().__init__()
        self.bot_running = False
        self.user_logged_in = False
        self.api_url = "http://localhost:5000"
        self.signals = []
        
    def build(self):
        if not self.user_logged_in:
            return self.build_login_screen()
        else:
            return self.build_main_screen()
    
    def build_login_screen(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='CryptoSniperXProBot',
            size_hint_y=None,
            height=60,
            font_size='24',
            bold=True
        )
        layout.add_widget(header)
        
        # Email login
        self.email_input = TextInput(
            hint_text='Email',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.email_input)
        
        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.password_input)
        
        # Login buttons
        email_login_btn = Button(
            text='Login with Email',
            size_hint_y=None,
            height=50,
            on_press=self.email_login
        )
        layout.add_widget(email_login_btn)
        
        google_login_btn = Button(
            text='Login with Google',
            size_hint_y=None,
            height=50,
            on_press=self.google_login
        )
        layout.add_widget(google_login_btn)
        
        # Demo login
        demo_btn = Button(
            text='Demo Login (Skip)',
            size_hint_y=None,
            height=50,
            on_press=self.demo_login
        )
        layout.add_widget(demo_btn)
        
        return layout
    
    def build_main_screen(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header with user info
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        header_layout.add_widget(Label(text='CryptoSniperXProBot', font_size='18', bold=True))
        logout_btn = Button(text='Logout', size_hint_x=0.3, on_press=self.logout)
        header_layout.add_widget(logout_btn)
        main_layout.add_widget(header_layout)
        
        # Tabbed interface
        tabs = TabbedPanel()
        
        # Dashboard Tab
        dashboard_tab = TabbedPanelItem(text='Dashboard')
        dashboard_layout = BoxLayout(orientation='vertical', padding=10)
        
        # Status section
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.status_label = Label(text='Status: Stopped', color=(1,0,0,1))
        self.start_stop_btn = Button(text='Start Bot', on_press=self.toggle_bot)
        status_layout.add_widget(self.status_label)
        status_layout.add_widget(self.start_stop_btn)
        dashboard_layout.add_widget(status_layout)
        
        # Stats section
        stats_layout = GridLayout(cols=2, size_hint_y=None, height=120)
        stats_layout.add_widget(Label(text='Signals Generated:'))
        self.signals_count = Label(text='0')
        stats_layout.add_widget(self.signals_count)
        stats_layout.add_widget(Label(text='Active Signals:'))
        self.active_signals = Label(text='0')
        stats_layout.add_widget(self.active_signals)
        stats_layout.add_widget(Label(text='Symbols Monitored:'))
        self.symbols_count = Label(text='0')
        stats_layout.add_widget(self.symbols_count)
        stats_layout.add_widget(Label(text='Uptime:'))
        self.uptime_label = Label(text='0h')
        stats_layout.add_widget(self.uptime_label)
        dashboard_layout.add_widget(stats_layout)
        
        # Quick actions
        actions_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
        actions_layout.add_widget(Label(text='Quick Actions:', bold=True))
        
        test_btn = Button(text='Send Test Signal', on_press=self.send_test_signal)
        actions_layout.add_widget(test_btn)
        
        refresh_btn = Button(text='Refresh Status', on_press=self.refresh_status)
        actions_layout.add_widget(refresh_btn)
        
        dashboard_layout.add_widget(actions_layout)
        dashboard_tab.add_widget(dashboard_layout)
        
        # Signals Tab
        signals_tab = TabbedPanelItem(text='Signals')
        signals_layout = BoxLayout(orientation='vertical')
        
        self.signals_scroll = ScrollView()
        self.signals_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.signals_grid.bind(minimum_height=self.signals_grid.setter('height'))
        self.signals_scroll.add_widget(self.signals_grid)
        signals_layout.add_widget(self.signals_scroll)
        
        signals_tab.add_widget(signals_layout)
        
        # Control Tab
        control_tab = TabbedPanelItem(text='Control')
        control_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Symbol management
        symbol_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        symbol_layout.add_widget(Label(text='Symbol:'))
        self.symbol_input = TextInput(text='BTC/USDT', multiline=False)
        symbol_layout.add_widget(self.symbol_input)
        add_symbol_btn = Button(text='Add', on_press=self.add_symbol)
        symbol_layout.add_widget(add_symbol_btn)
        control_layout.add_widget(symbol_layout)
        
        # Remove symbol
        remove_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        remove_layout.add_widget(Label(text='Remove:'))
        self.remove_input = TextInput(text='BTC/USDT', multiline=False)
        remove_layout.add_widget(self.remove_input)
        remove_btn = Button(text='Remove', on_press=self.remove_symbol)
        remove_layout.add_widget(remove_btn)
        control_layout.add_widget(remove_layout)
        
        # Bot controls
        control_layout.add_widget(Label(text='Bot Controls:', bold=True))
        
        scan_btn = Button(text='Toggle Scanning', on_press=self.toggle_scanning)
        control_layout.add_widget(scan_btn)
        
        emergency_btn = Button(text='Emergency Stop', on_press=self.emergency_stop)
        control_layout.add_widget(emergency_btn)
        
        control_tab.add_widget(control_layout)
        
        # Settings Tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Telegram settings
        telegram_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        telegram_layout.add_widget(Label(text='Telegram:'))
        self.telegram_switch = Switch(active=False)
        telegram_layout.add_widget(self.telegram_switch)
        settings_layout.add_widget(telegram_layout)
        
        # Auto scanning
        scan_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        scan_layout.add_widget(Label(text='Auto Scanning:'))
        self.scan_switch = Switch(active=True)
        scan_layout.add_widget(self.scan_switch)
        settings_layout.add_widget(scan_layout)
        
        # Theme settings
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        theme_layout.add_widget(Label(text='Dark Theme:'))
        self.theme_switch = Switch(active=True)
        theme_layout.add_widget(self.theme_switch)
        settings_layout.add_widget(theme_layout)
        
        settings_tab.add_widget(settings_layout)
        
        # Add tabs
        tabs.add_widget(dashboard_tab)
        tabs.add_widget(signals_tab)
        tabs.add_widget(control_tab)
        tabs.add_widget(settings_tab)
        
        main_layout.add_widget(tabs)
        
        # Start update loop
        Clock.schedule_interval(self.update_status, 5)
        
        return main_layout
    
    def email_login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        
        if email and password:
            # Simple validation
            if '@' in email and len(password) >= 6:
                self.user_logged_in = True
                self.current_user = email
                self.root.clear_widgets()
                self.root.add_widget(self.build_main_screen())
            else:
                self.show_message("Invalid email or password")
        else:
            self.show_message("Please enter email and password")
    
    def google_login(self, instance):
        # Simulate Google login
        self.user_logged_in = True
        self.current_user = "google_user@example.com"
        self.root.clear_widgets()
        self.root.add_widget(self.build_main_screen())
    
    def demo_login(self, instance):
        # Skip login for demo
        self.user_logged_in = True
        self.current_user = "demo_user"
        self.root.clear_widgets()
        self.root.add_widget(self.build_main_screen())
    
    def logout(self, instance):
        self.user_logged_in = False
        self.current_user = None
        self.root.clear_widgets()
        self.root.add_widget(self.build_login_screen())
    
    def toggle_bot(self, instance):
        if not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        try:
            response = requests.post(f"{self.api_url}/api/start", timeout=5)
            if response.status_code == 200:
                self.bot_running = True
                self.status_label.text = "Status: Running"
                self.status_label.color = (0, 1, 0, 1)
                self.start_stop_btn.text = 'Stop Bot'
                self.add_log("Bot started successfully")
            else:
                self.add_log("Failed to start bot")
        except Exception as e:
            self.add_log(f"Error starting bot: {e}")
    
    def stop_bot(self):
        try:
            response = requests.post(f"{self.api_url}/api/stop", timeout=5)
            if response.status_code == 200:
                self.bot_running = False
                self.status_label.text = "Status: Stopped"
                self.status_label.color = (1, 0, 0, 1)
                self.start_stop_btn.text = 'Start Bot'
                self.add_log("Bot stopped successfully")
            else:
                self.add_log("Failed to stop bot")
        except Exception as e:
            self.add_log(f"Error stopping bot: {e}")
    
    def send_test_signal(self, instance):
        try:
            response = requests.post(f"{self.api_url}/api/send-test-signal", timeout=5)
            if response.status_code == 200:
                self.add_log("Test signal sent successfully")
            else:
                self.add_log("Failed to send test signal")
        except Exception as e:
            self.add_log(f"Error sending test signal: {e}")
    
    def add_symbol(self, instance):
        symbol = self.symbol_input.text.upper()
        try:
            response = requests.post(
                f"{self.api_url}/api/add-symbol",
                json={'symbol': symbol},
                timeout=5
            )
            if response.status_code == 200:
                self.add_log(f"Added symbol: {symbol}")
            else:
                self.add_log(f"Failed to add symbol: {symbol}")
        except Exception as e:
            self.add_log(f"Error adding symbol: {e}")
    
    def remove_symbol(self, instance):
        symbol = self.remove_input.text.upper()
        try:
            response = requests.post(
                f"{self.api_url}/api/remove-symbol",
                json={'symbol': symbol},
                timeout=5
            )
            if response.status_code == 200:
                self.add_log(f"Removed symbol: {symbol}")
            else:
                self.add_log(f"Failed to remove symbol: {symbol}")
        except Exception as e:
            self.add_log(f"Error removing symbol: {e}")
    
    def toggle_scanning(self, instance):
        try:
            response = requests.post(f"{self.api_url}/api/toggle-scanning", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.add_log(f"Scanning {'enabled' if data.get('scanning') else 'disabled'}")
            else:
                self.add_log("Failed to toggle scanning")
        except Exception as e:
            self.add_log(f"Error toggling scanning: {e}")
    
    def emergency_stop(self, instance):
        try:
            response = requests.post(f"{self.api_url}/api/emergency-stop", timeout=5)
            if response.status_code == 200:
                self.add_log("Emergency stop executed")
                self.bot_running = False
                self.status_label.text = "Status: Emergency Stop"
                self.status_label.color = (1, 0, 0, 1)
            else:
                self.add_log("Emergency stop failed")
        except Exception as e:
            self.add_log(f"Error during emergency stop: {e}")
    
    def refresh_status(self, instance):
        self.update_status(0)
    
    def update_status(self, dt):
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                self.signals_count.text = str(status.get('signals_generated', 0))
                self.active_signals.text = str(status.get('active_signals', 0))
                self.symbols_count.text = str(status.get('symbols_monitored', 0))
                self.uptime_label.text = status.get('uptime', '0h')
                
                if status.get('status') == 'running':
                    self.bot_running = True
                    self.status_label.text = "Status: Running"
                    self.status_label.color = (0, 1, 0, 1)
                    self.start_stop_btn.text = 'Stop Bot'
                else:
                    self.bot_running = False
                    self.status_label.text = "Status: Stopped"
                    self.status_label.color = (1, 0, 0, 1)
                    self.start_stop_btn.text = 'Start Bot'
                    
        except Exception as e:
            self.status_label.text = 'Status: Error'
            self.status_label.color = (1,1,0)
    
    def add_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_label = Label(
            text=f"[{timestamp}] {message}",
            size_hint_y=None,
            height=30,
            text_size=(Window.width -20, None)
        )
        self.signals_grid.add_widget(log_label)
        
        if len(self.signals_grid.children) > 50:
            self.signals_grid.remove_widget(self.signals_grid.children[-1])
    
    def show_message(self, message):
        # Simple message display
        pass

if __name__ == '__main__':
    CryptoSniperApp().run()
