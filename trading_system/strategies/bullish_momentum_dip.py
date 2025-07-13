# strategies/bullish_momentum_dip.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class BullishMomentumDipStrategy:
    """
    Bullish Momentum Dip Strategy - Buy the Dip in Uptrending Stocks
    
    Entry Rules:
    - Stock must be in confirmed uptrend (above key moving averages)
    - Recent strong momentum (20-day and 50-day performance)
    - Current pullback from recent highs (dip opportunity)
    - RSI oversold but not extreme (30-45 range)
    - Volume confirmation on the dip
    - Only trade in bullish market conditions
    
    Exit Rules:
    - Sell when momentum exhausts (RSI > 75)
    - Sell when trend breaks (below key support)
    - Sell when market turns bearish
    - Stop loss at 6% below entry
    
    Risk Management:
    - Only long positions (no shorting in momentum strategy)
    - Focus on high-quality momentum stocks
    - Market condition filtering (bullish markets only)
    - Quick exits on trend breaks
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "BullishMomentumDip"
        
        # Momentum-specific parameters
        self.MIN_MOMENTUM_20D = 0.05        # 5% minimum 20-day momentum
        self.MIN_MOMENTUM_50D = 0.10        # 10% minimum 50-day momentum
        self.MAX_PULLBACK_FROM_HIGH = 0.08  # 8% max pullback from recent high
        self.MIN_PULLBACK_FROM_HIGH = 0.02  # 2% minimum pullback (actual dip)
        self.RSI_DIP_MIN = 30               # Min RSI for dip (not extreme oversold)
        self.RSI_DIP_MAX = 45               # Max RSI for dip (still oversold)
        self.RSI_EXIT = 75                  # RSI exit level (momentum exhausted)
        self.VOLUME_CONFIRMATION = 1.2     # 20% above average volume
        self.TREND_LOOKBACK = 50            # Days to confirm trend
        self.HIGH_LOOKBACK = 20             # Days to find recent high
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals for bullish momentum dip strategy
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        if len(data) < self.TREND_LOOKBACK:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Only trade in bullish market conditions
        market_condition = self._assess_market_condition(data)
        if market_condition != 'BULLISH':
            return signals
        
        # Check for buy signal (dip in uptrend)
        buy_signal = self._check_momentum_dip_buy_signal(latest, data, symbol)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol)
            
            # Convert all values to JSON-serializable types
            momentum_20d = float(self._calculate_momentum(data, 20))
            momentum_50d = float(self._calculate_momentum(data, 50))
            pullback = float(self._calculate_pullback_from_high(data))
            trend_strength = float(self._calculate_trend_strength(data))
            volume_confirmation = bool(self._check_volume_confirmation(data))
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': float(latest['Close']),
                'confidence': float(confidence),
                'reason': 'bullish_momentum_dip_opportunity',
                'metadata': json.dumps({
                    'momentum_20d': momentum_20d,
                    'momentum_50d': momentum_50d,
                    'pullback_from_high': pullback,
                    'trend_strength': trend_strength,
                    'rsi_level': float(latest.get('rsi', 50)),
                    'volume_confirmation': volume_confirmation,  # Now explicitly bool
                    'stop_loss': float(latest['Close'] * 0.94),  # 6% stop loss
                    'strategy_logic': 'bullish_momentum_dip_entry'
                })
            })
        
        # Check for sell signal (momentum exhaustion or trend break)
        sell_signal = self._check_momentum_sell_signal(latest, data, symbol)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol)
            
            # Convert all values to JSON-serializable types
            momentum_exhausted = bool(latest.get('rsi', 50) > self.RSI_EXIT)
            trend_broken = bool(self._check_trend_break(data))
            market_bearish = bool(market_condition == 'BEARISH')
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': float(latest['Close']),
                'confidence': float(confidence),
                'reason': 'momentum_exhaustion_or_trend_break',
                'metadata': json.dumps({
                    'momentum_exhausted': momentum_exhausted,
                    'trend_broken': trend_broken,
                    'market_bearish': market_bearish
                })
            })
        
        return signals
    
    def _assess_market_condition(self, data: pd.DataFrame) -> str:
        """Assess overall market condition (simplified using SPY-like behavior)"""
        if len(data) < 50:
            return 'NEUTRAL'
        
        # Use moving averages and momentum to assess market
        close_prices = data['Close']
        sma_20 = close_prices.rolling(20).mean()
        sma_50 = close_prices.rolling(50).mean()
        
        current_price = close_prices.iloc[-1]
        momentum_20d = (current_price / close_prices.iloc[-21]) - 1
        
        # Bullish: Above both MAs with positive momentum
        if (current_price > sma_20.iloc[-1] > sma_50.iloc[-1] and 
            momentum_20d > 0.02):  # 2% positive momentum
            return 'BULLISH'
        
        # Bearish: Below both MAs with negative momentum  
        elif (current_price < sma_20.iloc[-1] < sma_50.iloc[-1] and
              momentum_20d < -0.02):
            return 'BEARISH'
        
        return 'NEUTRAL'
    
    def _calculate_momentum(self, data: pd.DataFrame, period: int) -> float:
        """Calculate momentum over specified period"""
        if len(data) < period:
            return 0.0
        
        start_price = data['Close'].iloc[-period]
        current_price = data['Close'].iloc[-1]
        
        return (current_price / start_price) - 1.0
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate overall trend strength"""
        if len(data) < 50:
            return 0.0
        
        close_prices = data['Close']
        current_price = close_prices.iloc[-1]
        
        # Multiple timeframe trend analysis
        sma_10 = close_prices.rolling(10).mean().iloc[-1]
        sma_20 = close_prices.rolling(20).mean().iloc[-1]
        sma_50 = close_prices.rolling(50).mean().iloc[-1]
        
        # Score based on moving average alignment
        score = 0
        if current_price > sma_10:
            score += 1
        if sma_10 > sma_20:
            score += 1
        if sma_20 > sma_50:
            score += 1
        if current_price > sma_50:
            score += 1
        
        return score / 4.0  # Normalize to 0-1
    
    def _calculate_pullback_from_high(self, data: pd.DataFrame) -> float:
        """Calculate pullback percentage from recent high"""
        if len(data) < self.HIGH_LOOKBACK:
            return 0.0
        
        recent_high = data['High'].tail(self.HIGH_LOOKBACK).max()
        current_price = data['Close'].iloc[-1]
        
        pullback = (recent_high - current_price) / recent_high
        return pullback
    
    def _check_volume_confirmation(self, data: pd.DataFrame) -> bool:
        """Check for volume confirmation"""
        if len(data) < 20:
            return True  # Default to true if insufficient data
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(20).mean()
        
        return current_volume >= (avg_volume * self.VOLUME_CONFIRMATION)
    
    def _check_trend_break(self, data: pd.DataFrame) -> bool:
        """Check if the uptrend has been broken"""
        if len(data) < 20:
            return False
        
        close_prices = data['Close']
        current_price = close_prices.iloc[-1]
        sma_20 = close_prices.rolling(20).mean().iloc[-1]
        
        # Simple trend break: below 20-day MA
        return current_price < sma_20 * 0.97  # 3% below 20-day MA
    
    def _check_momentum_dip_buy_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check if current conditions meet momentum dip buy criteria"""
        
        # 1. Strong momentum requirements
        momentum_20d = self._calculate_momentum(data, 20)
        momentum_50d = self._calculate_momentum(data, 50)
        
        momentum_condition = (momentum_20d >= self.MIN_MOMENTUM_20D and 
                            momentum_50d >= self.MIN_MOMENTUM_50D)
        
        # 2. Trend strength requirement
        trend_strength = self._calculate_trend_strength(data)
        trend_condition = trend_strength >= 0.75  # Strong trend
        
        # 3. Pullback/dip requirement
        pullback = self._calculate_pullback_from_high(data)
        dip_condition = (self.MIN_PULLBACK_FROM_HIGH <= pullback <= self.MAX_PULLBACK_FROM_HIGH)
        
        # 4. RSI in dip range (oversold but not extreme)
        rsi = latest.get('rsi', 50)
        rsi_condition = self.RSI_DIP_MIN <= rsi <= self.RSI_DIP_MAX
        
        # 5. Volume confirmation
        volume_condition = self._check_volume_confirmation(data)
        
        # 6. Price above key moving averages (trend confirmation)
        if len(data) >= 50:
            current_price = latest['Close']
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            ma_condition = current_price > sma_20 and sma_20 > sma_50
        else:
            ma_condition = True
        
        # 7. Not already extremely overbought
        not_overbought = rsi < 70
        
        return (momentum_condition and trend_condition and dip_condition and 
                rsi_condition and volume_condition and ma_condition and not_overbought)
    
    def _check_momentum_sell_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check if current conditions meet momentum sell criteria"""
        
        # 1. Momentum exhaustion (RSI overbought)
        rsi = latest.get('rsi', 50)
        momentum_exhausted = rsi > self.RSI_EXIT
        
        # 2. Trend break
        trend_broken = self._check_trend_break(data)
        
        # 3. Market turned bearish
        market_condition = self._assess_market_condition(data)
        market_bearish = market_condition == 'BEARISH'
        
        # 4. Extreme momentum (take profits at 25%+ gains)
        momentum_20d = self._calculate_momentum(data, 20)
        extreme_gains = momentum_20d > 0.25
        
        # 5. Volume exhaustion (decreasing volume on rallies)
        volume_exhaustion = self._check_volume_exhaustion(data)
        
        return (momentum_exhausted or trend_broken or market_bearish or 
                extreme_gains or volume_exhaustion)
    
    def _check_volume_exhaustion(self, data: pd.DataFrame) -> bool:
        """Check for volume exhaustion on recent rallies"""
        if len(data) < 10:
            return False
        
        # Compare recent 5-day volume to previous 5-day volume
        recent_volume = data['Volume'].tail(5).mean()
        previous_volume = data['Volume'].tail(10).head(5).mean()
        
        # Check if volume is declining while price might be rising
        recent_price_change = (data['Close'].iloc[-1] / data['Close'].iloc[-6]) - 1
        volume_declining = recent_volume < previous_volume * 0.8  # 20% volume decline
        
        # Volume exhaustion if price flat/up but volume declining significantly
        return volume_declining and recent_price_change > -0.02
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.6  # Base confidence for momentum plays
        
        if signal_type == 'BUY':
            # Higher confidence for stronger momentum
            momentum_20d = self._calculate_momentum(data, 20)
            momentum_50d = self._calculate_momentum(data, 50)
            
            if momentum_50d > 0.20:  # 20%+ 50-day momentum
                confidence += 0.2
            elif momentum_50d > 0.15:
                confidence += 0.1
            
            if momentum_20d > 0.10:  # 10%+ 20-day momentum  
                confidence += 0.15
            elif momentum_20d > 0.07:
                confidence += 0.1
            
            # Trend strength bonus
            trend_strength = self._calculate_trend_strength(data)
            if trend_strength > 0.85:
                confidence += 0.15
            elif trend_strength > 0.75:
                confidence += 0.1
            
            # Perfect dip level
            pullback = self._calculate_pullback_from_high(data)
            if 0.03 <= pullback <= 0.06:  # 3-6% pullback is ideal
                confidence += 0.1
            
            # Volume confirmation
            if self._check_volume_confirmation(data):
                confidence += 0.1
            
            # RSI in sweet spot
            rsi = latest.get('rsi', 50)
            if 32 <= rsi <= 40:  # Ideal dip RSI range
                confidence += 0.1
        
        elif signal_type == 'SELL':
            # Higher confidence for clear exit signals
            rsi = latest.get('rsi', 50)
            if rsi > 80:  # Very overbought
                confidence += 0.3
            elif rsi > 75:
                confidence += 0.2
            
            # Trend break confidence
            if self._check_trend_break(data):
                confidence += 0.25
            
            # Market condition confidence
            market_condition = self._assess_market_condition(data)
            if market_condition == 'BEARISH':
                confidence += 0.2
            
            # Extreme momentum take-profit confidence
            momentum_20d = self._calculate_momentum(data, 20)
            if momentum_20d > 0.30:  # 30%+ gains
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def calculate_position_size(self, account_value: float, price: float) -> int:
        """Calculate position size for momentum dip plays"""
        # Momentum strategies can be more aggressive with position sizing
        max_position_value = account_value * getattr(self.config, 'MAX_POSITION_VALUE_PERCENT', 0.1)
        
        # Slight bonus for high-confidence momentum plays
        max_position_value *= 1.1  # 10% bonus
        
        shares = int(max_position_value / price)
        return max(shares, 1) if shares > 0 else 0