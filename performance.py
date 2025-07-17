"""
Performance tracking for Crypto Sniper Bot
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Track bot performance and signal accuracy"""
    
    def __init__(self, db_path: str = "bot_performance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT UNIQUE,
                    symbol TEXT,
                    direction TEXT,
                    entry_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    confidence INTEGER,
                    strength TEXT,
                    signals_detected TEXT,
                    timestamp DATETIME,
                    status TEXT DEFAULT 'ACTIVE',
                    exit_price REAL,
                    exit_time DATETIME,
                    profit_loss REAL,
                    duration_minutes INTEGER
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    total_signals INTEGER,
                    successful_signals INTEGER,
                    failed_signals INTEGER,
                    accuracy_percentage REAL,
                    total_profit_loss REAL,
                    avg_profit_loss REAL,
                    max_profit REAL,
                    max_loss REAL,
                    win_rate REAL
                )
            ''')
            
            # Bot statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbols_monitored INTEGER,
                    signals_generated INTEGER,
                    active_signals INTEGER,
                    market_data_points INTEGER,
                    uptime_minutes INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Performance database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def record_signal(self, signal: Dict):
        """Record a new signal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO signals (
                    signal_id, symbol, direction, entry_price, stop_loss, 
                    take_profit, confidence, strength, signals_detected, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['id'],
                signal['symbol'],
                signal['direction'],
                signal['entry_price'],
                signal['stop_loss'],
                signal['take_profit'],
                signal['confidence'],
                signal['strength'],
                json.dumps(signal['signals']),
                signal['timestamp']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Signal recorded: {signal['id']}")
            
        except Exception as e:
            logger.error(f"Error recording signal: {e}")
    
    def update_signal_status(self, signal_id: str, status: str, exit_price: float = None):
        """Update signal status (ACTIVE, CLOSED, CANCELLED)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status == "CLOSED" and exit_price:
                # Calculate profit/loss and duration
                cursor.execute('''
                    SELECT entry_price, timestamp FROM signals 
                    WHERE signal_id = ?
                ''', (signal_id,))
                
                result = cursor.fetchone()
                if result:
                    entry_price, entry_time = result
                    profit_loss = exit_price - entry_price
                    exit_time = datetime.now()
                    duration = (exit_time - datetime.fromisoformat(entry_time)).total_seconds() / 60
                    
                    cursor.execute('''
                        UPDATE signals SET 
                        status = ?, exit_price = ?, exit_time = ?, 
                        profit_loss = ?, duration_minutes = ?
                        WHERE signal_id = ?
                    ''', (status, exit_price, exit_time, profit_loss, duration, signal_id))
                else:
                    cursor.execute('''
                        UPDATE signals SET status = ? WHERE signal_id = ?
                    ''', (status, signal_id))
            else:
                cursor.execute('''
                    UPDATE signals SET status = ? WHERE signal_id = ?
                ''', (status, signal_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Signal {signal_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating signal status: {e}")
    
    def get_performance_stats(self, days: int = 30) -> Dict:
        """Get performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get signals from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_signals,
                    SUM(CASE WHEN status = 'CLOSED' AND profit_loss > 0 THEN 1 ELSE 0 END) as winning_signals,
                    SUM(CASE WHEN status = 'CLOSED' AND profit_loss < 0 THEN 1 ELSE 0 END) as losing_signals,
                    AVG(CASE WHEN status = 'CLOSED' THEN profit_loss ELSE NULL END) as avg_profit_loss,
                    MAX(CASE WHEN status = 'CLOSED' THEN profit_loss ELSE NULL END) as max_profit,
                    MIN(CASE WHEN status = 'CLOSED' THEN profit_loss ELSE NULL END) as max_loss,
                    AVG(CASE WHEN status = 'CLOSED' THEN confidence ELSE NULL END) as avg_confidence
                FROM signals 
                WHERE timestamp >= ?
            ''', (cutoff_date,))
            
            result = cursor.fetchone()
            
            if result:
                total_signals, closed_signals, winning_signals, losing_signals, \
                avg_profit_loss, max_profit, max_loss, avg_confidence = result
                
                # Calculate metrics
                accuracy = (winning_signals / closed_signals * 100) if closed_signals > 0 else 0
                win_rate = (winning_signals / closed_signals * 100) if closed_signals > 0 else 0
                
                stats = {
                    "period_days": days,
                    "total_signals": total_signals or 0,
                    "closed_signals": closed_signals or 0,
                    "winning_signals": winning_signals or 0,
                    "losing_signals": losing_signals or 0,
                    "accuracy_percentage": round(accuracy, 2),
                    "win_rate": round(win_rate, 2),
                    "avg_profit_loss": round(avg_profit_loss or 0, 4),
                    "max_profit": round(max_profit or 0, 4),
                    "max_loss": round(max_loss or 0, 4),
                    "avg_confidence": round(avg_confidence or 0, 1)
                }
            else:
                stats = {
                    "period_days": days,
                    "total_signals": 0,
                    "closed_signals": 0,
                    "winning_signals": 0,
                    "losing_signals": 0,
                    "accuracy_percentage": 0,
                    "win_rate": 0,
                    "avg_profit_loss": 0,
                    "max_profit": 0,
                    "max_loss": 0,
                    "avg_confidence": 0
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def get_signal_history(self, limit: int = 50) -> List[Dict]:
        """Get recent signal history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    signal_id, symbol, direction, entry_price, stop_loss, 
                    take_profit, confidence, strength, status, timestamp,
                    exit_price, profit_loss, duration_minutes
                FROM signals 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            signals = []
            
            for row in results:
                signal = {
                    "signal_id": row[0],
                    "symbol": row[1],
                    "direction": row[2],
                    "entry_price": row[3],
                    "stop_loss": row[4],
                    "take_profit": row[5],
                    "confidence": row[6],
                    "strength": row[7],
                    "status": row[8],
                    "timestamp": row[9],
                    "exit_price": row[10],
                    "profit_loss": row[11],
                    "duration_minutes": row[12]
                }
                signals.append(signal)
            
            conn.close()
            return signals
            
        except Exception as e:
            logger.error(f"Error getting signal history: {e}")
            return []
    
    def get_symbol_performance(self, symbol: str, days: int = 30) -> Dict:
        """Get performance for specific symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_signals,
                    SUM(CASE WHEN status = 'CLOSED' AND profit_loss > 0 THEN 1 ELSE 0 END) as winning_signals,
                    AVG(CASE WHEN status = 'CLOSED' THEN profit_loss ELSE NULL END) as avg_profit_loss,
                    AVG(CASE WHEN status = 'CLOSED' THEN confidence ELSE NULL END) as avg_confidence
                FROM signals 
                WHERE symbol = ? AND timestamp >= ?
            ''', (symbol, cutoff_date))
            
            result = cursor.fetchone()
            
            if result:
                total_signals, closed_signals, winning_signals, avg_profit_loss, avg_confidence = result
                
                accuracy = (winning_signals / closed_signals * 100) if closed_signals > 0 else 0
                
                stats = {
                    "symbol": symbol,
                    "period_days": days,
                    "total_signals": total_signals or 0,
                    "closed_signals": closed_signals or 0,
                    "winning_signals": winning_signals or 0,
                    "accuracy_percentage": round(accuracy, 2),
                    "avg_profit_loss": round(avg_profit_loss or 0, 4),
                    "avg_confidence": round(avg_confidence or 0, 1)
                }
            else:
                stats = {
                    "symbol": symbol,
                    "period_days": days,
                    "total_signals": 0,
                    "closed_signals": 0,
                    "winning_signals": 0,
                    "accuracy_percentage": 0,
                    "avg_profit_loss": 0,
                    "avg_confidence": 0
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting symbol performance: {e}")
            return {}
    
    def record_bot_statistics(self, stats: Dict):
        """Record bot statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bot_statistics (
                    timestamp, symbols_monitored, signals_generated, 
                    active_signals, market_data_points, uptime_minutes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                stats.get('symbols_monitored', 0),
                stats.get('signals_generated', 0),
                stats.get('active_signals', 0),
                stats.get('market_data_points', 0),
                stats.get('uptime_minutes', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording bot statistics: {e}")
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean up old signals
            cursor.execute('DELETE FROM signals WHERE timestamp < ?', (cutoff_date,))
            
            # Clean up old bot statistics
            cursor.execute('DELETE FROM bot_statistics WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

class PerformanceAnalyzer:
    """Analyze performance patterns"""
    
    @staticmethod
    def analyze_signal_patterns(signals: List[Dict]) -> Dict:
        """Analyze signal patterns for optimization"""
        try:
            if not signals:
                return {}
            
            # Analyze by time of day
            hourly_stats = {}
            for signal in signals:
                hour = datetime.fromisoformat(signal['timestamp']).hour
                if hour not in hourly_stats:
                    hourly_stats[hour] = {"total": 0, "successful": 0}
                hourly_stats[hour]["total"] += 1
                if signal.get('profit_loss', 0) > 0:
                    hourly_stats[hour]["successful"] += 1
            
            # Find best performing hours
            best_hours = []
            for hour, stats in hourly_stats.items():
                if stats["total"] >= 5:  # Minimum signals for statistical significance
                    success_rate = (stats["successful"] / stats["total"]) * 100
                    best_hours.append((hour, success_rate))
            
            best_hours.sort(key=lambda x: x[1], reverse=True)
            
            # Analyze by symbol
            symbol_stats = {}
            for signal in signals:
                symbol = signal['symbol']
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {"total": 0, "successful": 0}
                symbol_stats[symbol]["total"] += 1
                if signal.get('profit_loss', 0) > 0:
                    symbol_stats[symbol]["successful"] += 1
            
            # Find best performing symbols
            best_symbols = []
            for symbol, stats in symbol_stats.items():
                if stats["total"] >= 3:  # Minimum signals
                    success_rate = (stats["successful"] / stats["total"]) * 100
                    best_symbols.append((symbol, success_rate))
            
            best_symbols.sort(key=lambda x: x[1], reverse=True)
            
            return {
                "best_hours": best_hours[:5],  # Top 5 hours
                "best_symbols": best_symbols[:5],  # Top 5 symbols
                "total_signals_analyzed": len(signals)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signal patterns: {e}")
            return {}
    
    @staticmethod
    def generate_optimization_suggestions(performance_stats: Dict) -> List[str]:
        """Generate optimization suggestions based on performance"""
        suggestions = []
        
        try:
            accuracy = performance_stats.get('accuracy_percentage', 0)
            win_rate = performance_stats.get('win_rate', 0)
            avg_profit_loss = performance_stats.get('avg_profit_loss', 0)
            
            if accuracy < 60:
                suggestions.append("🔍 Consider increasing minimum confidence threshold")
                suggestions.append("📊 Review signal filtering criteria")
                suggestions.append("⏰ Analyze best performing time periods")
            
            if win_rate < 50:
                suggestions.append("🎯 Focus on higher probability setups")
                suggestions.append("📈 Improve risk-reward ratio requirements")
                suggestions.append("🔄 Review stop-loss and take-profit levels")
            
            if avg_profit_loss < 0:
                suggestions.append("💰 Optimize position sizing")
                suggestions.append("📉 Review market conditions")
                suggestions.append("⚡ Consider faster exit strategies")
            
            if not suggestions:
                suggestions.append("✅ Performance is good! Consider adding more pairs")
                suggestions.append("🚀 System is optimized for current market conditions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return ["❌ Unable to generate suggestions"]