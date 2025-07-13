# strategies/gap_trading.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, time
import json

class GapTradingStrategy:
    """
    Gap Trading Strategy for volatile morning moves
    
    Strategy Types:
    1. Gap Fade: Trade against the gap (mean reversion)
    2. Gap Continuation: Trade with the gap (momentum)
    3. Gap Range: Trade range after partial fill
    
    Entry Rules:
    - Gap > 1% with volume confirmation
    - Time window: First 60 minutes of trading
    - Quality classification system
    
    Risk Management:
    - Tight stops (1.5x normal)
    - Time-based exits (60 minute max)
    - Position sizing based on gap volatility
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "GapTrading"
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate gap trading signals
        
        Args:
            data: DataFrame with OHLCV and gap indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        if len(data) < 2:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check if there's a significant gap today
        if not self._has_significant_gap(latest):
            return signals
        
        # Classify the gap
        gap_classification = self._classify_gap(latest)
        
        # Only trade high quality gaps
        if gap_classification['quality'] not in ['HIGH', 'MEDIUM']:
            return signals
        
        # Check trading time window (first 60 minutes)
        if not self._is_in_trading_window():
            return signals
        
        # Generate appropriate signal based on gap characteristics
        signal = self._determine_gap_strategy(latest, gap_classification, data)
        
        if signal:
            signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close'],
            })
            signals.append(signal)
        
        return signals
    
    def _has_significant_gap(self, latest: pd.Series) -> bool:
        """Check if there's a significant gap worth trading"""
        return (hasattr(latest, 'gap_size') and 
                latest['gap_size'] >= self.config.GAP_MIN_SIZE and
                hasattr(latest, 'volume_ratio') and
                latest['volume_ratio'] >= self.config.GAP_VOLUME_MULTIPLIER)
    
    def _classify_gap(self, latest: pd.Series) -> Dict:
        """Classify gap quality and characteristics"""
        gap_percent = latest.get('gap_percent', 0)
        volume_ratio = latest.get('volume_ratio', 1.0)
        
        # Import the classification function from indicators
        from indicators.technical import TechnicalIndicators
        return TechnicalIndicators.classify_gap(gap_percent, volume_ratio)
    
    def _is_in_trading_window(self) -> bool:
        """Check if we're in the gap trading time window (first 60 minutes)"""
        current_time = datetime.now().time()
        market_open = time(9, 30)  # 9:30 AM
        gap_window_close = time(10, 30)  # 10:30 AM
        
        return market_open <= current_time <= gap_window_close
    
    def _determine_gap_strategy(self, latest: pd.Series, gap_classification: Dict, 
                               data: pd.DataFrame) -> Optional[Dict]:
        """Determine which gap strategy to use based on conditions"""
        
        gap_size = gap_classification['gap_size']
        gap_direction = gap_classification['direction']
        quality = gap_classification['quality']
        
        # Strategy selection logic
        if gap_size >= self.config.GAP_LARGE_SIZE:
            # Large gaps: Usually fade (mean reversion)
            return self._gap_fade_signal(latest, gap_classification, data)
        
        elif gap_size >= self.config.GAP_MIN_SIZE:
            # Medium gaps: Check for continuation vs fade
            if self._should_fade_gap(latest, data):
                return self._gap_fade_signal(latest, gap_classification, data)
            else:
                return self._gap_continuation_signal(latest, gap_classification, data)
        
        return None
    
    def _should_fade_gap(self, latest: pd.Series, data: pd.DataFrame) -> bool:
        """Determine if gap should be faded based on technical conditions"""
        
        # Check if price is already pulling back toward gap
        if len(data) >= 3:
            recent_high = data['High'].tail(3).max()
            recent_low = data['Low'].tail(3).min()
            current_price = latest['Close']
            
            if latest['gap_direction'] == 'UP':
                # Gap up: fade if price is coming down from highs
                return current_price < recent_high * 0.98
            else:
                # Gap down: fade if price is bouncing from lows
                return current_price > recent_low * 1.02
        
        # Default to continuation for newer gaps
        return False
    
    def _gap_fade_signal(self, latest: pd.Series, gap_classification: Dict, 
                        data: pd.DataFrame) -> Dict:
        """Generate gap fade (mean reversion) signal"""
        
        gap_direction = gap_classification['direction']
        gap_percent = gap_classification['gap_percent']
        prev_close = latest['Close'] / (1 + gap_percent)  # Approximate previous close
        
        if gap_direction == 'UP':
            # Gap up: Short/sell signal (expecting gap fill)
            signal_type = 'SELL'
            target_price = prev_close  # Target gap fill
            stop_price = latest['Close'] * (1 + self.config.GAP_MAX_RISK)
        else:
            # Gap down: Long/buy signal (expecting gap fill)
            signal_type = 'BUY'
            target_price = prev_close  # Target gap fill
            stop_price = latest['Close'] * (1 - self.config.GAP_MAX_RISK)
        
        confidence = self._calculate_fade_confidence(latest, gap_classification)
        
        return {
            'signal_type': signal_type,
            'confidence': confidence,
            'gap_strategy': 'FADE',
            'metadata': json.dumps({
                'gap_size': gap_classification['gap_size'],
                'gap_direction': gap_direction,
                'target_price': target_price,
                'stop_price': stop_price,
                'volume_ratio': gap_classification['volume_ratio'],
                'quality': gap_classification['quality'],
                'strategy_logic': 'gap_fade_mean_reversion'
            })
        }
    
    def _gap_continuation_signal(self, latest: pd.Series, gap_classification: Dict, 
                               data: pd.DataFrame) -> Dict:
        """Generate gap continuation (momentum) signal"""
        
        gap_direction = gap_classification['direction']
        gap_size = gap_classification['gap_size']
        
        if gap_direction == 'UP':
            # Gap up: Buy signal (expecting continued upward momentum)
            signal_type = 'BUY'
            target_price = latest['Close'] * (1 + gap_size * 1.5)  # 1.5x gap extension
            stop_price = latest['Close'] * (1 - self.config.GAP_MAX_RISK)
        else:
            # Gap down: Sell signal (expecting continued downward momentum)
            signal_type = 'SELL'
            target_price = latest['Close'] * (1 - gap_size * 1.5)  # 1.5x gap extension
            stop_price = latest['Close'] * (1 + self.config.GAP_MAX_RISK)
        
        confidence = self._calculate_continuation_confidence(latest, gap_classification)
        
        return {
            'signal_type': signal_type,
            'confidence': confidence,
            'gap_strategy': 'CONTINUATION',
            'metadata': json.dumps({
                'gap_size': gap_classification['gap_size'],
                'gap_direction': gap_direction,
                'target_price': target_price,
                'stop_price': stop_price,
                'volume_ratio': gap_classification['volume_ratio'],
                'quality': gap_classification['quality'],
                'strategy_logic': 'gap_continuation_momentum'
            })
        }
    
    def _calculate_fade_confidence(self, latest: pd.Series, gap_classification: Dict) -> float:
        """Calculate confidence for gap fade trades"""
        confidence = 0.5  # Base confidence
        
        gap_size = gap_classification['gap_size']
        volume_strength = gap_classification['volume_strength']
        quality = gap_classification['quality']
        
        # Larger gaps have higher fade probability
        if gap_size > self.config.GAP_LARGE_SIZE:
            confidence += 0.3
        elif gap_size > self.config.GAP_MIN_SIZE * 2:
            confidence += 0.2
        
        # High volume gaps are more reliable
        if volume_strength == 'VERY_HIGH':
            confidence += 0.2
        elif volume_strength == 'HIGH':
            confidence += 0.1
        
        # Quality adjustment
        if quality == 'HIGH':
            confidence += 0.1
        
        # Check for overextension (RSI if available)
        if hasattr(latest, 'rsi'):
            if gap_classification['direction'] == 'UP' and latest['rsi'] > 70:
                confidence += 0.2  # Overbought gap up
            elif gap_classification['direction'] == 'DOWN' and latest['rsi'] < 30:
                confidence += 0.2  # Oversold gap down
        
        return min(confidence, 1.0)
    
    def _calculate_continuation_confidence(self, latest: pd.Series, gap_classification: Dict) -> float:
        """Calculate confidence for gap continuation trades"""
        confidence = 0.4  # Lower base confidence (continuation less reliable)
        
        gap_size = gap_classification['gap_size']
        volume_strength = gap_classification['volume_strength']
        quality = gap_classification['quality']
        
        # Medium gaps with high volume are good for continuation
        if self.config.GAP_MIN_SIZE <= gap_size <= self.config.GAP_LARGE_SIZE:
            confidence += 0.2
        
        # Very high volume suggests institutional interest
        if volume_strength == 'VERY_HIGH':
            confidence += 0.3
        elif volume_strength == 'HIGH':
            confidence += 0.2
        
        # Quality adjustment
        if quality == 'HIGH':
            confidence += 0.2
        elif quality == 'MEDIUM':
            confidence += 0.1
        
        return min(confidence, 1.0)
    