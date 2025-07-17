#!/usr/bin/env python3
import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🎯 CryptoSniperXProBot Mobile Launcher")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import flask
        import requests
        print("✅ Dependencies found")
    except ImportError:
        print("❌ Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "requests"])
    
    # Start mobile web server
    print("🚀 Starting mobile web server...")
    print("📱 Access on your phone: http://YOUR_IP:8080")
    print("🌐 Local access: http://localhost:8080")
    print("🔐 Login: any email/password or use Demo Login")
    print("
Press Ctrl+C to stop")
    
    # Open browser
    time.sleep(2)
    webbrowser.open("http://localhost:8080")
    
    # Start server
    subprocess.run([sys.executable, "mobile_web_server.py"])

if __name__ == "__main__":
    main()
