# trading_system/strategies/bollinger_mean_reversion.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import the base strategy classes
from .base_strategy import TradingStrategy, TradingSignal

class BollingerMeanReversionStrategy(TradingStrategy):
    """
    Bollinger Band Mean Reversion Strategy - Refactored
    
    Entry Rules:
    - Buy when price touches lower Bollinger Band AND RSI < 30
    - Sell when price reaches middle Bollinger Band OR stop loss hit
    
    Risk Management:
    - Stop loss at 8% below entry (from config)
    - Position size based on account percentage
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "BollingerMeanReversion"
        
    def get_required_indicators(self) -> List[str]:
        return ['bb_upper', 'bb_lower', 'bb_middle', 'rsi', 'Close', 'Volume']
    
    def get_min_data_points(self) -> int:
        return max(self.config.BB_PERIOD, self.config.RSI_PERIOD)
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[TradingSignal]:
        """
        Generate buy/sell signals based on Bollinger Band mean reversion
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of TradingSignal objects
        """
        # Validate data first
        try:
            self.validate_data(data)
        except ValueError as e:
            # Return empty list if data validation fails
            return []
        
        if len(data) < self.get_min_data_points():
            return []
        
        signals = []
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal
        if self._is_buy_condition(latest, data):
            signal = TradingSignal(
                symbol=symbol,
                signal_type='BUY',
                price=float(latest['Close']),
                confidence=self._calculate_buy_confidence(latest, data),
                strategy=self.name,
                timestamp=latest_date,
                metadata=self._get_buy_metadata(latest, data)
            )
            signals.append(signal)
        
        # Check for sell signal
        if self._is_sell_condition(latest, data):
            signal = TradingSignal(
                symbol=symbol,
                signal_type='SELL',
                price=float(latest['Close']),
                confidence=self._calculate_sell_confidence(latest, data),
                strategy=self.name,
                timestamp=latest_date,
                metadata=self._get_sell_metadata(latest)
            )
            signals.append(signal)
        
        return signals
    
    def _is_buy_condition(self, latest: pd.Series, data: pd.DataFrame) -> bool:
        """Check if buy conditions are met"""
        # Price near or below lower Bollinger Band
        price_condition = latest['Close'] <= latest['bb_lower'] * 1.02  # Within 2%
        
        # RSI oversold
        rsi_condition = latest['rsi'] < self.config.RSI_OVERSOLD
        
        # Volume spike (optional but preferred)
        avg_volume = data['Volume'].tail(10).mean()
        volume_condition = latest['Volume'] > avg_volume * 1.2
        
        # Not already at extreme oversold (avoid falling knife)
        not_extreme = latest['rsi'] > 20  # Don't buy if RSI below 20
        
        return price_condition and rsi_condition and not_extreme
    
    def _is_sell_condition(self, latest: pd.Series, data: pd.DataFrame) -> bool:
        """Check if sell conditions are met"""
        # Price reached middle Bollinger Band (target)
        target_reached = latest['Close'] >= latest['bb_middle']
        
        # RSI overbought
        rsi_overbought = latest['rsi'] > self.config.RSI_OVERBOUGHT
        
        return target_reached or rsi_overbought
    
    def _calculate_buy_confidence(self, latest: pd.Series, data: pd.DataFrame) -> float:
        """Calculate confidence for buy signals"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more oversold conditions
        if latest['rsi'] < 25:
            confidence += 0.2
        elif latest['rsi'] < 30:
            confidence += 0.1
        
        # Bollinger Band position
        bb_position = (latest['Close'] - latest['bb_lower']) / \
                     (latest['bb_upper'] - latest['bb_lower'])
        if bb_position < 0.1:  # Very close to lower band
            confidence += 0.3
        elif bb_position < 0.2:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_sell_confidence(self, latest: pd.Series, data: pd.DataFrame) -> float:
        """Calculate confidence for sell signals"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for overbought conditions
        if latest['rsi'] > 75:
            confidence += 0.3
        elif latest['rsi'] > 70:
            confidence += 0.2
        
        # Price relative to middle band
        if latest['Close'] >= latest['bb_middle']:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_buy_metadata(self, latest: pd.Series, data: pd.DataFrame) -> Dict:
        """Generate metadata for buy signals"""
        return {
            'bb_position': float((latest['Close'] - latest['bb_lower']) / 
                               (latest['bb_upper'] - latest['bb_lower'])),
            'rsi': float(latest['rsi']),
            'stop_loss': float(latest['Close'] * (1 - self.config.PERSONAL_STOP_LOSS)),
            'target': float(latest['bb_middle']),
            'strategy_logic': 'mean_reversion_oversold'
        }
    
    def _get_sell_metadata(self, latest: pd.Series) -> Dict:
        """Generate metadata for sell signals"""
        return {
            'reason': 'target_reached' if latest['Close'] >= latest['bb_middle'] else 'overbought',
            'strategy_logic': 'mean_reversion_exit'
        }