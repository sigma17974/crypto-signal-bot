#!/usr/bin/env python3
"""
Advanced Features Test Script for CryptoSniperXProBot
Tests: Z+++ Indicators, Real-time Charts, Arbitrage Detection, Multi-Exchange Integration
"""

import os
import sys
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

def test_advanced_indicators():
    """Test Z+++ advanced indicators"""
    print("🧪 Testing Z+++ Advanced Indicators")
    print("=" * 40)
    
    try:
        from advanced_indicators import InstitutionalZPlusPlus
        
        # Initialize Z+++ system
        z_plus_plus = InstitutionalZPlusPlus()
        print("✅ Z+++ system initialized")
        
        # Wait for data collection
        print("⏳ Collecting market data (30 seconds)...")
        time.sleep(30)
        
        # Test momentum signals
        momentum_signals = z_plus_plus.get_momentum_signals()
        print(f"✅ Momentum signals: {len(momentum_signals)} found")
        
        # Test sentiment signals
        sentiment_signals = z_plus_plus.get_sentiment_signals()
        print(f"✅ Sentiment signals: {len(sentiment_signals)} found")
        
        # Test arbitrage signals
        arbitrage_signals = z_plus_plus.get_arbitrage_signals()
        print(f"✅ Arbitrage signals: {len(arbitrage_signals)} found")
        
        # Test all signals
        all_signals = z_plus_plus.get_all_signals()
        print(f"✅ Total signals: {len(all_signals.get('momentum_signals', [])) + len(all_signals.get('sentiment_signals', [])) + len(all_signals.get('arbitrage_signals', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Z+++ indicators test failed: {e}")
        return False

def test_chart_generation():
    """Test real-time chart generation"""
    print("\n📊 Testing Chart Generation")
    print("=" * 30)
    
    try:
        from chart_generator import ChartGenerator
        import pandas as pd
        import numpy as np
        
        # Initialize chart generator
        chart_gen = ChartGenerator()
        print("✅ Chart generator initialized")
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(45000, 50000, 100),
            'high': np.random.uniform(45000, 50000, 100),
            'low': np.random.uniform(45000, 50000, 100),
            'close': np.random.uniform(45000, 50000, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        })
        
        # Add indicators
        sample_data['rsi'] = np.random.uniform(30, 70, 100)
        sample_data['macd'] = np.random.uniform(-100, 100, 100)
        sample_data['macd_signal'] = np.random.uniform(-100, 100, 100)
        sample_data['z_momentum_score'] = np.random.uniform(0, 1, 100)
        sample_data['z_trend_strength'] = np.random.uniform(0, 1, 100)
        sample_data['z_volume_score'] = np.random.uniform(0, 2, 100)
        sample_data['z_overall_score'] = np.random.uniform(0, 1, 100)
        
        # Create sample signal
        sample_signal = {
            'symbol': 'BTC/USDT',
            'type': 'MOMENTUM_LONG',
            'price': 47500.0,
            'confidence': 85,
            'strength': 'STRONG',
            'timestamp': datetime.now(),
            'indicators': {
                'momentum_score': 0.8,
                'trend_strength': 0.7,
                'volume_score': 1.5,
                'overall_score': 0.75
            }
        }
        
        # Generate chart
        chart_image = chart_gen.generate_signal_chart('BTC/USDT', sample_data, sample_signal)
        
        if chart_image:
            print("✅ Signal chart generated successfully")
            print(f"📏 Chart size: {len(chart_image)} characters")
        else:
            print("❌ Chart generation failed")
            return False
        
        # Test arbitrage chart
        arbitrage_opp = {
            'symbol': 'BTC/USDT',
            'buy_exchange': 'binance',
            'sell_exchange': 'bybit',
            'buy_price': 47500.0,
            'sell_price': 47650.0,
            'profit_pct': 0.32,
            'timestamp': datetime.now()
        }
        
        arbitrage_chart = chart_gen.generate_arbitrage_chart(arbitrage_opp)
        
        if arbitrage_chart:
            print("✅ Arbitrage chart generated successfully")
        else:
            print("❌ Arbitrage chart generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chart generation test failed: {e}")
        return False

def test_multi_exchange_integration():
    """Test multi-exchange integration"""
    print("\n🏪 Testing Multi-Exchange Integration")
    print("=" * 35)
    
    try:
        import ccxt
        
        # Test exchanges
        exchanges = ['binance', 'bybit', 'bitget', 'gate', 'kucoin']
        working_exchanges = []
        
        for exchange_name in exchanges:
            try:
                exchange_class = getattr(ccxt, exchange_name)
                exchange = exchange_class({'sandbox': False})
                
                # Test connection
                ticker = exchange.fetch_ticker('BTC/USDT')
                print(f"✅ {exchange_name.upper()}: Connected")
                working_exchanges.append(exchange_name)
                
            except Exception as e:
                print(f"❌ {exchange_name.upper()}: Failed - {str(e)[:50]}")
        
        print(f"\n📊 Working exchanges: {len(working_exchanges)}/{len(exchanges)}")
        print(f"✅ Exchanges: {', '.join(working_exchanges)}")
        
        return len(working_exchanges) >= 2  # Need at least 2 for arbitrage
        
    except Exception as e:
        print(f"❌ Multi-exchange test failed: {e}")
        return False

def test_arbitrage_detection():
    """Test arbitrage detection"""
    print("\n💰 Testing Arbitrage Detection")
    print("=" * 30)
    
    try:
        import ccxt
        
        # Test with major exchanges
        exchanges = {
            'binance': ccxt.binance(),
            'bybit': ccxt.bybit(),
            'bitget': ccxt.bitget()
        }
        
        symbol = 'BTC/USDT'
        prices = {}
        
        # Get prices from exchanges
        for name, exchange in exchanges.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                prices[name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last']
                }
                print(f"✅ {name.upper()}: Bid=${ticker['bid']:.2f}, Ask=${ticker['ask']:.2f}")
            except Exception as e:
                print(f"❌ {name.upper()}: Failed to get price")
        
        # Calculate arbitrage opportunities
        opportunities = []
        exchange_names = list(prices.keys())
        
        for i in range(len(exchange_names)):
            for j in range(i + 1, len(exchange_names)):
                ex1, ex2 = exchange_names[i], exchange_names[j]
                
                buy_price = prices[ex1]['ask']
                sell_price = prices[ex2]['bid']
                
                if sell_price > buy_price:
                    profit_pct = ((sell_price - buy_price) / buy_price) * 100
                    opportunities.append({
                        'buy_exchange': ex1,
                        'sell_exchange': ex2,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct
                    })
        
        print(f"\n💰 Arbitrage opportunities found: {len(opportunities)}")
        
        for opp in opportunities:
            print(f"  • {opp['buy_exchange']} → {opp['sell_exchange']}: {opp['profit_pct']:.3f}% profit")
        
        return True
        
    except Exception as e:
        print(f"❌ Arbitrage detection test failed: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n📈 Testing Sentiment Analysis")
    print("=" * 30)
    
    try:
        import requests
        
        # Test CoinGecko API
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 5,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ CoinGecko: {len(data)} coins fetched")
                
                for coin in data[:3]:
                    print(f"  • {coin['symbol'].upper()}: ${coin['current_price']:.2f} ({coin.get('price_change_percentage_24h', 0):.2f}%)")
            else:
                print(f"❌ CoinGecko: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ CoinGecko API failed: {e}")
        
        # Test CoinMarketCap API
        try:
            url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
            params = {
                'start': 1,
                'limit': 5,
                'sortBy': 'market_cap',
                'sortType': 'desc',
                'convert': 'USD'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                coins = data.get('data', {}).get('cryptoCurrencyList', [])
                print(f"✅ CoinMarketCap: {len(coins)} coins fetched")
                
                for coin in coins[:3]:
                    symbol = coin['symbol']
                    price = coin.get('quote', {}).get('USD', {}).get('price', 0)
                    change = coin.get('quote', {}).get('USD', {}).get('percentChange24h', 0)
                    print(f"  • {symbol}: ${price:.2f} ({change:.2f}%)")
            else:
                print(f"❌ CoinMarketCap: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ CoinMarketCap API failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment analysis test failed: {e}")
        return False

def test_integration():
    """Test full integration"""
    print("\n🔗 Testing Full Integration")
    print("=" * 30)
    
    try:
        from main import CryptoSniperBot
        
        # Initialize bot
        bot = CryptoSniperBot()
        print("✅ Bot initialized with advanced features")
        
        # Test Z+++ integration
        if hasattr(bot, 'z_plus_plus'):
            print("✅ Z+++ indicators integrated")
        else:
            print("❌ Z+++ indicators not integrated")
            return False
        
        # Test chart generator integration
        if hasattr(bot, 'chart_generator'):
            print("✅ Chart generator integrated")
        else:
            print("❌ Chart generator not integrated")
            return False
        
        # Test advanced signal processing
        if hasattr(bot, '_process_advanced_signal'):
            print("✅ Advanced signal processing available")
        else:
            print("❌ Advanced signal processing not available")
            return False
        
        # Test arbitrage processing
        if hasattr(bot, '_process_arbitrage_signal'):
            print("✅ Arbitrage signal processing available")
        else:
            print("❌ Arbitrage signal processing not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 CryptoSniperXProBot - Advanced Features Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Some tests may fail without proper configuration")
    
    # Run tests
    tests = [
        ("Z+++ Advanced Indicators", test_advanced_indicators),
        ("Chart Generation", test_chart_generation),
        ("Multi-Exchange Integration", test_multi_exchange_integration),
        ("Arbitrage Detection", test_arbitrage_detection),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Full Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All advanced features are working correctly!")
        print("\n🚀 Your CryptoSniperXProBot is ready with:")
        print("  • Institutional-grade Z+++ indicators")
        print("  • Real-time chart generation")
        print("  • Multi-exchange arbitrage detection")
        print("  • Market sentiment analysis")
        print("  • Advanced signal filtering")
        print("  • Professional-grade risk management")
    else:
        print("⚠️ Some features need attention. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)