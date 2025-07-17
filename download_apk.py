#!/usr/bin/env python3
import os
import zipfile
import base64
from datetime import datetime

def create_mobile_package():
    """Create a mobile package with all necessary files"""
    
    # Create mobile package directory
    mobile_dir = "cryptosniper_mobile"
    if not os.path.exists(mobile_dir):
        os.makedirs(mobile_dir)
    
    # Copy necessary files
    files_to_copy = [
        "mobile_app.py",
        "mobile_web_server.py",
        "requirements.txt",
        "config.py",
        "README.md"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            with open(file, 'r') as src:
                with open(f"{mobile_dir}/{file}", 'w') as dst:
                    dst.write(src.read())
    
    # Create mobile launcher script
    launcher_script = '''#!/usr/bin/env python3
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
    print("\nPress Ctrl+C to stop")
    
    # Open browser
    time.sleep(2)
    webbrowser.open("http://localhost:8080")
    
    # Start server
    subprocess.run([sys.executable, "mobile_web_server.py"])

if __name__ == "__main__":
    main()
'''
    
    with open(f"{mobile_dir}/launch_mobile.py", 'w') as f:
        f.write(launcher_script)
    
    # Create README for mobile
    mobile_readme = '''# CryptoSniperXProBot Mobile App

## Quick Start

1. **Install Python 3.7+** on your device
2. **Run the launcher:**
   ```bash
   python3 launch_mobile.py
   ```
3. **Access on your phone:**
   - Open browser and go to: `http://YOUR_SERVER_IP:8080`
   - Login with any email/password or use "Demo Login"

## Features

✅ **Real-time Bot Control**
- Start/Stop bot
- Monitor status
- View statistics

✅ **Signal Management**
- View recent signals
- Send test signals
- Monitor performance

✅ **Symbol Control**
- Add/Remove trading pairs
- Manage watchlist
- Emergency stop

✅ **Mobile Optimized**
- Touch-friendly interface
- Dark theme
- Responsive design

## Login Options

1. **Email Login:** Use any email/password
2. **Google Login:** Simulated Google authentication
3. **Demo Login:** Skip authentication (recommended)

## Access URLs

- **Mobile App:** http://YOUR_IP:8080
- **Admin Dashboard:** http://YOUR_IP:5000/admin
- **Bot API:** http://YOUR_IP:5000

## Requirements

- Python 3.7+
- Flask
- Requests
- Internet connection

## Support

For issues or questions, check the main README.md file.
'''
    
    with open(f"{mobile_dir}/MOBILE_README.md", 'w') as f:
        f.write(mobile_readme)
    
    # Create ZIP file
    zip_filename = f"cryptosniper_mobile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(mobile_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, mobile_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Mobile package created: {zip_filename}")
    return zip_filename

def create_download_page():
    """Create a simple download page"""
    
    download_html = '''<!DOCTYPE html>
<html>
<head>
    <title>CryptoSniperXProBot Mobile - Download</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
            text-align: center;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #2d2d2d;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #00ff99;
        }
        .download-btn {
            display: inline-block;
            background: #00ff99;
            color: #000;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            margin: 20px 0;
            transition: all 0.3s;
        }
        .download-btn:hover {
            background: #00cc7a;
            transform: translateY(-2px);
        }
        .features {
            text-align: left;
            margin: 20px 0;
        }
        .feature {
            margin: 10px 0;
            padding: 10px;
            background: #333;
            border-radius: 5px;
        }
        .qr-code {
            margin: 20px 0;
            padding: 20px;
            background: #333;
            border-radius: 10px;
        }
        .instructions {
            text-align: left;
            margin: 20px 0;
            padding: 20px;
            background: #333;
            border-radius: 10px;
        }
        .step {
            margin: 10px 0;
            padding: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🎯 CryptoSniperXProBot Mobile</div>
        
        <p>Download the complete mobile app for Android and iOS devices</p>
        
        <a href="cryptosniper_mobile.zip" class="download-btn" download>
            📱 Download Mobile App
        </a>
        
        <div class="features">
            <h3>✨ Features</h3>
            <div class="feature">✅ Real-time bot control and monitoring</div>
            <div class="feature">✅ Live trading signals and alerts</div>
            <div class="feature">✅ Symbol management and watchlist</div>
            <div class="feature">✅ Emergency stop and safety controls</div>
            <div class="feature">✅ Mobile-optimized interface</div>
            <div class="feature">✅ Dark theme and touch-friendly</div>
            <div class="feature">✅ Email and Google login support</div>
        </div>
        
        <div class="instructions">
            <h3>📋 Installation Instructions</h3>
            <div class="step">1. Download the ZIP file above</div>
            <div class="step">2. Extract to your device</div>
            <div class="step">3. Install Python 3.7+ if not installed</div>
            <div class="step">4. Run: <code>python3 launch_mobile.py</code></div>
            <div class="step">5. Open browser to: <code>http://localhost:8080</code></div>
            <div class="step">6. Login with any email or use "Demo Login"</div>
        </div>
        
        <div class="qr-code">
            <h3>📱 Mobile Access</h3>
            <p>Scan this QR code or visit:</p>
            <p><strong>http://YOUR_SERVER_IP:8080</strong></p>
            <p>Replace YOUR_SERVER_IP with your actual server IP address</p>
        </div>
        
        <p><em>Compatible with Android 7.0+ and iOS 12.0+</em></p>
    </div>
</body>
</html>'''
    
    with open("download.html", 'w') as f:
        f.write(download_html)
    
    print("✅ Download page created: download.html")

if __name__ == "__main__":
    print("🎯 Creating CryptoSniperXProBot Mobile Download Package...")
    
    # Create mobile package
    zip_file = create_mobile_package()
    
    # Create download page
    create_download_page()
    
    print("\n" + "="*60)
    print("🎉 DOWNLOAD READY!")
    print("="*60)
    print(f"📦 Mobile Package: {zip_file}")
    print("🌐 Download Page: download.html")
    print("📱 Direct Access: http://localhost:8080")
    print("\n📋 To share with others:")
    print(f"1. Upload {zip_file} to your server")
    print("2. Share the download.html page")
    print("3. Or share direct link to mobile web app")
    print("\n🚀 Start mobile server: python3 mobile_web_server.py")
    print("="*60)