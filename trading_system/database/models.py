# database/models.py - UPDATED VERSION
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def __enter__(self):
        """Context manager entry"""
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            self.connection.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Stock price data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # Technical indicators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    bb_upper REAL,
                    bb_middle REAL,
                    bb_lower REAL,
                    rsi REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # Trading signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    signal_type TEXT NOT NULL,  -- BUY, SELL, HOLD
                    price REAL,
                    confidence REAL,
                    metadata TEXT,  -- JSON string for additional data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Portfolio positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    stop_loss REAL,
                    target_price REAL,
                    status TEXT DEFAULT 'OPEN',  -- OPEN, CLOSED
                    exit_date TEXT,
                    exit_price REAL,
                    pnl REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS position_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    cost_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    market_value REAL NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    pnl_rate REAL NOT NULL,
                    last_open_time TEXT,
                    account_value REAL,
                    settled_funds REAL,
                    is_fractional INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sync_date, symbol)
                )
            ''')
            
            # Market conditions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    condition TEXT NOT NULL,  -- TRENDING, RANGE_BOUND, HIGH_VOLATILITY
                    vix_level REAL,
                    market_trend TEXT,  -- BULLISH, BEARISH, SIDEWAYS
                    recommended_strategy TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            ''')
            
            conn.commit()
    
    def insert_stock_data(self, symbol: str, data: pd.DataFrame):
        """Insert stock price data"""
        with sqlite3.connect(self.db_path) as conn:
            for index, row in data.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO stock_data 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, index.strftime('%Y-%m-%d'), row['Open'], 
                      row['High'], row['Low'], row['Close'], row['Volume']))
            conn.commit()
    
    def insert_indicators(self, symbol: str, indicators: pd.DataFrame):
        """Insert technical indicators"""
        with sqlite3.connect(self.db_path) as conn:
            for index, row in indicators.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO indicators 
                    (symbol, date, bb_upper, bb_middle, bb_lower, rsi)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, index.strftime('%Y-%m-%d'), 
                      row.get('bb_upper'), row.get('bb_middle'), 
                      row.get('bb_lower'), row.get('rsi')))
            conn.commit()
    
    def get_stock_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """Retrieve stock data for a symbol"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT date, open, high, low, close, volume 
                FROM stock_data 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=(symbol, days))
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                # Sort by date ascending for proper time series
                df = df.sort_index()
            return df
    
    def insert_signal(self, symbol: str, date: str, strategy: str, 
                    signal_type: str, price: float, confidence: float, 
                    metadata: str = None, **kwargs):
        """
        Insert trading signal
        **kwargs allows for extra fields like 'reason' that aren't stored in DB
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO signals 
                (symbol, date, strategy, signal_type, price, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, date, strategy, signal_type, price, confidence, metadata))
            conn.commit()
    
    def insert_market_condition(self, market_condition: dict):
        """Insert market condition analysis"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO market_conditions 
                (date, condition, vix_level, market_trend, recommended_strategy, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                market_condition['date'],
                market_condition['condition'],
                market_condition['vix_level'],
                market_condition['market_trend'],
                market_condition['recommended_strategy'],
                market_condition['confidence']
            ))
            conn.commit()
    
    def get_latest_signals(self, limit: int = 20) -> pd.DataFrame:
        """Get latest trading signals"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT symbol, date, strategy, signal_type, price, confidence, created_at
                FROM signals 
                ORDER BY created_at DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def get_open_positions(self) -> pd.DataFrame:
        """Get all open positions"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM positions 
                WHERE status = 'OPEN'
                ORDER BY entry_date DESC
            '''
            return pd.read_sql_query(query, conn)

# main.py - UPDATED _analyze_market_conditions method
def _analyze_market_conditions(self):
    """Analyze current market conditions"""
    # Get SPY data for market analysis
    spy_data = self.db.get_stock_data('SPY', 100)
    
    if spy_data.empty:
        print("Warning: No SPY data available, using default conditions")
        return self.market_analyzer._default_condition()
    
    # Get VIX data if available (using VXX as proxy)
    vix_data = self.db.get_stock_data('VXX', 50)
    
    market_condition = self.market_analyzer.analyze_market_condition(
        spy_data, vix_data if not vix_data.empty else None)
    
    # Store market condition using the new method
    self.db.insert_market_condition(market_condition)
    
    return market_condition