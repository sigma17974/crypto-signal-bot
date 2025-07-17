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
from kivy.utils import platform
import threading
import requests
import json
from datetime import datetime
import os

class CryptoSniperApp(App):
    def __init__(self):
        super().__init__()
        self.bot_running = False
        self.signals = []
        self.api_url = "http://localhost:5000"
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text='CryptoSniperXProBot Mobile',
            size_hint_y=None,
            height=50,
            font_size='20',
            bold=True
        )
        main_layout.add_widget(header)
        
        # Tabbed interface
        tabs = TabbedPanel()
        
        # Dashboard Tab
        dashboard_tab = TabbedPanelItem(text='Dashboard')
        dashboard_layout = BoxLayout(orientation='vertical', padding=10)
        
        # Status section
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.status_label = Label(text="Status: Stopped", color=(1,0, 1))
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
        stats_layout.add_widget(Label(text='Last Signal:'))
        self.last_signal = Label(text='None')
        stats_layout.add_widget(self.last_signal)
        dashboard_layout.add_widget(stats_layout)
        
        # Settings section
        settings_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        settings_layout.add_widget(Label(text='Settings:', bold=True))
        
        # Telegram settings
        telegram_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        telegram_layout.add_widget(Label(text='Telegram:'))
        self.telegram_switch = Switch(active=False)
        telegram_layout.add_widget(self.telegram_switch)
        settings_layout.add_widget(telegram_layout)
        
        # Scanning settings
        scan_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        scan_layout.add_widget(Label(text='Auto Scanning:'))
        self.scan_switch = Switch(active=True)
        scan_layout.add_widget(self.scan_switch)
        settings_layout.add_widget(scan_layout)
        
        dashboard_layout.add_widget(settings_layout)
        dashboard_tab.add_widget(dashboard_layout)
        
        # Signals Tab
        signals_tab = TabbedPanelItem(text='Signals')
        signals_layout = BoxLayout(orientation='vertical')
        
        # Signals list
        self.signals_scroll = ScrollView()
        self.signals_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.signals_grid.bind(minimum_height=self.signals_grid.setter('height'))
        self.signals_scroll.add_widget(self.signals_grid)
        signals_layout.add_widget(self.signals_scroll)
        
        signals_tab.add_widget(signals_layout)
        
        # Control Tab
        control_tab = TabbedPanelItem(text='Control')
        control_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Manual controls
        control_layout.add_widget(Label(text='Manual Controls:', bold=True))
        
        # Test signal button
        test_btn = Button(
            text='Send Test Signal',
            size_hint_y=None,
            height=50,
            on_press=self.send_test_signal
        )
        control_layout.add_widget(test_btn)
        
        # Add symbol
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
        
        control_tab.add_widget(control_layout)
        
        # Add tabs
        tabs.add_widget(dashboard_tab)
        tabs.add_widget(signals_tab)
        tabs.add_widget(control_tab)
        
        main_layout.add_widget(tabs)
        
        # Start update loop
        Clock.schedule_interval(self.update_status, 5)
        
        return main_layout
    
    def toggle_bot(self, instance):
        if not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        try:
            # Start bot via API
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
            # Stop bot via API
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
    
    def update_status(self, dt):
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                self.signals_count.text = str(status.get('signals_generated', 0))
                self.active_signals.text = str(status.get('active_signals', 0))
                
                # Update last signal
                if self.signals:
                    last_signal = self.signals[-1]
                    self.last_signal.text = f"{last_signal['symbol']} {last_signal['signal_type']}"
                
                # Update bot status
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
        
        # Keep only last 50 logs
        if len(self.signals_grid.children) > 50:
            self.signals_grid.remove_widget(self.signals_grid.children[-1])

if __name__ == '__main__':
    CryptoSniperApp().run()