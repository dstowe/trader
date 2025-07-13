# strategies/international_strategy.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import the base strategy classes
from .base_strategy import TradingStrategy, TradingSignal

class InternationalStrategy(TradingStrategy):
    """
    International Strategy - Capitalize on International Outperformance
    
    Entry Rules:
    - Buy international ETFs when showing relative strength vs domestic
    - Focus on currency-unhedged ETFs in weak USD environment
    - Use momentum and relative performance indicators
    
    Exit Rules:
    - Sell when relative performance deteriorates
    - Currency hedging considerations based on DXY
    
    Risk Management:
    - Max 30% international allocation
    - Stop loss at 8% below entry
    - Monitor currency exposure
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "International"
        
        # International-specific thresholds
        self.MIN_RELATIVE_STRENGTH = 1.05  # 5% outperformance vs SPY
        self.MOMENTUM_PERIOD = 20  # 20-day momentum
        self.RELATIVE_STRENGTH_PERIOD = 60  # 60-day relative performance
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals for international ETFs
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: ETF symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Only process international ETFs
        if not self._is_international_etf(symbol):
            return signals
        
        if len(data) < self.RELATIVE_STRENGTH_PERIOD:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal
        buy_signal = self._check_buy_signal(latest, data, symbol)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'international_outperformance',
                'metadata': json.dumps({
                    'relative_strength': self._calculate_relative_strength(data),
                    'momentum_20d': self._calculate_momentum(data, 20),
                    'currency_hedged': self._is_currency_hedged(symbol),
                    'stop_loss': latest['Close'] * (1 - self.config.PERSONAL_STOP_LOSS),
                    'strategy_logic': 'international_momentum'
                })
            })
        
        # Check for sell signal
        sell_signal = self._check_sell_signal(latest, data, symbol)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'relative_weakness',
                'metadata': json.dumps({
                    'relative_strength': self._calculate_relative_strength(data),
                    'momentum_deterioration': True
                })
            })
        
        return signals
    
    def _is_international_etf(self, symbol: str) -> bool:
        """Check if symbol is an international ETF"""
        international_etfs = [
            'VEA', 'EFA', 'VXUS', 'IEFA', 'HEFA', 'HEDJ',
            'VGK', 'EWJ', 'EEMA', 'VWO', 'EWG', 'EWU', 'EWY', 'INDA'
        ]
        return symbol in international_etfs
    
    def _is_currency_hedged(self, symbol: str) -> bool:
        """Check if ETF is currency hedged"""
        hedged_etfs = ['HEFA', 'HEDJ']
        return symbol in hedged_etfs
    
    def _calculate_relative_strength(self, data: pd.DataFrame) -> float:
        """Calculate relative strength vs SPY over period"""
        if len(data) < self.RELATIVE_STRENGTH_PERIOD:
            return 1.0
        
        # Calculate performance over period
        period_start = data.iloc[-self.RELATIVE_STRENGTH_PERIOD]['Close']
        current_price = data.iloc[-1]['Close']
        etf_performance = current_price / period_start
        
        # For simplicity, assume SPY performance of 1.0 (would need real SPY data)
        # In production, you'd fetch SPY data and calculate actual relative performance
        spy_performance = 1.02  # Assume 2% SPY performance as baseline
        
        return etf_performance / spy_performance
    
    def _calculate_momentum(self, data: pd.DataFrame, period: int) -> float:
        """Calculate price momentum over specified period"""
        if len(data) < period:
            return 0.0
        
        start_price = data.iloc[-period]['Close']
        current_price = data.iloc[-1]['Close']
        
        return (current_price / start_price) - 1.0
    
    def _check_buy_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check if current conditions meet buy criteria"""
        # Relative strength vs domestic markets
        relative_strength = self._calculate_relative_strength(data)
        strength_condition = relative_strength >= self.MIN_RELATIVE_STRENGTH
        
        # Positive momentum
        momentum_20d = self._calculate_momentum(data, self.MOMENTUM_PERIOD)
        momentum_condition = momentum_20d > 0.02  # 2% positive momentum
        
        # Volume confirmation
        avg_volume = data['Volume'].tail(10).mean()
        volume_condition = latest['Volume'] > avg_volume * 0.8  # Not requiring volume spike for ETFs
        
        # RSI not overbought
        rsi_condition = latest.get('rsi', 50) < 75
        
        # Currency consideration - prefer unhedged in weak USD
        currency_preference = True
        if hasattr(self.config, 'PREFER_CURRENCY_HEDGED'):
            is_hedged = self._is_currency_hedged(symbol)
            if self.config.PREFER_CURRENCY_HEDGED:
                currency_preference = is_hedged
            else:
                currency_preference = not is_hedged
        
        return (strength_condition and momentum_condition and 
                rsi_condition and currency_preference)
    
    def _check_sell_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check if current conditions meet sell criteria"""
        # Relative strength deterioration
        relative_strength = self._calculate_relative_strength(data)
        weakness_condition = relative_strength < 0.98  # 2% underperformance
        
        # Negative momentum
        momentum_20d = self._calculate_momentum(data, self.MOMENTUM_PERIOD)
        momentum_deterioration = momentum_20d < -0.03  # 3% negative momentum
        
        # Overbought RSI
        rsi_overbought = latest.get('rsi', 50) > 80
        
        return weakness_condition or momentum_deterioration or rsi_overbought
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.6  # Base confidence for international
        
        relative_strength = self._calculate_relative_strength(data)
        momentum_20d = self._calculate_momentum(data, self.MOMENTUM_PERIOD)
        
        if signal_type == 'BUY':
            # Higher confidence for stronger relative performance
            if relative_strength > 1.10:  # 10% outperformance
                confidence += 0.3
            elif relative_strength > 1.05:  # 5% outperformance
                confidence += 0.2
            
            # Momentum confirmation
            if momentum_20d > 0.05:  # 5% momentum
                confidence += 0.2
            elif momentum_20d > 0.02:
                confidence += 0.1
            
            # Currency alignment bonus
            is_hedged = self._is_currency_hedged(symbol)
            if hasattr(self.config, 'PREFER_CURRENCY_HEDGED'):
                if (self.config.PREFER_CURRENCY_HEDGED and is_hedged) or \
                   (not self.config.PREFER_CURRENCY_HEDGED and not is_hedged):
                    confidence += 0.1
        
        elif signal_type == 'SELL':
            # Higher confidence for clear weakness
            if relative_strength < 0.95:  # 5% underperformance
                confidence += 0.3
            elif relative_strength < 0.98:
                confidence += 0.2
            
            # Momentum deterioration
            if momentum_20d < -0.05:
                confidence += 0.2
        
        return min(confidence, 1.0)
    