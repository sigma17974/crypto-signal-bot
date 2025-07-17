from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'cryptosniper_secret_key'

BOT_API_URL = "http://localhost:5000"

# Mobile HTML template
MOBILE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoSniperXProBot Mobile</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background: #1a1a1a;
            color: #ffffff;
        }
        .header {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #00ff99;
        }
        .card {
            background: #2d2d2d;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .btn {
            background: #00ff99;
            color: #000;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            width: 100%;
        }
        .btn:hover {
            background: #00cc7a;
        }
        .btn.danger {
            background: #ff4444;
        }
        .btn.danger:hover {
            background: #cc3333;
        }
        .input {
            width: 100%;
            padding: 10px;
            border: 2px solid #444;
            border-radius: 5px;
            background: #333;
            color: #fff;
            font-size: 16px;
            box-sizing: border-box;
            margin-bottom: 10px;
        }
        .input:focus {
            border-color: #00ff99;
            outline: none;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 15px 0;
        }
        .stat {
            background: #333;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #00ff99;
        }
        .stat-label {
            font-size: 12px;
            opacity: 0.7;
        }
        .status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff4444;
        }
        .status-indicator.running {
            background: #00ff99;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            background: #333;
            border: none;
            color: #fff;
            cursor: pointer;
        }
        .tab.active {
            background: #00ff99;
            color: #000;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .login-form {
            max-width: 400px;
            margin: 0 auto;
        }
        .logout-btn {
            background: #ff4444;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            float: right;
        }
    </style>
</head>
<body>
    <div class="header">
        🎯 CryptoSniperXProBot Mobile
        <button class="logout-btn" onclick="logout()">Logout</button>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('dashboard')">Dashboard</button>
        <button class="tab" onclick="showTab('signals')">Signals</button>
        <button class="tab" onclick="showTab('control')">Control</button>
        <button class="tab" onclick="showTab('settings')">Settings</button>
    </div>
    
    <div id="dashboard" class="tab-content active">
        <div class="card">
            <div class="status">
                <span>Bot Status</span>
                <div class="status-indicator" id="status-indicator"></div>
            </div>
            <button class="btn" id="start-stop-btn" onclick="toggleBot()">Start Bot</button>
        </div>
        
        <div class="card">
            <h3>Statistics</h3>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="signals-count">0</div>
                    <div class="stat-label">Signals Generated</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="active-signals">0</div>
                    <div class="stat-label">Active Signals</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="symbols-count">0</div>
                    <div class="stat-label">Symbols Monitored</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="uptime">0h</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Quick Actions</h3>
            <button class="btn" onclick="sendTestSignal()">Send Test Signal</button>
            <button class="btn" onclick="refreshStatus()">Refresh Status</button>
        </div>
    </div>
    
    <div id="signals" class="tab-content">
        <div class="card">
            <h3>Recent Signals</h3>
            <div id="signals-list">
                <p>No signals yet. Bot will generate signals when running.</p>
            </div>
        </div>
    </div>
    
    <div id="control" class="tab-content">
        <div class="card">
            <h3>Symbol Management</h3>
            <input type="text" class="input" id="symbol-input" placeholder="e.g., BTC/USDT" value="BTC/USDT">
            <button class="btn" onclick="addSymbol()">Add Symbol</button>
            <input type="text" class="input" id="remove-input" placeholder="e.g., BTC/USDT" value="BTC/USDT">
            <button class="btn danger" onclick="removeSymbol()">Remove Symbol</button>
        </div>
        
        <div class="card">
            <h3>Bot Control</h3>
            <button class="btn" onclick="toggleScanning()">Toggle Scanning</button>
            <button class="btn danger" onclick="emergencyStop()">Emergency Stop</button>
        </div>
    </div>
    
    <div id="settings" class="tab-content">
        <div class="card">
            <h3>App Settings</h3>
            <p><strong>User:</strong> <span id="user-email">demo@example.com</span></p>
            <p><strong>Bot API:</strong> http://localhost:5000</p>
            <p><strong>Admin Dashboard:</strong> <a href="http://localhost:5000/admin" style="color: #00ff99;">http://localhost:5000/admin</a></p>
            <p><strong>Login:</strong> admin / admin123</p>
        </div>
    </div>
    
    <script>
        let botRunning = false;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const indicator = document.getElementById('status-indicator');
                    const btn = document.getElementById('start-stop-btn');
                    
                    if (data.status === 'running') {
                        indicator.classList.add('running');
                        btn.textContent = 'Stop Bot';
                        botRunning = true;
                    } else {
                        indicator.classList.remove('running');
                        btn.textContent = 'Start Bot';
                        botRunning = false;
                    }
                    
                    document.getElementById('signals-count').textContent = data.signals_generated || 0;
                    document.getElementById('active-signals').textContent = data.active_signals || 0;
                    document.getElementById('symbols-count').textContent = data.symbols_monitored || 0;
                    document.getElementById('uptime').textContent = data.uptime || '0h';
                })
                .catch(error => {
                    console.error('Error updating status:', error);
                });
        }
        
        function toggleBot() {
            const action = botRunning ? 'stop' : 'start';
            fetch(`/api/${action}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        updateStatus();
                    }
                })
                .catch(error => {
                    console.error('Error toggling bot:', error);
                });
        }
        
        function sendTestSignal() {
            fetch('/api/send-test-signal', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        alert('Test signal sent successfully!');
                    } else {
                        alert('Failed to send test signal');
                    }
                })
                .catch(error => {
                    console.error('Error sending test signal:', error);
                });
        }
        
        function addSymbol() {
            const symbol = document.getElementById('symbol-input').value;
            fetch('/api/add-symbol', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ symbol: symbol })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    alert(`Symbol ${symbol} added successfully!`);
                    updateStatus();
                } else {
                    alert('Failed to add symbol');
                }
            })
            .catch(error => {
                console.error('Error adding symbol:', error);
            });
        }
        
        function removeSymbol() {
            const symbol = document.getElementById('remove-input').value;
            fetch('/api/remove-symbol', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ symbol: symbol })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    alert(`Symbol ${symbol} removed successfully!`);
                    updateStatus();
                } else {
                    alert('Failed to remove symbol');
                }
            })
            .catch(error => {
                console.error('Error removing symbol:', error);
            });
        }
        
        function refreshStatus() {
            updateStatus();
        }
        
        function toggleScanning() {
            fetch('/api/toggle-scanning', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        alert(`Scanning ${data.scanning ? 'enabled' : 'disabled'}`);
                    }
                })
                .catch(error => {
                    console.error('Error toggling scanning:', error);
                });
        }
        
        function emergencyStop() {
            if (confirm('Are you sure you want to emergency stop the bot?')) {
                fetch('/api/emergency-stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            alert('Bot stopped in emergency mode!');
                            updateStatus();
                        } else {
                            alert('Emergency stop failed');
                        }
                    })
                    .catch(error => {
                        console.error('Error during emergency stop:', error);
                    });
            }
        }
        
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/logout';
            }
        }
        
        // Update status every 5 seconds
        setInterval(updateStatus, 5000);
        
        // Initial status update
        updateStatus();
    </script>
</body>
</html>
'''

# Login HTML
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoSniperXProBot - Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-container {
            background: #2d2d2d;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .header {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 30px;
            color: #00ff99;
        }
        .input {
            width: 100%;
            padding: 12px;
            border: 2px solid #444;
            border-radius: 8px;
            background: #333;
            color: #fff;
            font-size: 16px;
            box-sizing: border-box;
            margin-bottom: 15px;
        }
        .input:focus {
            border-color: #00ff99;
            outline: none;
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: #00ff99;
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #00cc7a;
        }
        .btn.google {
            background: #4285f4;
            color: white;
        }
        .btn.google:hover {
            background: #3367d6;
        }
        .demo-note {
            text-align: center;
            font-size: 12px;
            opacity: 0.7;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">🎯 CryptoSniperXProBot</div>
        
        <form method="POST" action="/login">
            <input type="email" name="email" class="input" placeholder="Email" required>
            <input type="password" name="password" class="input" placeholder="Password" required>
            <button type="submit" class="btn">Login with Email</button>
        </form>
        
        <button class="btn google" onclick="googleLogin()">Login with Google</button>
        <button class="btn" onclick="demoLogin()">Demo Login (Skip)</button>
        
        <div class="demo-note">
            Demo: Use any email/password or click Demo Login
        </div>
    </div>
    
    <script>
        function googleLogin() {
            // Simulate Google login
            window.location.href = '/google-login';
        }
        
        function demoLogin() {
            window.location.href = '/demo-login';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def mobile_interface():
    if 'user_logged_in' not in session:
        return redirect('/login')
    return MOBILE_HTML

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple validation
        if email and password:
            session['user_logged_in'] = True
            session['user_email'] = email
            return redirect('/')
        else:
            return "Invalid credentials", 401
    
    return LOGIN_HTML

@app.route('/google-login')
def google_login():
    session['user_logged_in'] = True
    session['user_email'] = 'google_user@example.com'
    return redirect('/')

@app.route('/demo-login')
def demo_login():
    session['user_logged_in'] = True
    session['user_email'] = 'demo_user@example.com'
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/status')
def get_status():
    try:
        response = requests.get(f"{BOT_API_URL}/api/status", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'status': 'error', 'message': 'Bot not responding'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/start', methods=['POST'])
def start_bot():
    try:
        response = requests.post(f"{BOT_API_URL}/api/start", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    try:
        response = requests.post(f"{BOT_API_URL}/api/stop", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/send-test-signal', methods=['POST'])
def send_test_signal():
    try:
        response = requests.post(f"{BOT_API_URL}/api/send-test-signal", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/add-symbol', methods=['POST'])
def add_symbol():
    try:
        data = request.get_json()
        response = requests.post(
            f"{BOT_API_URL}/api/add-symbol",
            json=data,
            timeout=5
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/remove-symbol', methods=['POST'])
def remove_symbol():
    try:
        data = request.get_json()
        response = requests.post(
            f"{BOT_API_URL}/api/remove-symbol",
            json=data,
            timeout=5
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/toggle-scanning', methods=['POST'])
def toggle_scanning():
    try:
        response = requests.post(f"{BOT_API_URL}/api/toggle-scanning", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop():
    try:
        response = requests.post(f"{BOT_API_URL}/api/emergency-stop", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("🚀 Starting CryptoSniperXProBot Mobile Web Server...")
    print("📱 Access on your phone: http://YOUR_SERVER_IP:8080")
    print("🌐 Local access: http://localhost:8080")
    print("🔐 Login with email or Google account")
    app.run(host='0.0.0.0', port=8080, debug=False)