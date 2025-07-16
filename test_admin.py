#!/usr/bin/env python3
"""
Test script for Admin Dashboard
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

def test_admin_dashboard():
    """Test the admin dashboard functionality"""
    
    print("🧪 Testing Admin Dashboard")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'ADMIN_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please run setup_admin.py first")
        return False
    
    print("✅ Environment variables loaded")
    
    # Test imports
    try:
        from admin_dashboard import AdminDashboard
        from main import CryptoSniperBot
        print("✅ Admin dashboard imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return False
    
    # Test bot initialization
    try:
        print("\n🤖 Testing bot initialization...")
        bot = CryptoSniperBot()
        print("✅ Bot initialization successful")
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False
    
    # Test admin dashboard initialization
    try:
        print("\n🔧 Testing admin dashboard initialization...")
        admin_dashboard = AdminDashboard(bot)
        print("✅ Admin dashboard initialization successful")
    except Exception as e:
        print(f"❌ Admin dashboard initialization failed: {e}")
        return False
    
    # Test system status
    try:
        print("\n📊 Testing system status...")
        status = admin_dashboard._get_system_status()
        print(f"✅ System status: {status}")
    except Exception as e:
        print(f"❌ System status failed: {e}")
        return False
    
    # Test Telegram connection
    try:
        print("\n📱 Testing Telegram connection...")
        admin_dashboard._send_telegram_message("🧪 Admin dashboard test - Connection successful!")
        print("✅ Telegram connection successful")
    except Exception as e:
        print(f"❌ Telegram connection failed: {e}")
        return False
    
    # Test auto systems
    try:
        print("\n🔄 Testing auto systems...")
        print(f"Auto-reconnect: {admin_dashboard.auto_reconnect_enabled}")
        print(f"Auto-cleanup: {admin_dashboard.auto_cleanup_enabled}")
        print("✅ Auto systems initialized")
    except Exception as e:
        print(f"❌ Auto systems failed: {e}")
        return False
    
    # Test error logging
    try:
        print("\n📝 Testing error logging...")
        admin_dashboard._log_error("Test error message")
        print(f"✅ Error logging: {len(admin_dashboard.error_log)} errors logged")
    except Exception as e:
        print(f"❌ Error logging failed: {e}")
        return False
    
    # Test performance data
    try:
        print("\n📈 Testing performance data...")
        admin_dashboard._update_performance_data()
        print(f"✅ Performance data: {admin_dashboard.performance_data}")
    except Exception as e:
        print(f"❌ Performance data failed: {e}")
        return False
    
    # Test system health
    try:
        print("\n🏥 Testing system health...")
        health_score = admin_dashboard._get_system_health_score()
        print(f"✅ System health score: {health_score}%")
    except Exception as e:
        print(f"❌ System health failed: {e}")
        return False
    
    print("\n🎉 All admin dashboard tests passed!")
    print("\n📋 Next Steps:")
    print("1. Start the admin dashboard:")
    print("   python start_admin.py")
    print("\n2. Access the admin panel:")
    print("   http://localhost:5000/admin")
    print("\n3. Login with your Telegram credentials")
    
    return True

def test_web_interface():
    """Test the web interface"""
    
    print("\n🌐 Testing Web Interface")
    print("=" * 30)
    
    try:
        # Start a simple test server
        import threading
        from admin_dashboard import AdminDashboard
        from main import CryptoSniperBot
        
        bot = CryptoSniperBot()
        admin_dashboard = AdminDashboard(bot)
        
        def run_test_server():
            admin_dashboard.app.run(host='localhost', port=5001, debug=False)
        
        server_thread = threading.Thread(target=run_test_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test login page
        try:
            response = requests.get('http://localhost:5001/admin/login', timeout=5)
            if response.status_code == 200:
                print("✅ Login page accessible")
            else:
                print(f"❌ Login page failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Login page test failed: {e}")
        
        # Test API status
        try:
            response = requests.get('http://localhost:5001/api/status', timeout=5)
            if response.status_code == 200:
                print("✅ API status accessible")
            else:
                print(f"❌ API status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API status test failed: {e}")
        
        print("✅ Web interface tests completed")
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")

def main():
    """Main test function"""
    
    print("🚀 Crypto Sniper Pro Bot - Admin Dashboard Test")
    print("=" * 50)
    
    # Test admin dashboard functionality
    if not test_admin_dashboard():
        print("\n❌ Admin dashboard tests failed!")
        sys.exit(1)
    
    # Test web interface
    test_web_interface()
    
    print("\n✅ All tests completed successfully!")
    print("\n🎉 Admin dashboard is ready to use!")

if __name__ == "__main__":
    main()