# strategies/microstructure_breakout.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class MicrostructureBreakoutStrategy:
    """
    Microstructure Breakout Strategy - Precise Breakout Patterns
    
    Entry Rules:
    - Buy on confirmed breakouts with tight bid-ask spreads
    - Focus on high-volume, liquid securities
    - Use ATR for dynamic stop placement
    
    Exit Rules:
    - ATR-based trailing stops
    - Volume exhaustion signals
    - Support/resistance level exits
    
    Risk Management:
    - Only trade high-volume securities (>1M daily)
    - Tight stops using ATR multiples
    - Quick exits on volume decline
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "MicrostructureBreakout"
        
        # Microstructure-specific parameters
        self.MIN_DAILY_VOLUME = 1_000_000  # 1M minimum daily volume
        self.ATR_MULTIPLIER = 2.0  # ATR multiplier for stops
        self.BREAKOUT_LOOKBACK = 20  # 20-day breakout period
        self.VOLUME_SPIKE_THRESHOLD = 1.5  # 50% above average volume
        self.TIGHT_SPREAD_THRESHOLD = 0.01  # 1% max spread (estimated)
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals for microstructure breakouts
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Only process high-volume securities
        if not self._is_high_volume_security(data, symbol):
            return signals
        
        if len(data) < self.BREAKOUT_LOOKBACK:
            return signals
        
        # Calculate ATR if not present
        if 'atr' not in data.columns:
            data = self._calculate_atr(data)
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal (breakout)
        buy_signal = self._check_breakout_buy_signal(latest, data, symbol)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol)
            atr_stop = latest['Close'] - (latest.get('atr', latest['Close'] * 0.02) * self.ATR_MULTIPLIER)
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'microstructure_breakout',
                'metadata': json.dumps({
                    'breakout_level': self._get_breakout_level(data),
                    'volume_spike': self._get_volume_ratio(data),
                    'atr': latest.get('atr', 0),
                    'atr_stop': atr_stop,
                    'spread_quality': self._estimate_spread_quality(symbol),
                    'stop_loss': atr_stop,
                    'strategy_logic': 'microstructure_breakout'
                })
            })
        
        # Check for sell signal
        sell_signal = self._check_breakout_sell_signal(latest, data, symbol)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'breakout_exhaustion_or_reversal',
                'metadata': json.dumps({
                    'volume_exhaustion': self._check_volume_exhaustion(data),
                    'support_break': self._check_support_break(data)
                })
            })
        
        return signals
    
    def _is_high_volume_security(self, data: pd.DataFrame, symbol: str) -> bool:
        """Check if security meets volume requirements"""
        # Check recent average volume
        if len(data) < 10:
            return False
        
        avg_volume = data['Volume'].tail(10).mean()
        
        # Also check if it's in our high-volume universe
        high_volume_universe = [
            # Major ETFs (tight spreads)
            'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
            # Large Cap Tech (tight spreads)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
            # High volume names
            'AMD', 'INTC', 'NFLX', 'CRM', 'ORCL'
        ]
        
        return avg_volume >= self.MIN_DAILY_VOLUME or symbol in high_volume_universe
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        
        data = data.copy()
        data['atr'] = atr
        return data
    
    def _estimate_spread_quality(self, symbol: str) -> str:
        """Estimate bid-ask spread quality based on symbol type"""
        # Major ETFs and large caps have tight spreads
        tight_spread_symbols = [
            'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV',
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'
        ]
        
        if symbol in tight_spread_symbols:
            return 'tight'
        else:
            return 'moderate'
    
    def _get_breakout_level(self, data: pd.DataFrame) -> float:
        """Get the breakout resistance level"""
        if len(data) < self.BREAKOUT_LOOKBACK:
            return float(data['High'].iloc[-1])
        
        # 20-day high as resistance level
        resistance = data['High'].tail(self.BREAKOUT_LOOKBACK).max()
        return float(resistance)
    
    def _get_volume_ratio(self, data: pd.DataFrame) -> float:
        """Get current volume vs average volume ratio"""
        if len(data) < 10:
            return 1.0
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(10).mean()
        
        return float(current_volume / avg_volume if avg_volume > 0 else 1.0)
    
    def _check_breakout_buy_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for breakout buy conditions"""
        # Price breakout above resistance
        resistance_level = self._get_breakout_level(data)
        breakout_condition = latest['Close'] > resistance_level
        
        # Volume confirmation
        volume_ratio = self._get_volume_ratio(data)
        volume_condition = volume_ratio >= self.VOLUME_SPIKE_THRESHOLD
        
        # ATR-based momentum
        atr = latest.get('atr', latest['Close'] * 0.02)
        momentum_condition = (latest['Close'] - data['Close'].iloc[-2]) > (atr * 0.5)
        
        # RSI not extremely overbought
        rsi_condition = latest.get('rsi', 50) < 80
        
        # Not a gap up (prefer sustained breakouts)
        gap_condition = (latest['Open'] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] < 0.02
        
        return (breakout_condition and volume_condition and 
                momentum_condition and rsi_condition and gap_condition)
    
    def _check_breakout_sell_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for breakout sell conditions"""
        # Volume exhaustion
        volume_exhaustion = self._check_volume_exhaustion(data)
        
        # Support level break
        support_break = self._check_support_break(data)
        
        # ATR-based stop loss
        atr = latest.get('atr', latest['Close'] * 0.02)
        atr_stop_hit = False
        if len(data) >= 2:
            entry_price = data['Close'].iloc[-2]  # Assume entry was previous day
            stop_level = entry_price - (atr * self.ATR_MULTIPLIER)
            atr_stop_hit = latest['Close'] <= stop_level
        
        # Overbought reversal
        rsi_reversal = latest.get('rsi', 50) > 85
        
        return volume_exhaustion or support_break or atr_stop_hit or rsi_reversal
    
    def _check_volume_exhaustion(self, data: pd.DataFrame) -> bool:
        """Check for volume exhaustion pattern"""
        if len(data) < 5:
            return False
        
        # Look for declining volume on recent bars
        recent_volumes = data['Volume'].tail(3).values
        
        # Volume declining over last 3 bars
        if len(recent_volumes) >= 3:
            return recent_volumes[2] < recent_volumes[1] < recent_volumes[0]
        
        return False
    
    def _check_support_break(self, data: pd.DataFrame) -> bool:
        """Check if price broke below support level"""
        if len(data) < self.BREAKOUT_LOOKBACK:
            return False
        
        # Recent low as support
        support_level = data['Low'].tail(10).min()
        current_price = data['Close'].iloc[-1]
        
        return current_price < support_level
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.65  # Base confidence for microstructure plays
        
        volume_ratio = self._get_volume_ratio(data)
        spread_quality = self._estimate_spread_quality(symbol)
        
        if signal_type == 'BUY':
            # Volume spike confidence
            if volume_ratio > 2.0:  # 2x volume
                confidence += 0.25
            elif volume_ratio > 1.5:
                confidence += 0.15
            
            # Spread quality bonus
            if spread_quality == 'tight':
                confidence += 0.1
            
            # Clean breakout (not too extended)
            resistance = self._get_breakout_level(data)
            breakout_extension = (latest['Close'] - resistance) / resistance
            if breakout_extension < 0.02:  # Less than 2% above resistance
                confidence += 0.1
            
            # ATR-based momentum
            atr = latest.get('atr', latest['Close'] * 0.02)
            if len(data) >= 2:
                price_move = latest['Close'] - data['Close'].iloc[-2]
                if price_move > atr * 0.75:  # Strong ATR-based move
                    confidence += 0.1
        
        elif signal_type == 'SELL':
            # Clear reversal signals
            if self._check_volume_exhaustion(data):
                confidence += 0.2
            
            if self._check_support_break(data):
                confidence += 0.3
            
            # RSI extreme readings
            rsi = latest.get('rsi', 50)
            if rsi > 85:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def calculate_position_size(self, account_value: float, price: float) -> int:
        """Calculate position size for microstructure breakout plays"""
        # Standard position sizing
        max_position_value = account_value * getattr(self.config, 'MAX_POSITION_VALUE_PERCENT', 0.1)
        
        shares = int(max_position_value / price)
        return max(shares, 1) if shares > 0 else 0