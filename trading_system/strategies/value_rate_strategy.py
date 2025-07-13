# strategies/value_rate_strategy.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import the base strategy classes
from .base_strategy import TradingStrategy, TradingSignal

class ValueRateStrategy(TradingStrategy):
    """
    Value Rate Strategy - Rate-Sensitive Value Plays
    
    Entry Rules:
    - Buy undervalued stocks in rate-sensitive sectors
    - Focus on dividend aristocrats and value metrics
    - Target stocks benefiting from rate environment
    
    Exit Rules:
    - Sell when valuation becomes stretched
    - Rate environment changes unfavorably
    - Dividend cuts or fundamental deterioration
    
    Risk Management:
    - Focus on quality metrics (low debt, stable earnings)
    - Dividend yield and coverage analysis
    - Interest rate sensitivity monitoring
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "ValueRate"
        
        # Value-specific parameters
        self.MIN_DIVIDEND_YIELD = 0.02  # 2% minimum dividend yield
        self.MAX_PE_RATIO = 20  # Maximum P/E ratio for value consideration
        self.MIN_MOMENTUM = -0.10  # Allow some negative momentum for value
        self.RATE_SENSITIVITY_THRESHOLD = 0.05  # 5% rate sensitivity
        
        # Value sectors that benefit from certain rate environments
        self.RATE_SENSITIVE_VALUE = [
            # Banks and Financials (benefit from rising rates)
            'JPM', 'BAC', 'WFC', 'USB', 'PNC',
            # Utilities (hurt by rising rates but often oversold)
            'SO', 'D', 'DUK', 'AEP', 'EXC',
            # REITs (rate sensitive but value opportunities)
            'O', 'PLD', 'SPG', 'EXR',
            # Value ETFs
            'VTV', 'IWD', 'SCHD'
        ]
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals for value rate plays
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Only process rate-sensitive value stocks
        if not self._is_rate_sensitive_value(symbol):
            return signals
        
        if len(data) < 60:  # Need longer history for value analysis
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal (value opportunity)
        buy_signal = self._check_value_buy_signal(latest, data, symbol)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'value_rate_opportunity',
                'metadata': json.dumps({
                    'value_score': self._calculate_value_score(data, symbol),
                    'rate_environment': self._assess_rate_environment(),
                    'sector_type': self._get_value_sector_type(symbol),
                    'dividend_appeal': self._assess_dividend_appeal(symbol, latest['Close']),
                    'oversold_level': latest.get('rsi', 50),
                    'stop_loss': latest['Close'] * (1 - self.config.PERSONAL_STOP_LOSS),
                    'strategy_logic': 'value_rate_entry'
                })
            })
        
        # Check for sell signal (value deterioration)
        sell_signal = self._check_value_sell_signal(latest, data, symbol)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'value_deterioration_or_rate_risk',
                'metadata': json.dumps({
                    'overvalued': self._is_overvalued(data, symbol),
                    'rate_headwind': True
                })
            })
        
        return signals
    
    def _is_rate_sensitive_value(self, symbol: str) -> bool:
        """Check if symbol is a rate-sensitive value play"""
        return symbol in self.RATE_SENSITIVE_VALUE
    
    def _get_value_sector_type(self, symbol: str) -> str:
        """Categorize the value sector type"""
        if symbol in ['JPM', 'BAC', 'WFC', 'USB', 'PNC']:
            return 'financials'
        elif symbol in ['SO', 'D', 'DUK', 'AEP', 'EXC']:
            return 'utilities'
        elif symbol in ['O', 'PLD', 'SPG', 'EXR']:
            return 'reits'
        elif symbol in ['VTV', 'IWD', 'SCHD']:
            return 'value_etf'
        else:
            return 'other_value'
    
    def _assess_rate_environment(self) -> str:
        """Assess current interest rate environment (simplified)"""
        # In production, would use actual rate data (10Y, Fed Funds, etc.)
        # For now, return a simplified assessment
        return 'neutral'  # Could be 'rising', 'falling', 'neutral'
    
    def _estimate_dividend_yield(self, symbol: str, price: float) -> float:
        """Estimate dividend yield (simplified calculation)"""
        # Known dividend yields for some symbols (simplified)
        estimated_yields = {
            'JPM': 0.025,   # 2.5%
            'USB': 0.038,   # 3.8%
            'SO': 0.042,    # 4.2%
            'D': 0.039,     # 3.9%
            'O': 0.045,     # 4.5%
            'SCHD': 0.035,  # 3.5%
            'VTV': 0.022,   # 2.2%
        }
        return estimated_yields.get(symbol, 0.025)  # Default 2.5%
    
    def _assess_dividend_appeal(self, symbol: str, price: float) -> Dict:
        """Assess dividend attractiveness"""
        estimated_yield = self._estimate_dividend_yield(symbol, price)
        
        return {
            'estimated_yield': estimated_yield,
            'above_minimum': estimated_yield >= self.MIN_DIVIDEND_YIELD,
            'attractive': estimated_yield >= 0.035,  # 3.5%+ considered attractive
            'sector_type': self._get_value_sector_type(symbol)
        }
    
    def _calculate_value_score(self, data: pd.DataFrame, symbol: str) -> float:
        """Calculate comprehensive value score"""
        # Price momentum (value stocks can have negative momentum)
        momentum_60d = self._calculate_momentum(data, 60)
        momentum_score = 1.0 if momentum_60d > self.MIN_MOMENTUM else 0.5
        
        # RSI oversold condition
        latest_rsi = data.iloc[-1].get('rsi', 50)
        rsi_score = 1.5 if latest_rsi < 35 else (1.2 if latest_rsi < 45 else 1.0)
        
        # Price vs moving averages (value typically below long-term averages)
        current_price = data.iloc[-1]['Close']
        if len(data) >= 200:
            ma_200 = data['Close'].tail(200).mean()
            ma_score = 1.3 if current_price < ma_200 * 0.95 else 1.0  # 5% below 200-day MA
        else:
            ma_score = 1.0
        
        # Dividend yield component
        dividend_appeal = self._assess_dividend_appeal(symbol, current_price)
        dividend_score = 1.3 if dividend_appeal['attractive'] else 1.1
        
        # Sector-specific adjustments
        sector_type = self._get_value_sector_type(symbol)
        sector_score = 1.0
        if sector_type == 'financials':
            # Banks benefit from rising rates
            rate_env = self._assess_rate_environment()
            sector_score = 1.2 if rate_env == 'rising' else 1.0
        elif sector_type == 'utilities':
            # Utilities hurt by rising rates but often oversold
            sector_score = 1.1 if latest_rsi < 40 else 0.9
        
        # Combined value score
        value_score = (momentum_score * rsi_score * ma_score * 
                      dividend_score * sector_score) / 5.0
        
        return value_score
    
    def _calculate_momentum(self, data: pd.DataFrame, period: int) -> float:
        """Calculate momentum over specified period"""
        if len(data) < period:
            return 0.0
        
        start_price = data.iloc[-period]['Close']
        current_price = data.iloc[-1]['Close']
        
        return (current_price / start_price) - 1.0
    
    def _is_overvalued(self, data: pd.DataFrame, symbol: str) -> bool:
        """Check if stock appears overvalued (simplified)"""
        # Use price momentum and RSI as proxies for overvaluation
        current_rsi = data.iloc[-1].get('rsi', 50)
        momentum_30d = self._calculate_momentum(data, 30)
        
        # Consider overvalued if RSI > 75 and strong recent momentum
        return current_rsi > 75 and momentum_30d > 0.15
    
    def _check_value_buy_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for value buy opportunity"""
        # High value score
        value_score = self._calculate_value_score(data, symbol)
        value_condition = value_score > 1.1
        
        # Oversold but not extreme
        rsi_condition = 25 <= latest.get('rsi', 50) <= 45  # Oversold but not falling knife
        
        # Dividend yield requirement
        dividend_appeal = self._assess_dividend_appeal(symbol, latest['Close'])
        dividend_condition = dividend_appeal['above_minimum']
        
        # Not in severe downtrend
        momentum_60d = self._calculate_momentum(data, 60)
        momentum_condition = momentum_60d > self.MIN_MOMENTUM
        
        # Volume not collapsing
        avg_volume = data['Volume'].tail(20).mean()
        volume_condition = latest['Volume'] > avg_volume * 0.5
        
        # Rate environment favorable or neutral
        rate_env = self._assess_rate_environment()
        sector_type = self._get_value_sector_type(symbol)
        
        rate_condition = True
        if sector_type == 'utilities' and rate_env == 'rising':
            rate_condition = latest.get('rsi', 50) < 35  # Only if very oversold
        elif sector_type == 'reits' and rate_env == 'rising':
            rate_condition = latest.get('rsi', 50) < 40  # Only if oversold
        
        return (value_condition and rsi_condition and dividend_condition and 
                momentum_condition and rate_condition)
    
    def _check_value_sell_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for value sell signal"""
        # Overvaluation
        overvalued = self._is_overvalued(data, symbol)
        
        # RSI overbought for value stock
        rsi_overbought = latest.get('rsi', 50) > 70
        
        # Strong momentum (value realized)
        momentum_30d = self._calculate_momentum(data, 30)
        momentum_exit = momentum_30d > 0.20  # 20% gain might be time to take profits
        
        # Rate environment turns unfavorable
        rate_env = self._assess_rate_environment()
        sector_type = self._get_value_sector_type(symbol)
        
        rate_headwind = False
        if sector_type == 'utilities' and rate_env == 'rising':
            rate_headwind = momentum_30d < 0.05  # Rising rates + weak performance
        elif sector_type == 'reits' and rate_env == 'rising':
            rate_headwind = momentum_30d < 0.03
        
        return overvalued or rsi_overbought or momentum_exit or rate_headwind
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.55  # Base confidence for value plays
        
        value_score = self._calculate_value_score(data, symbol)
        rsi = latest.get('rsi', 50)
        dividend_appeal = self._assess_dividend_appeal(symbol, latest['Close'])
        
        if signal_type == 'BUY':
            # High value score
            if value_score > 1.3:
                confidence += 0.25
            elif value_score > 1.2:
                confidence += 0.15
            
            # Strong oversold condition
            if rsi < 30:
                confidence += 0.2
            elif rsi < 40:
                confidence += 0.1
            
            # Attractive dividend yield
            if dividend_appeal['attractive']:
                confidence += 0.15
            elif dividend_appeal['above_minimum']:
                confidence += 0.1
            
            # Sector-specific confidence
            sector_type = self._get_value_sector_type(symbol)
            if sector_type == 'financials':
                rate_env = self._assess_rate_environment()
                if rate_env == 'rising':
                    confidence += 0.1
            elif sector_type == 'value_etf':
                confidence += 0.05  # ETFs are diversified
        
        elif signal_type == 'SELL':
            # Clear overvaluation
            if self._is_overvalued(data, symbol):
                confidence += 0.3
            
            # Overbought condition
            if rsi > 75:
                confidence += 0.2
            elif rsi > 70:
                confidence += 0.1
            
            # Strong momentum (profits taken)
            momentum_30d = self._calculate_momentum(data, 30)
            if momentum_30d > 0.25:
                confidence += 0.2
            elif momentum_30d > 0.15:
                confidence += 0.1
        
        return min(confidence, 1.0)
    