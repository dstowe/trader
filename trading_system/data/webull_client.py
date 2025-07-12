# data/webull_client.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

class DataFetcher:
    """
    Data fetcher using yfinance as primary source
    Can be extended to use Webull API when available
    """
    
    def __init__(self):
        self.session = None
    
    def fetch_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """
        Fetch stock data using yfinance
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                print(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Ensure we have the expected columns
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_columns:
                if col not in data.columns:
                    print(f"Missing column {col} for {symbol}")
                    return pd.DataFrame()
            
            return data[expected_columns]
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, symbols: List[str], 
                            period: str = "3mo") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks"""
        results = {}
        
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            data = self.fetch_stock_data(symbol, period)
            if not data.empty:
                results[symbol] = data
            time.sleep(0.1)  # Rate limiting
        
        return results
    
    def get_current_price(self, symbol: str) -> float:
        """Get current/latest price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('regularMarketPrice', info.get('previousClose', 0))
        except:
            return 0