# strategies/bollinger_mean_reversion.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class BollingerMeanReversionStrategy:
    """
    Bollinger Band Mean Reversion Strategy
    
    Entry Rules:
    - Buy when price touches lower Bollinger Band AND RSI < 30
    - Sell when price reaches middle Bollinger Band OR stop loss hit
    
    Risk Management:
    - Stop loss at 5% below entry
    - Position size based on account percentage
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "BollingerMeanReversion"
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals based on Bollinger Band mean reversion
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        if len(data) < self.config.BB_PERIOD:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal
        buy_signal = self._check_buy_signal(latest, data)
        if buy_signal:
            confidence = self._calculate_confidence(latest, 'BUY')
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'metadata': json.dumps({
                    'bb_position': (latest['Close'] - latest['bb_lower']) / 
                                  (latest['bb_upper'] - latest['bb_lower']),
                    'rsi': latest['rsi'],
                    'stop_loss': latest['Close'] * (1 - self.config.STOP_LOSS_PERCENT),
                    'target': latest['bb_middle']
                })
            })
        
        # Check for sell signal (if we have an open position)
        sell_signal = self._check_sell_signal(latest, data)
        if sell_signal:
            confidence = self._calculate_confidence(latest, 'SELL')
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'metadata': json.dumps({
                    'reason': 'target_reached' if latest['Close'] >= latest['bb_middle'] else 'other'
                })
            })
        
        return signals
    
    def _check_buy_signal(self, latest: pd.Series, data: pd.DataFrame) -> bool:
        """Check if current conditions meet buy criteria"""
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
    
    def _check_sell_signal(self, latest: pd.Series, data: pd.DataFrame) -> bool:
        """Check if current conditions meet sell criteria"""
        # Price reached middle Bollinger Band (target)
        target_reached = latest['Close'] >= latest['bb_middle']
        
        # RSI overbought
        rsi_overbought = latest['rsi'] > self.config.RSI_OVERBOUGHT
        
        return target_reached or rsi_overbought
    
    def _calculate_confidence(self, latest: pd.Series, signal_type: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.5  # Base confidence
        
        if signal_type == 'BUY':
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
        
        elif signal_type == 'SELL':
            # Higher confidence for overbought conditions
            if latest['rsi'] > 75:
                confidence += 0.3
            elif latest['rsi'] > 70:
                confidence += 0.2
            
            # Price relative to middle band
            if latest['Close'] >= latest['bb_middle']:
                confidence += 0.3
        
        return min(confidence, 1.0)
    