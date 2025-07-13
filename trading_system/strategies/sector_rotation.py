# strategies/sector_rotation.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class SectorRotationStrategy:
    """
    Sector Rotation Strategy - Momentum-Based Sector ETF Rotation
    
    Entry Rules:
    - Buy sector ETFs showing relative strength and momentum
    - Focus on sectors with improving fundamentals
    - Rotate based on economic cycle indicators
    
    Exit Rules:
    - Sell when relative performance deteriorates
    - Momentum exhaustion signals
    - Economic cycle rotation signals
    
    Risk Management:
    - Max 20% allocation per sector
    - Diversification across multiple sectors
    - Quick rotation on momentum shifts
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "SectorRotation"
        
        # Sector rotation parameters
        self.MOMENTUM_PERIOD = 30  # 30-day momentum
        self.RELATIVE_STRENGTH_PERIOD = 60  # 60-day relative strength
        self.MIN_RELATIVE_STRENGTH = 1.03  # 3% outperformance vs SPY
        self.ROTATION_THRESHOLD = 0.05  # 5% performance difference for rotation
        
        # Economic cycle sectors
        self.EARLY_CYCLE_SECTORS = ['XLF', 'XLI', 'XLB']  # Financials, Industrials, Materials
        self.MID_CYCLE_SECTORS = ['XLK', 'XLY', 'XLC']    # Tech, Consumer Disc, Comm Services
        self.LATE_CYCLE_SECTORS = ['XLE', 'XLV']          # Energy, Healthcare
        self.DEFENSIVE_SECTORS = ['XLP', 'XLU', 'XLRE']   # Staples, Utilities, REITs
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate buy/sell signals for sector rotation
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Sector ETF symbol
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Only process sector ETFs
        if not self._is_sector_etf(symbol):
            return signals
        
        if len(data) < self.RELATIVE_STRENGTH_PERIOD:
            return signals
        
        # Get the latest data point
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check for buy signal (sector rotation entry)
        buy_signal = self._check_sector_buy_signal(latest, data, symbol)
        if buy_signal:
            confidence = self._calculate_confidence(latest, data, 'BUY', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'sector_momentum_rotation',
                'metadata': json.dumps({
                    'sector_name': self._get_sector_name(symbol),
                    'relative_strength': self._calculate_relative_strength(data),
                    'momentum_30d': self._calculate_momentum(data, self.MOMENTUM_PERIOD),
                    'cycle_position': self._get_cycle_position(symbol),
                    'rotation_score': self._calculate_rotation_score(data, symbol),
                    'stop_loss': latest['Close'] * (1 - self.config.PERSONAL_STOP_LOSS),
                    'strategy_logic': 'sector_rotation_entry'
                })
            })
        
        # Check for sell signal (sector rotation exit)
        sell_signal = self._check_sector_sell_signal(latest, data, symbol)
        if sell_signal:
            confidence = self._calculate_confidence(latest, data, 'SELL', symbol)
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'reason': 'sector_rotation_exit',
                'metadata': json.dumps({
                    'relative_weakness': self._calculate_relative_strength(data) < 0.98,
                    'momentum_deterioration': self._calculate_momentum(data, 20) < -0.02
                })
            })
        
        return signals
    
    def _is_sector_etf(self, symbol: str) -> bool:
        """Check if symbol is a sector ETF"""
        sector_etfs = [
            'XLK',   # Technology
            'XLF',   # Financials
            'XLE',   # Energy
            'XLV',   # Healthcare
            'XLI',   # Industrials
            'XLP',   # Consumer Staples
            'XLU',   # Utilities
            'XLY',   # Consumer Discretionary
            'XLB',   # Materials
            'XLRE',  # Real Estate
            'XLC'    # Communication Services
        ]
        return symbol in sector_etfs
    
    def _get_sector_name(self, symbol: str) -> str:
        """Get the sector name for the ETF symbol"""
        sector_map = {
            'XLK': 'Technology',
            'XLF': 'Financials', 
            'XLE': 'Energy',
            'XLV': 'Healthcare',
            'XLI': 'Industrials',
            'XLP': 'Consumer Staples',
            'XLU': 'Utilities',
            'XLY': 'Consumer Discretionary',
            'XLB': 'Materials',
            'XLRE': 'Real Estate',
            'XLC': 'Communication Services'
        }
        return sector_map.get(symbol, 'Unknown')
    
    def _get_cycle_position(self, symbol: str) -> str:
        """Determine economic cycle position for sector"""
        if symbol in self.EARLY_CYCLE_SECTORS:
            return 'early_cycle'
        elif symbol in self.MID_CYCLE_SECTORS:
            return 'mid_cycle'
        elif symbol in self.LATE_CYCLE_SECTORS:
            return 'late_cycle'
        elif symbol in self.DEFENSIVE_SECTORS:
            return 'defensive'
        else:
            return 'unknown'
    
    def _calculate_relative_strength(self, data: pd.DataFrame) -> float:
        """Calculate relative strength vs SPY"""
        if len(data) < self.RELATIVE_STRENGTH_PERIOD:
            return 1.0
        
        # Calculate sector performance
        period_start = data.iloc[-self.RELATIVE_STRENGTH_PERIOD]['Close']
        current_price = data.iloc[-1]['Close']
        sector_performance = current_price / period_start
        
        # Assume SPY performance (would need real SPY data in production)
        spy_performance = 1.05  # Assume 5% SPY performance as baseline
        
        return sector_performance / spy_performance
    
    def _calculate_momentum(self, data: pd.DataFrame, period: int) -> float:
        """Calculate momentum over specified period"""
        if len(data) < period:
            return 0.0
        
        start_price = data.iloc[-period]['Close']
        current_price = data.iloc[-1]['Close']
        
        return (current_price / start_price) - 1.0
    
    def _calculate_rotation_score(self, data: pd.DataFrame, symbol: str) -> float:
        """Calculate overall rotation score for sector"""
        # Combine multiple factors
        relative_strength = self._calculate_relative_strength(data)
        momentum_30d = self._calculate_momentum(data, 30)
        momentum_10d = self._calculate_momentum(data, 10)
        
        # Volume trend
        volume_trend = 0.0
        if len(data) >= 20:
            recent_volume = data['Volume'].tail(10).mean()
            historical_volume = data['Volume'].tail(20).head(10).mean()
            volume_trend = (recent_volume / historical_volume) - 1.0 if historical_volume > 0 else 0.0
        
        # Weighted score
        rotation_score = (
            relative_strength * 0.4 +      # 40% weight on relative strength
            (1 + momentum_30d) * 0.3 +     # 30% weight on 30-day momentum
            (1 + momentum_10d) * 0.2 +     # 20% weight on 10-day momentum
            (1 + volume_trend) * 0.1       # 10% weight on volume trend
        )
        
        return rotation_score
    
    def _estimate_market_cycle(self) -> str:
        """Estimate current market cycle phase (simplified)"""
        # In production, this would use economic indicators
        # For now, return a default cycle phase
        return 'mid_cycle'
    
    def _check_sector_buy_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for sector rotation buy signal"""
        # Relative strength requirement
        relative_strength = self._calculate_relative_strength(data)
        strength_condition = relative_strength >= self.MIN_RELATIVE_STRENGTH
        
        # Momentum conditions
        momentum_30d = self._calculate_momentum(data, 30)
        momentum_10d = self._calculate_momentum(data, 10)
        momentum_condition = momentum_30d > 0.02 and momentum_10d > 0.01  # Positive momentum
        
        # Rotation score threshold
        rotation_score = self._calculate_rotation_score(data, symbol)
        rotation_condition = rotation_score > 1.05  # Above average rotation score
        
        # Volume confirmation
        avg_volume = data['Volume'].tail(10).mean()
        volume_condition = latest['Volume'] > avg_volume * 0.8  # Reasonable volume
        
        # RSI not overbought
        rsi_condition = latest.get('rsi', 50) < 75
        
        # Cycle alignment (simplified)
        market_cycle = self._estimate_market_cycle()
        cycle_position = self._get_cycle_position(symbol)
        cycle_condition = True  # Simplified - would be more complex in production
        
        return (strength_condition and momentum_condition and 
                rotation_condition and rsi_condition and cycle_condition)
    
    def _check_sector_sell_signal(self, latest: pd.Series, data: pd.DataFrame, symbol: str) -> bool:
        """Check for sector rotation sell signal"""
        # Relative strength deterioration
        relative_strength = self._calculate_relative_strength(data)
        weakness_condition = relative_strength < 0.98  # 2% underperformance
        
        # Momentum deterioration
        momentum_30d = self._calculate_momentum(data, 30)
        momentum_10d = self._calculate_momentum(data, 10)
        momentum_deterioration = momentum_30d < -0.02 or momentum_10d < -0.03
        
        # Rotation score decline
        rotation_score = self._calculate_rotation_score(data, symbol)
        rotation_decline = rotation_score < 0.95
        
        # Overbought RSI
        rsi_overbought = latest.get('rsi', 50) > 80
        
        return weakness_condition or momentum_deterioration or rotation_decline or rsi_overbought
    
    def _calculate_confidence(self, latest: pd.Series, data: pd.DataFrame, 
                            signal_type: str, symbol: str) -> float:
        """Calculate confidence score for the signal (0-1)"""
        confidence = 0.6  # Base confidence for sector rotation
        
        relative_strength = self._calculate_relative_strength(data)
        rotation_score = self._calculate_rotation_score(data, symbol)
        momentum_30d = self._calculate_momentum(data, 30)
        
        if signal_type == 'BUY':
            # Strong relative performance
            if relative_strength > 1.10:  # 10% outperformance
                confidence += 0.25
            elif relative_strength > 1.05:  # 5% outperformance
                confidence += 0.15
            
            # High rotation score
            if rotation_score > 1.15:
                confidence += 0.2
            elif rotation_score > 1.10:
                confidence += 0.1
            
            # Strong momentum
            if momentum_30d > 0.08:  # 8% monthly momentum
                confidence += 0.15
            elif momentum_30d > 0.05:
                confidence += 0.1
            
            # Sector-specific bonuses
            sector_name = self._get_sector_name(symbol)
            if sector_name in ['Technology', 'Financials']:  # High-beta sectors
                if momentum_30d > 0.06:
                    confidence += 0.05
        
        elif signal_type == 'SELL':
            # Clear underperformance
            if relative_strength < 0.95:  # 5% underperformance
                confidence += 0.3
            elif relative_strength < 0.98:
                confidence += 0.2
            
            # Rotation score decline
            if rotation_score < 0.90:
                confidence += 0.25
            elif rotation_score < 0.95:
                confidence += 0.15
            
            # Momentum reversal
            if momentum_30d < -0.05:
                confidence += 0.2
        
        return min(confidence, 1.0)
    