# strategies/microstructure_breakout.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, time
import json

class MicrostructureBreakoutStrategy:
    """
    Enhanced Microstructure Breakout Strategy
    
    Exploits 21-45% tighter bid-ask spreads to enable more precise
    technical strategies including ORB and compression breakouts
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "MicrostructureBreakout"
        
        # Timing parameters
        self.market_open = time(9, 30)
        self.avoid_open_minutes = 45  # Wait 45 min after open
        self.orb_period_minutes = 15   # 15-minute opening range
        
        # Technical parameters
        self.min_volume_multiplier = 1.5
        self.breakout_volume_multiplier = 2.0
        self.compression_candles_min = 5
        self.compression_candles_max = 10
        self.compression_range_pct = 0.02  # 2% max range for compression
        
        # Risk parameters
        self.max_risk_per_trade = 0.02  # 2% max risk
        self.min_reward_ratio = 2.0     # 2:1 min reward:risk
        self.atr_stop_multiplier = 1.5
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate microstructure breakout signals"""
        signals = []
        
        if len(data) < 20:
            return signals
            
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check if we're in valid trading window
        if not self._is_valid_trading_time():
            return signals
            
        # Calculate technical indicators
        atr = self._calculate_atr(data)
        volume_ratio = self._calculate_volume_ratio(data)
        
        # Check for different breakout patterns
        
        # 1. Opening Range Breakout (ORB)
        orb_signal = self._check_orb_pattern(data, latest, volume_ratio)
        if orb_signal:
            orb_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(orb_signal)
            
        # 2. Compression Breakout
        compression_signal = self._check_compression_breakout(data, latest, volume_ratio, atr)
        if compression_signal:
            compression_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(compression_signal)
            
        # 3. Multi-timeframe Breakout
        mtf_signal = self._check_multi_timeframe_breakout(data, latest, volume_ratio)
        if mtf_signal:
            mtf_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(mtf_signal)
            
        return signals
    
    def _is_valid_trading_time(self) -> bool:
        """Check if we're in valid trading window"""
        current_time = datetime.now().time()
        
        # Calculate cutoff time (45 minutes after open)
        cutoff_hour = 10 if self.market_open.minute + self.avoid_open_minutes >= 60 else 9
        cutoff_minute = (self.market_open.minute + self.avoid_open_minutes) % 60
        cutoff_time = time(cutoff_hour, cutoff_minute)
        
        market_close = time(16, 0)
        
        return cutoff_time <= current_time <= market_close
    
    def _calculate_atr(self, data: pd.DataFrame, periods: int = 14) -> float:
        """Calculate Average True Range"""
        if len(data) < periods + 1:
            return 0.0
            
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(periods).mean().iloc[-1]
        
        return atr if not pd.isna(atr) else 0.0
    
    def _calculate_volume_ratio(self, data: pd.DataFrame, periods: int = 20) -> float:
        """Calculate current volume vs average volume"""
        if len(data) < periods:
            return 1.0
            
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(periods).mean()
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def _check_orb_pattern(self, data: pd.DataFrame, latest: pd.Series, volume_ratio: float) -> Optional[Dict]:
        """Check for Opening Range Breakout pattern"""
        if len(data) < 5:
            return None
            
        # Get recent candles (simulate ORB period)
        recent_data = data.tail(self.orb_period_minutes // 5)  # Assume 5-min candles
        
        if len(recent_data) < 3:
            return None
            
        # Calculate opening range
        orb_high = recent_data['High'].max()
        orb_low = recent_data['Low'].min()
        orb_range = orb_high - orb_low
        
        current_price = latest['Close']
        
        # Check for breakout above range
        if current_price > orb_high and volume_ratio >= self.min_volume_multiplier:
            # Calculate risk/reward
            stop_price = orb_high * 0.998  # Just below breakout level
            target_price = orb_high + (orb_range * 2)  # 2x range extension
            
            risk = current_price - stop_price
            reward = target_price - current_price
            
            if risk > 0 and (reward / risk) >= self.min_reward_ratio:
                confidence = self._calculate_orb_confidence(volume_ratio, orb_range, current_price)
                
                return {
                    'signal_type': 'BUY',
                    'confidence': confidence,
                    'metadata': json.dumps({
                        'pattern': 'opening_range_breakout',
                        'orb_high': orb_high,
                        'orb_low': orb_low,
                        'orb_range': orb_range,
                        'volume_ratio': volume_ratio,
                        'stop_price': stop_price,
                        'target_price': target_price,
                        'risk_reward_ratio': reward / risk,
                        'strategy_logic': 'microstructure_orb'
                    })
                }
                
        # Check for breakout below range (short signal, but we're long-only)
        # Could be implemented as a sell signal for existing positions
        
        return None
    
    def _check_compression_breakout(self, data: pd.DataFrame, latest: pd.Series, 
                                  volume_ratio: float, atr: float) -> Optional[Dict]:
        """Check for price compression followed by breakout"""
        if len(data) < self.compression_candles_max:
            return None
            
        # Look for compression pattern
        compression_data = data.tail(self.compression_candles_max)
        
        # Calculate range compression
        compression_high = compression_data['High'].max()
        compression_low = compression_data['Low'].min()
        compression_range = compression_high - compression_low
        
        # Check if range is compressed (within 2% range)
        avg_price = (compression_high + compression_low) / 2
        compression_pct = compression_range / avg_price
        
        if compression_pct > self.compression_range_pct:
            return None  # Not compressed enough
            
        # Check for breakout
        current_price = latest['Close']
        recent_high = data.tail(3)['High'].max()
        
        # Breakout above compression with volume
        if (current_price > compression_high and 
            volume_ratio >= self.breakout_volume_multiplier):
            
            # Calculate risk/reward using ATR
            stop_price = compression_high - (atr * 0.5)
            target_price = compression_high + (atr * 2)
            
            risk = current_price - stop_price
            reward = target_price - current_price
            
            if risk > 0 and (reward / risk) >= self.min_reward_ratio:
                confidence = self._calculate_compression_confidence(
                    volume_ratio, compression_pct, compression_range)
                
                return {
                    'signal_type': 'BUY',
                    'confidence': confidence,
                    'metadata': json.dumps({
                        'pattern': 'compression_breakout',
                        'compression_high': compression_high,
                        'compression_low': compression_low,
                        'compression_range': compression_range,
                        'compression_pct': compression_pct,
                        'volume_ratio': volume_ratio,
                        'atr': atr,
                        'stop_price': stop_price,
                        'target_price': target_price,
                        'risk_reward_ratio': reward / risk,
                        'strategy_logic': 'microstructure_compression'
                    })
                }
                
        return None
    
    def _check_multi_timeframe_breakout(self, data: pd.DataFrame, latest: pd.Series, 
                                      volume_ratio: float) -> Optional[Dict]:
        """Check for multi-timeframe aligned breakout"""
        if len(data) < 50:
            return None
            
        current_price = latest['Close']
        
        # Daily trend (20-period SMA)
        sma_20 = data['Close'].rolling(20).mean().iloc[-1]
        daily_trend_up = current_price > sma_20
        
        # Short-term breakout (5-period high)
        recent_high = data['High'].tail(5).max()
        short_term_breakout = current_price > recent_high
        
        # RSI momentum confirmation
        rsi = self._calculate_rsi(data['Close'])
        rsi_bullish = 50 < rsi < 80  # Momentum but not overbought
        
        # Volume confirmation
        volume_confirmed = volume_ratio >= self.min_volume_multiplier
        
        # All conditions must align
        if (daily_trend_up and short_term_breakout and 
            rsi_bullish and volume_confirmed):
            
            # Calculate stops and targets
            atr = self._calculate_atr(data)
            stop_price = current_price - (atr * self.atr_stop_multiplier)
            target_price = current_price + (atr * 3)  # 3:1.5 = 2:1 ratio
            
            risk = current_price - stop_price
            reward = target_price - current_price
            
            if risk > 0:
                confidence = self._calculate_mtf_confidence(
                    volume_ratio, rsi, current_price - sma_20)
                
                return {
                    'signal_type': 'BUY',
                    'confidence': confidence,
                    'metadata': json.dumps({
                        'pattern': 'multi_timeframe_breakout',
                        'sma_20': sma_20,
                        'recent_high': recent_high,
                        'rsi': rsi,
                        'volume_ratio': volume_ratio,
                        'atr': atr,
                        'stop_price': stop_price,
                        'target_price': target_price,
                        'risk_reward_ratio': reward / risk,
                        'strategy_logic': 'microstructure_mtf'
                    })
                }
                
        return None
    
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < periods + 1:
            return 50.0
            
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_orb_confidence(self, volume_ratio: float, orb_range: float, 
                                current_price: float) -> float:
        """Calculate confidence for ORB signals"""
        confidence = 0.5
        
        # Higher volume = higher confidence
        if volume_ratio > 3.0:
            confidence += 0.3
        elif volume_ratio > 2.0:
            confidence += 0.2
        elif volume_ratio > 1.5:
            confidence += 0.1
            
        # Optimal range size (not too tight, not too wide)
        range_pct = orb_range / current_price
        if 0.005 <= range_pct <= 0.015:  # 0.5% to 1.5% range
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    def _calculate_compression_confidence(self, volume_ratio: float, 
                                        compression_pct: float, compression_range: float) -> float:
        """Calculate confidence for compression breakout signals"""
        confidence = 0.5
        
        # Higher volume on breakout
        if volume_ratio > 2.5:
            confidence += 0.3
        elif volume_ratio > 2.0:
            confidence += 0.2
            
        # Tighter compression = higher confidence
        if compression_pct < 0.01:  # Very tight compression
            confidence += 0.3
        elif compression_pct < 0.015:
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    def _calculate_mtf_confidence(self, volume_ratio: float, rsi: float, 
                                price_above_sma: float) -> float:
        """Calculate confidence for multi-timeframe signals"""
        confidence = 0.5
        
        # Volume confirmation
        if volume_ratio > 2.0:
            confidence += 0.2
        elif volume_ratio > 1.5:
            confidence += 0.1
            
        # RSI in sweet spot
        if 55 <= rsi <= 70:
            confidence += 0.2
        elif 50 <= rsi <= 75:
            confidence += 0.1
            
        # Strong trend
        if price_above_sma > 0:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def calculate_position_size(self, account_value: float, entry_price: float, 
                              stop_price: float) -> int:
        """Calculate position size based on risk management"""
        max_risk = account_value * self.max_risk_per_trade
        risk_per_share = entry_price - stop_price
        
        if risk_per_share <= 0:
            return 0
            
        shares = int(max_risk / risk_per_share)
        return max(shares, 1) if shares > 0 else 0
    
    def validate_spread_improvement(self, symbol: str) -> bool:
        """Validate that spreads are tight enough for strategy"""
        # This would ideally check real-time spread data
        # For now, assume major ETFs and large caps have good spreads
        major_symbols = [
            'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'
        ]
        
        return symbol in major_symbols