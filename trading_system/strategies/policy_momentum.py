# strategies/policy_momentum.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import the base strategy classes
from .base_strategy import TradingStrategy, TradingSignal

class PolicyMomentumStrategy(TradingStrategy):
    """
    Policy Momentum Strategy - Fed/Policy Volatility Plays
    
    Entry Rules:
    - Buy policy-sensitive stocks during Fed dovish pivots
    - Sell during hawkish policy shifts
    - Focus on rate-sensitive sectors (financials, growth)
    
    Exit Rules:
    - Sell on policy reversal signals
    - VIX spike protection (exit if VIX > 30)
    
    Risk Management:
    - Avoid during high VIX periods (>25)
    - Stop loss at 8% below entry
    - Monitor Fed meeting calendar
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "PolicyMomentum"
        
        # Policy-specific thresholds
        self.VIX_HIGH_THRESHOLD = 25
        self.VIX_EXTREME_THRESHOLD = 30
        self.MOMENTUM_PERIOD = 10  # 10-day momentum for policy response
        self.VOLATILITY_LOOKBACK = 20  # 20-day volatility
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals based on policy momentum
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Stock symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Only process policy-sensitive stocks
        if not self._is_policy_sensitive(symbol):
            return signals
        
        if len(data) < self.VOLATILITY_LOOKBACK:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Get estimated VIX level (would need real VIX data in production)
        estimated_vix = self._estimate_vix_level(data)
        
        # Check for buy signal
        buy_signal = self._check_buy_signal(latest, data, symbol, estimated_vix)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol, estimated_vix)
            
            # Convert all values to JSON-serializable types
            policy_momentum = float(self._calculate_policy_momentum(data))
            stop_loss_price = float(latest['Close'] * (1 - self.config.PERSONAL_STOP_LOSS))
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': float(latest['Close']),
                'confidence': float(confidence),
                'reason': 'policy_reversal_or_vix_spike',
                'metadata': json.dumps({
                    'estimated_vix': float(estimated_vix),
                    'policy_momentum': policy_momentum,
                    'volatility_regime': str(self._get_volatility_regime(estimated_vix)),
                    'sector': str(self._get_policy_sector(symbol)),
                    'stop_loss': stop_loss_price,
                    'strategy_logic': 'policy_momentum_entry'
                })
            })
        
        # Check for sell signal
        sell_signal = self._check_sell_signal(latest, data, symbol, estimated_vix)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol, estimated_vix)
            
            # Convert all values to JSON-serializable types
            vix_spike = bool(estimated_vix > self.VIX_EXTREME_THRESHOLD)
            policy_reversal = True
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': float(latest['Close']),
                'confidence': float(confidence),
                'metadata': json.dumps({
                    'estimated_vix': float(estimated_vix),
                    'vix_spike': vix_spike,
                    'policy_reversal': policy_reversal
                })
            })
        
        return signals
    
    def _is_policy_sensitive(self, symbol: str) -> bool:
        """Check if symbol is policy-sensitive"""
        policy_sensitive = [
            # Rate-sensitive financials
            'JPM', 'BAC', 'USB', 'XLF',
            # Growth stocks (policy sensitive)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
            # Market-sensitive ETFs
            'SPY', 'QQQ', 'IWM'
        ]
        return symbol in policy_sensitive
    
    def _estimate_vix_level(self, data: pd.DataFrame) -> float:
        """Estimate VIX level based on price volatility"""
        if len(data) < self.VOLATILITY_LOOKBACK:
            return 20.0  # Default VIX level
        
        # Calculate rolling volatility as proxy for VIX
        returns = data['Close'].pct_change().dropna()
        volatility = returns.rolling(window=self.VOLATILITY_LOOKBACK).std().iloc[-1]
        
        # Convert to annualized volatility (rough VIX proxy)
        annualized_vol = volatility * np.sqrt(252) * 100
        
        # Scale to typical VIX range (15-40)
        estimated_vix = max(15, min(40, annualized_vol))
        
        return estimated_vix
    
    def _get_volatility_regime(self, vix_level: float) -> str:
        """Categorize volatility regime"""
        if vix_level < 20:
            return 'low'
        elif vix_level < 25:
            return 'moderate'
        elif vix_level < 30:
            return 'high'
        else:
            return 'extreme'
    
    def _get_policy_sector(self, symbol: str) -> str:
        """Get the policy-sensitive sector for this symbol"""
        if symbol in ['JPM', 'BAC', 'USB', 'XLF']:
            return 'financials'
        elif symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']:
            return 'growth_tech'
        elif symbol in ['SPY', 'QQQ', 'IWM']:
            return 'broad_market_etf'
        else:
            return 'other'
    
    def _calculate_policy_momentum(self, data: pd.DataFrame) -> float:
        """Calculate policy momentum based on recent price action"""
        if len(data) < self.MOMENTUM_PERIOD:
            return 0.0
        
        # Short-term momentum to capture policy response
        start_price = data.iloc[-self.MOMENTUM_PERIOD]['Close']
        current_price = data.iloc[-1]['Close']
        
        return (current_price / start_price) - 1.0
    
    def _check_buy_signal(self, latest: pd.Series, data: pd.DataFrame, 
                         symbol: str, vix_level: float) -> bool:
        """Check if current conditions meet buy criteria"""
        # VIX not too high (avoid extreme volatility)
        vix_condition = vix_level < self.VIX_HIGH_THRESHOLD
        
        # Positive policy momentum
        policy_momentum = self._calculate_policy_momentum(data)
        momentum_condition = policy_momentum > 0.01  # 1% positive momentum
        
        # RSI not overbought
        rsi_condition = latest.get('rsi', 50) < 70
        
        # Volume confirmation
        avg_volume = data['Volume'].tail(5).mean()
        volume_condition = latest['Volume'] > avg_volume * 1.1
        
        # Sector-specific conditions
        sector = self._get_policy_sector(symbol)
        sector_condition = True
        
        if sector == 'financials':
            # Financials benefit from rising rates environment
            # Look for steepening yield curve signals (simplified)
            sector_condition = policy_momentum > 0.02  # Higher threshold for financials
        elif sector == 'growth_tech':
            # Growth stocks benefit from dovish policy
            sector_condition = vix_level < 22  # Lower VIX threshold for growth
        
        return (vix_condition and momentum_condition and 
                rsi_condition and sector_condition)
    
    def _check_sell_signal(self, latest: pd.Series, data: pd.DataFrame, 
                          symbol: str, vix_level: float) -> bool:
        """Check if current conditions meet sell criteria"""
        # VIX spike protection
        vix_spike = vix_level > self.VIX_EXTREME_THRESHOLD
        
        # Policy momentum reversal
        policy_momentum = self._calculate_policy_momentum(data)
        momentum_reversal = policy_momentum < -0.02  # 2% negative momentum
        
        # Overbought RSI
        rsi_overbought = latest.get('rsi', 50) > 75
        
        # Sector-specific exit conditions
        sector = self._get_policy_sector(symbol)
        sector_exit = False
        
        if sector == 'financials':
            # Exit financials if policy turns dovish
            sector_exit = policy_momentum < -0.03
        elif sector == 'growth_tech':
            # Exit growth on hawkish policy signals
            sector_exit = vix_level > 27  # Earlier exit for growth
        
        return vix_spike or momentum_reversal or rsi_overbought or sector_exit
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str, vix_level: float) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.55  # Base confidence for policy plays
        
        policy_momentum = self._calculate_policy_momentum(data)
        sector = self._get_policy_sector(symbol)
        
        if signal_type == 'BUY':
            # Higher confidence for stronger policy momentum
            if policy_momentum > 0.03:  # 3% momentum
                confidence += 0.25
            elif policy_momentum > 0.01:
                confidence += 0.15
            
            # VIX level consideration
            if vix_level < 20:  # Low volatility
                confidence += 0.2
            elif vix_level < 22:
                confidence += 0.1
            
            # Sector-specific confidence boosts
            if sector == 'financials' and policy_momentum > 0.025:
                confidence += 0.1  # Financials with strong momentum
            elif sector == 'growth_tech' and vix_level < 18:
                confidence += 0.1  # Growth in low vol environment
        
        elif signal_type == 'SELL':
            # Higher confidence for clear policy reversals
            if policy_momentum < -0.03:
                confidence += 0.3
            elif policy_momentum < -0.02:
                confidence += 0.2
            
            # VIX spike confidence
            if vix_level > self.VIX_EXTREME_THRESHOLD:
                confidence += 0.3
            elif vix_level > self.VIX_HIGH_THRESHOLD:
                confidence += 0.2
        
        return min(confidence, 1.0)
    