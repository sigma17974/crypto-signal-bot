#!/bin/bash

echo "Building CryptoSniperXProBot APK..."

# Install buildozer
pip install buildozer

# Create mobile app file
cat > mobile_app.py << 'EOF'
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import requests
import json
from datetime import datetime

class CryptoSniperApp(App):
    def __init__(self):
        super().__init__()
        self.bot_running = False
        self.api_url = "http://localhost:5000"
        
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        header = Label(
            text='CryptoSniperXProBot Mobile',
            size_hint_y=None,
            height=50,
            font_size='20',
            bold=True
        )
        main_layout.add_widget(header)
        
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.status_label = Label(text='Status: Stopped', color=(1,0,0,1))
        self.start_stop_btn = Button(text='Start Bot', on_press=self.toggle_bot)
        status_layout.add_widget(self.status_label)
        status_layout.add_widget(self.start_stop_btn)
        main_layout.add_widget(status_layout)
        
        test_btn = Button(
            text='Send Test Signal',
            size_hint_y=None,
            height=50,
            on_press=self.send_test_signal
        )
        main_layout.add_widget(test_btn)
        
        refresh_btn = Button(
            text='Refresh Status',
            size_hint_y=None,
            height=50,
            on_press=self.refresh_status
        )
        main_layout.add_widget(refresh_btn)
        
        Clock.schedule_interval(self.update_status, 5)
        
        return main_layout
    
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
            else:
                pass
        except Exception as e:
            pass
    
    def stop_bot(self):
        try:
            response = requests.post(f"{self.api_url}/api/stop", timeout=5)
            if response.status_code == 200:
                self.bot_running = False
                self.status_label.text = "Status: Stopped"
                self.status_label.color = (1, 0, 0, 1)
                self.start_stop_btn.text = 'Start Bot'
            else:
                pass
        except Exception as e:
            pass
    
    def send_test_signal(self, instance):
        try:
            response = requests.post(f"{self.api_url}/api/send-test-signal", timeout=5)
            if response.status_code == 200:
                pass
            else:
                pass
        except Exception as e:
            pass
    
    def refresh_status(self, instance):
        self.update_status(0)
    
    def update_status(self, dt):
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
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

if __name__ == '__main__':
    CryptoSniperApp().run()
EOF

# Build APK
buildozer android debug

echo "APK built successfully!"
echo "APK location: bin/cryptosniperxprobot-2.0.0-debug.apk"