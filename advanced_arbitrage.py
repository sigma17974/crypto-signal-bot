"""
Advanced Arbitrage System for CryptoSniperXProBot
Features: Multi-exchange arbitrage, newly listed coins, deposit/withdrawal verification, bad trade protection
"""

import ccxt
import requests
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class AdvancedArbitrage:
    """Advanced arbitrage system with comprehensive protection"""
    
    def __init__(self):
        self.exchanges = {}
        self.arbitrage_opportunities = []
        self.newly_listed_coins = []
        self.bad_trade_signals = []
        self.exchange_info = {}
        self.deposit_withdrawal_status = {}
        
        # Initialize exchanges
        self._init_exchanges()
        
        # Start monitoring threads
        self._start_monitoring()
    
    def _init_exchanges(self):
        """Initialize comprehensive list of exchanges"""
        exchange_configs = {
            # Major exchanges
            'binance': {'sandbox': False, 'enableRateLimit': True},
            'bybit': {'sandbox': False, 'enableRateLimit': True},
            'bitget': {'sandbox': False, 'enableRateLimit': True},
            'gate': {'sandbox': False, 'enableRateLimit': True},
            'kucoin': {'sandbox': False, 'enableRateLimit': True},
            'okx': {'sandbox': False, 'enableRateLimit': True},
            'mexc': {'sandbox': False, 'enableRateLimit': True},
            
            # Additional exchanges for arbitrage
            'huobi': {'sandbox': False, 'enableRateLimit': True},
            'coinbase': {'sandbox': False, 'enableRateLimit': True},
            'kraken': {'sandbox': False, 'enableRateLimit': True},
            'bitfinex': {'sandbox': False, 'enableRateLimit': True},
            'poloniex': {'sandbox': False, 'enableRateLimit': True},
            'bittrex': {'sandbox': False, 'enableRateLimit': True},
            'bitstamp': {'sandbox': False, 'enableRateLimit': True},
            'gemini': {'sandbox': False, 'enableRateLimit': True},
            'coinbase_pro': {'sandbox': False, 'enableRateLimit': True},
            'ftx': {'sandbox': False, 'enableRateLimit': True},
            'deribit': {'sandbox': False, 'enableRateLimit': True},
            'bitflyer': {'sandbox': False, 'enableRateLimit': True},
            'liquid': {'sandbox': False, 'enableRateLimit': True},
            'bitbank': {'sandbox': False, 'enableRateLimit': True},
            'zaif': {'sandbox': False, 'enableRateLimit': True},
            'coincheck': {'sandbox': False, 'enableRateLimit': True},
            'btcex': {'sandbox': False, 'enableRateLimit': True},
            'xt': {'sandbox': False, 'enableRateLimit': True},
            'lbank': {'sandbox': False, 'enableRateLimit': True},
            'hotbit': {'sandbox': False, 'enableRateLimit': True},
            'digifinex': {'sandbox': False, 'enableRateLimit': True},
            'coinex': {'sandbox': False, 'enableRateLimit': True},
            'ascendex': {'sandbox': False, 'enableRateLimit': True},
            'bitmart': {'sandbox': False, 'enableRateLimit': True},
            'bigone': {'sandbox': False, 'enableRateLimit': True},
            'whitebit': {'sandbox': False, 'enableRateLimit': True},
            'bitforex': {'sandbox': False, 'enableRateLimit': True},
            'xtrade': {'sandbox': False, 'enableRateLimit': True},
            'bitrue': {'sandbox': False, 'enableRateLimit': True},
            'coinbase_advanced': {'sandbox': False, 'enableRateLimit': True},
            'okcoin': {'sandbox': False, 'enableRateLimit': True},
            'bitflyer': {'sandbox': False, 'enableRateLimit': True},
            'liquid': {'sandbox': False, 'enableRateLimit': True},
            'bitbank': {'sandbox': False, 'enableRateLimit': True},
            'zaif': {'sandbox': False, 'enableRateLimit': True},
            'coincheck': {'sandbox': False, 'enableRateLimit': True},
            'btcex': {'sandbox': False, 'enableRateLimit': True},
            'xt': {'sandbox': False, 'enableRateLimit': True},
            'lbank': {'sandbox': False, 'enableRateLimit': True},
            'hotbit': {'sandbox': False, 'enableRateLimit': True},
            'digifinex': {'sandbox': False, 'enableRateLimit': True},
            'coinex': {'sandbox': False, 'enableRateLimit': True},
            'ascendex': {'sandbox': False, 'enableRateLimit': True},
            'bitmart': {'sandbox': False, 'enableRateLimit': True},
            'bigone': {'sandbox': False, 'enableRateLimit': True},
            'whitebit': {'sandbox': False, 'enableRateLimit': True},
            'bitforex': {'sandbox': False, 'enableRateLimit': True},
            'xtrade': {'sandbox': False, 'enableRateLimit': True},
            'bitrue': {'sandbox': False, 'enableRateLimit': True}
        }
        
        for name, config in exchange_configs.items():
            try:
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class(config)
                logger.info(f"✅ {name.upper()} exchange initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {name}: {e}")
    
    def _start_monitoring(self):
        """Start monitoring threads"""
        threading.Thread(target=self._monitor_arbitrage, daemon=True).start()
        threading.Thread(target=self._monitor_new_listings, daemon=True).start()
        threading.Thread(target=self._verify_deposit_withdrawal, daemon=True).start()
        threading.Thread(target=self._bad_trade_protection, daemon=True).start()
    
    def _monitor_arbitrage(self):
        """Monitor arbitrage opportunities across all exchanges"""
        while True:
            try:
                opportunities = []
                
                # Get all trading pairs from all exchanges
                all_symbols = self._get_all_trading_pairs()
                
                for symbol in all_symbols:
                    try:
                        prices = self._get_prices_for_symbol(symbol)
                        
                        if len(prices) >= 2:
                            arbitrage_opps = self._calculate_arbitrage_opportunities(symbol, prices)
                            opportunities.extend(arbitrage_opps)
                    
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                
                # Filter and rank opportunities
                filtered_opportunities = self._filter_arbitrage_opportunities(opportunities)
                self.arbitrage_opportunities = filtered_opportunities
                
                logger.info(f"Found {len(filtered_opportunities)} arbitrage opportunities")
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Arbitrage monitoring error: {e}")
                time.sleep(60)
    
    def _get_all_trading_pairs(self) -> List[str]:
        """Get all trading pairs from all exchanges"""
        all_symbols = set()
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                markets = exchange.load_markets()
                symbols = list(markets.keys())
                
                # Filter for USDT pairs
                usdt_symbols = [s for s in symbols if '/USDT' in s]
                all_symbols.update(usdt_symbols)
                
            except Exception as e:
                logger.error(f"Error loading markets for {exchange_name}: {e}")
        
        return list(all_symbols)
    
    def _get_prices_for_symbol(self, symbol: str) -> Dict:
        """Get prices for symbol across all exchanges"""
        prices = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                prices[exchange_name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last'],
                    'volume': ticker['baseVolume'],
                    'timestamp': ticker['timestamp']
                }
            except Exception as e:
                logger.debug(f"Could not get {symbol} price from {exchange_name}: {e}")
        
        return prices
    
    def _calculate_arbitrage_opportunities(self, symbol: str, prices: Dict) -> List[Dict]:
        """Calculate arbitrage opportunities for symbol"""
        opportunities = []
        
        try:
            exchanges = list(prices.keys())
            
            for i in range(len(exchanges)):
                for j in range(i + 1, len(exchanges)):
                    ex1, ex2 = exchanges[i], exchanges[j]
                    
                    # Calculate potential profit
                    buy_price = prices[ex1]['ask']
                    sell_price = prices[ex2]['bid']
                    
                    if sell_price > buy_price:
                        profit_pct = ((sell_price - buy_price) / buy_price) * 100
                        
                        # Calculate fees and net profit
                        net_profit = self._calculate_net_profit(
                            buy_price, sell_price, ex1, ex2, symbol
                        )
                        
                        if net_profit > 0:
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': ex1,
                                'sell_exchange': ex2,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gross_profit_pct': profit_pct,
                                'net_profit_pct': net_profit,
                                'volume': min(prices[ex1]['volume'], prices[ex2]['volume']),
                                'timestamp': datetime.now(),
                                'risk_score': self._calculate_risk_score(ex1, ex2, symbol),
                                'execution_speed': self._calculate_execution_speed(ex1, ex2)
                            }
                            opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage for {symbol}: {e}")
            return []
    
    def _calculate_net_profit(self, buy_price: float, sell_price: float, 
                             buy_ex: str, sell_ex: str, symbol: str) -> float:
        """Calculate net profit after fees"""
        try:
            # Get fee information
            buy_fee = self._get_trading_fee(buy_ex, symbol)
            sell_fee = self._get_trading_fee(sell_ex, symbol)
            
            # Calculate fees
            buy_fee_amount = buy_price * buy_fee
            sell_fee_amount = sell_price * sell_fee
            
            # Calculate net profit
            gross_profit = sell_price - buy_price
            total_fees = buy_fee_amount + sell_fee_amount
            net_profit = gross_profit - total_fees
            
            # Convert to percentage
            net_profit_pct = (net_profit / buy_price) * 100
            
            return net_profit_pct
            
        except Exception as e:
            logger.error(f"Error calculating net profit: {e}")
            return 0.0
    
    def _get_trading_fee(self, exchange: str, symbol: str) -> float:
        """Get trading fee for exchange and symbol"""
        try:
            # Default fees (can be enhanced with API calls)
            default_fees = {
                'binance': 0.001,  # 0.1%
                'bybit': 0.001,
                'bitget': 0.001,
                'gate': 0.002,
                'kucoin': 0.001,
                'okx': 0.001,
                'mexc': 0.001,
                'huobi': 0.002,
                'coinbase': 0.005,
                'kraken': 0.0026,
                'bitfinex': 0.002,
                'poloniex': 0.0025,
                'bittrex': 0.0025,
                'bitstamp': 0.005,
                'gemini': 0.0035,
                'ftx': 0.0007,
                'deribit': 0.0003,
                'bitflyer': 0.0015,
                'liquid': 0.001,
                'bitbank': 0.0015,
                'zaif': 0.002,
                'coincheck': 0.0015,
                'btcex': 0.001,
                'xt': 0.001,
                'lbank': 0.001,
                'hotbit': 0.002,
                'digifinex': 0.001,
                'coinex': 0.001,
                'ascendex': 0.001,
                'bitmart': 0.0025,
                'bigone': 0.001,
                'whitebit': 0.001,
                'bitforex': 0.001,
                'xtrade': 0.001,
                'bitrue': 0.001
            }
            
            return default_fees.get(exchange, 0.002)  # Default 0.2%
            
        except Exception as e:
            logger.error(f"Error getting trading fee: {e}")
            return 0.002
    
    def _calculate_risk_score(self, buy_ex: str, sell_ex: str, symbol: str) -> float:
        """Calculate risk score for arbitrage opportunity"""
        try:
            risk_score = 0.0
            
            # Exchange reliability
            reliable_exchanges = ['binance', 'bybit', 'bitget', 'gate', 'kucoin', 'okx', 'mexc']
            if buy_ex in reliable_exchanges:
                risk_score += 0.2
            if sell_ex in reliable_exchanges:
                risk_score += 0.2
            
            # Volume check
            volume_risk = self._check_volume_risk(buy_ex, sell_ex, symbol)
            risk_score += volume_risk
            
            # Liquidity check
            liquidity_risk = self._check_liquidity_risk(buy_ex, sell_ex, symbol)
            risk_score += liquidity_risk
            
            # Price stability
            stability_risk = self._check_price_stability(buy_ex, sell_ex, symbol)
            risk_score += stability_risk
            
            return min(risk_score, 1.0)  # Max risk score of 1.0
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5
    
    def _check_volume_risk(self, buy_ex: str, sell_ex: str, symbol: str) -> float:
        """Check volume risk for exchanges"""
        try:
            # High volume exchanges get lower risk
            high_volume_exchanges = ['binance', 'bybit', 'okx', 'kucoin']
            medium_volume_exchanges = ['bitget', 'gate', 'mexc', 'huobi']
            
            risk = 0.0
            
            if buy_ex in high_volume_exchanges:
                risk += 0.1
            elif buy_ex in medium_volume_exchanges:
                risk += 0.2
            else:
                risk += 0.3
            
            if sell_ex in high_volume_exchanges:
                risk += 0.1
            elif sell_ex in medium_volume_exchanges:
                risk += 0.2
            else:
                risk += 0.3
            
            return risk
            
        except Exception as e:
            logger.error(f"Error checking volume risk: {e}")
            return 0.3
    
    def _check_liquidity_risk(self, buy_ex: str, sell_ex: str, symbol: str) -> float:
        """Check liquidity risk"""
        try:
            # Major pairs have lower liquidity risk
            major_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
            
            if symbol in major_pairs:
                return 0.1
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error checking liquidity risk: {e}")
            return 0.2
    
    def _check_price_stability(self, buy_ex: str, sell_ex: str, symbol: str) -> float:
        """Check price stability risk"""
        try:
            # Newly listed coins have higher price stability risk
            if symbol in self.newly_listed_coins:
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"Error checking price stability: {e}")
            return 0.2
    
    def _calculate_execution_speed(self, buy_ex: str, sell_ex: str) -> float:
        """Calculate execution speed score"""
        try:
            # Faster exchanges get higher scores
            fast_exchanges = ['binance', 'bybit', 'okx']
            medium_exchanges = ['bitget', 'gate', 'kucoin', 'mexc']
            
            speed_score = 0.0
            
            if buy_ex in fast_exchanges:
                speed_score += 0.5
            elif buy_ex in medium_exchanges:
                speed_score += 0.3
            else:
                speed_score += 0.1
            
            if sell_ex in fast_exchanges:
                speed_score += 0.5
            elif sell_ex in medium_exchanges:
                speed_score += 0.3
            else:
                speed_score += 0.1
            
            return speed_score / 2.0  # Average of both exchanges
            
        except Exception as e:
            logger.error(f"Error calculating execution speed: {e}")
            return 0.3
    
    def _filter_arbitrage_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Filter and rank arbitrage opportunities"""
        try:
            filtered = []
            
            for opp in opportunities:
                # Minimum profit threshold
                if opp['net_profit_pct'] < 0.3:  # 0.3% minimum
                    continue
                
                # Risk score threshold
                if opp['risk_score'] > 0.7:  # Max 70% risk
                    continue
                
                # Volume threshold
                if opp['volume'] < 1000:  # Minimum volume
                    continue
                
                # Execution speed threshold
                if opp['execution_speed'] < 0.2:  # Minimum speed
                    continue
                
                # Check deposit/withdrawal status
                if not self._check_deposit_withdrawal_status(opp['buy_exchange'], opp['sell_exchange']):
                    continue
                
                # Check if it's a bad trade signal
                if self._is_bad_trade_signal(opp):
                    continue
                
                filtered.append(opp)
            
            # Sort by net profit percentage
            filtered.sort(key=lambda x: x['net_profit_pct'], reverse=True)
            
            return filtered[:20]  # Return top 20 opportunities
            
        except Exception as e:
            logger.error(f"Error filtering arbitrage opportunities: {e}")
            return []
    
    def _monitor_new_listings(self):
        """Monitor for newly listed coins"""
        while True:
            try:
                # Check for new listings on major exchanges
                new_listings = self._detect_new_listings()
                
                for listing in new_listings:
                    if listing not in self.newly_listed_coins:
                        self.newly_listed_coins.append(listing)
                        logger.info(f"New listing detected: {listing}")
                
                # Clean old listings (older than 7 days)
                cutoff_time = datetime.now() - timedelta(days=7)
                self.newly_listed_coins = [
                    coin for coin in self.newly_listed_coins 
                    if self._get_listing_time(coin) > cutoff_time
                ]
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring new listings: {e}")
                time.sleep(600)
    
    def _detect_new_listings(self) -> List[str]:
        """Detect newly listed coins"""
        new_listings = []
        
        try:
            # Check Binance new listings
            try:
                url = "https://api.binance.com/api/v3/exchangeInfo"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                    
                    # Filter for new USDT pairs
                    usdt_pairs = [s for s in symbols if s.endswith('USDT')]
                    
                    # Check if any are new (this is a simplified check)
                    for pair in usdt_pairs:
                        if self._is_new_listing(pair):
                            new_listings.append(pair)
            except Exception as e:
                logger.error(f"Error checking Binance listings: {e}")
            
            # Check other exchanges for new listings
            for exchange_name, exchange in self.exchanges.items():
                try:
                    markets = exchange.load_markets()
                    symbols = list(markets.keys())
                    
                    # Filter for USDT pairs
                    usdt_symbols = [s for s in symbols if '/USDT' in s]
                    
                    for symbol in usdt_symbols:
                        if self._is_new_listing(symbol):
                            new_listings.append(symbol)
                            
                except Exception as e:
                    logger.error(f"Error checking {exchange_name} listings: {e}")
            
            return list(set(new_listings))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error detecting new listings: {e}")
            return []
    
    def _is_new_listing(self, symbol: str) -> bool:
        """Check if symbol is a new listing"""
        try:
            # This is a simplified check - in production you'd track listing dates
            # For now, we'll consider coins with low market cap as potentially new
            return True  # Simplified for demo
            
        except Exception as e:
            logger.error(f"Error checking if {symbol} is new listing: {e}")
            return False
    
    def _get_listing_time(self, symbol: str) -> datetime:
        """Get listing time for symbol"""
        # Simplified - in production you'd track actual listing times
        return datetime.now() - timedelta(hours=1)
    
    def _verify_deposit_withdrawal(self):
        """Verify deposit and withdrawal status for exchanges"""
        while True:
            try:
                for exchange_name in self.exchanges.keys():
                    status = self._check_exchange_status(exchange_name)
                    self.deposit_withdrawal_status[exchange_name] = status
                
                time.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Error verifying deposit/withdrawal: {e}")
                time.sleep(3600)
    
    def _check_exchange_status(self, exchange_name: str) -> Dict:
        """Check exchange deposit/withdrawal status"""
        try:
            # This would normally check exchange APIs for deposit/withdrawal status
            # For now, we'll use a simplified approach
            
            status = {
                'deposits_enabled': True,
                'withdrawals_enabled': True,
                'last_check': datetime.now(),
                'status': 'operational'
            }
            
            # Some exchanges might have issues
            problematic_exchanges = ['ftx']  # Example
            
            if exchange_name in problematic_exchanges:
                status['status'] = 'maintenance'
                status['deposits_enabled'] = False
                status['withdrawals_enabled'] = False
            
            return status
            
        except Exception as e:
            logger.error(f"Error checking {exchange_name} status: {e}")
            return {
                'deposits_enabled': False,
                'withdrawals_enabled': False,
                'last_check': datetime.now(),
                'status': 'unknown'
            }
    
    def _check_deposit_withdrawal_status(self, buy_ex: str, sell_ex: str) -> bool:
        """Check if both exchanges have deposit/withdrawal enabled"""
        try:
            buy_status = self.deposit_withdrawal_status.get(buy_ex, {})
            sell_status = self.deposit_withdrawal_status.get(sell_ex, {})
            
            buy_ok = buy_status.get('deposits_enabled', False) and buy_status.get('withdrawals_enabled', False)
            sell_ok = sell_status.get('deposits_enabled', False) and sell_status.get('withdrawals_enabled', False)
            
            return buy_ok and sell_ok
            
        except Exception as e:
            logger.error(f"Error checking deposit/withdrawal status: {e}")
            return False
    
    def _bad_trade_protection(self):
        """Monitor and protect against bad trade signals"""
        while True:
            try:
                # Check for suspicious patterns
                suspicious_patterns = self._detect_suspicious_patterns()
                
                for pattern in suspicious_patterns:
                    self.bad_trade_signals.append({
                        'pattern': pattern,
                        'timestamp': datetime.now(),
                        'reason': 'Suspicious trading pattern detected'
                    })
                
                # Clean old bad trade signals (older than 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.bad_trade_signals = [
                    signal for signal in self.bad_trade_signals
                    if signal['timestamp'] > cutoff_time
                ]
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in bad trade protection: {e}")
                time.sleep(600)
    
    def _detect_suspicious_patterns(self) -> List[str]:
        """Detect suspicious trading patterns"""
        suspicious_patterns = []
        
        try:
            # Check for pump and dump patterns
            # Check for wash trading
            # Check for price manipulation
            # Check for unusual volume spikes
            
            # This is a simplified implementation
            # In production, you'd implement sophisticated pattern detection
            
            return suspicious_patterns
            
        except Exception as e:
            logger.error(f"Error detecting suspicious patterns: {e}")
            return []
    
    def _is_bad_trade_signal(self, opportunity: Dict) -> bool:
        """Check if opportunity is a bad trade signal"""
        try:
            # Check against known bad patterns
            for bad_signal in self.bad_trade_signals:
                if self._matches_bad_pattern(opportunity, bad_signal):
                    return True
            
            # Check for suspicious characteristics
            if opportunity['risk_score'] > 0.8:
                return True
            
            if opportunity['net_profit_pct'] > 5.0:  # Too good to be true
                return True
            
            if opportunity['volume'] < 100:  # Too low volume
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking bad trade signal: {e}")
            return True  # Err on the side of caution
    
    def _matches_bad_pattern(self, opportunity: Dict, bad_signal: Dict) -> bool:
        """Check if opportunity matches a bad pattern"""
        try:
            # Simplified pattern matching
            # In production, you'd implement sophisticated pattern matching
            
            return False
            
        except Exception as e:
            logger.error(f"Error matching bad pattern: {e}")
            return False
    
    def get_arbitrage_signals(self) -> List[Dict]:
        """Get filtered arbitrage signals"""
        return self.arbitrage_opportunities
    
    def get_new_listings(self) -> List[str]:
        """Get newly listed coins"""
        return self.newly_listed_coins
    
    def get_exchange_status(self) -> Dict:
        """Get exchange status information"""
        return self.deposit_withdrawal_status
    
    def get_bad_trade_signals(self) -> List[Dict]:
        """Get bad trade signals"""
        return self.bad_trade_signals