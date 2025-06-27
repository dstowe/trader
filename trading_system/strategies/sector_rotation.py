# strategies/sector_rotation.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class SectorRotationStrategy:
    """
    Volatility-Adjusted Sector Rotation Strategy
    
    Systematically rotates between sectors based on momentum ranking
    with dynamic volatility scaling for 2025 market conditions
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "SectorRotation"
        
        # Sector ETFs for rotation
        self.sectors = {
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
        
        # Target sectors ranked 4-6 in momentum
        self.target_rank_min = 4
        self.target_rank_max = 6
        
        # Volatility thresholds
        self.vix_exit_threshold = 30
        self.vix_scale_threshold = 25
        self.sector_vol_multiplier = 1.5
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate sector rotation signals based on momentum and volatility"""
        signals = []
        
        if symbol not in self.sectors:
            return signals
            
        if len(data) < 63:  # Need 3 months of data
            return signals
            
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Calculate momentum scores
        momentum_1m = self._calculate_momentum(data, 21)  # 1 month
        momentum_3m = self._calculate_momentum(data, 63)  # 3 months
        combined_momentum = (momentum_1m * 0.6) + (momentum_3m * 0.4)
        
        # Calculate current volatility
        current_volatility = self._calculate_volatility(data)
        historical_volatility = self._calculate_historical_volatility(data)
        vol_ratio = current_volatility / historical_volatility if historical_volatility > 0 else 1.0
        
        # Get VIX level (would need to be passed from main system)
        vix_level = getattr(self.config, 'CURRENT_VIX_LEVEL', 20)
        
        # Determine if we should trade this sector
        should_enter = self._should_enter_sector(combined_momentum, vol_ratio, vix_level)
        should_exit = self._should_exit_sector(combined_momentum, vol_ratio, vix_level)
        
        if should_enter:
            confidence = self._calculate_confidence(combined_momentum, vol_ratio, 'BUY')
            position_scale = self._calculate_position_scale(vol_ratio, vix_level)
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'BUY',
                'price': latest['Close'],
                'confidence': confidence,
                'metadata': json.dumps({
                    'momentum_1m': momentum_1m,
                    'momentum_3m': momentum_3m,
                    'combined_momentum': combined_momentum,
                    'volatility_ratio': vol_ratio,
                    'position_scale': position_scale,
                    'vix_level': vix_level,
                    'sector_name': self.sectors[symbol],
                    'strategy_logic': 'sector_rotation_momentum'
                })
            })
            
        elif should_exit:
            confidence = self._calculate_confidence(combined_momentum, vol_ratio, 'SELL')
            
            signals.append({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'signal_type': 'SELL',
                'price': latest['Close'],
                'confidence': confidence,
                'metadata': json.dumps({
                    'momentum_1m': momentum_1m,
                    'momentum_3m': momentum_3m,
                    'combined_momentum': combined_momentum,
                    'volatility_ratio': vol_ratio,
                    'vix_level': vix_level,
                    'exit_reason': 'momentum_deterioration' if combined_momentum < 0 else 'vix_spike',
                    'sector_name': self.sectors[symbol],
                    'strategy_logic': 'sector_rotation_exit'
                })
            })
            
        return signals
    
    def _calculate_momentum(self, data: pd.DataFrame, periods: int) -> float:
        """Calculate momentum over specified periods"""
        if len(data) < periods:
            return 0.0
            
        current_price = data['Close'].iloc[-1]
        past_price = data['Close'].iloc[-periods]
        
        return (current_price - past_price) / past_price
    
    def _calculate_volatility(self, data: pd.DataFrame, periods: int = 20) -> float:
        """Calculate current volatility (20-day rolling)"""
        if len(data) < periods:
            return 0.0
            
        returns = data['Close'].pct_change().dropna()
        return returns.tail(periods).std() * np.sqrt(252)  # Annualized
    
    def _calculate_historical_volatility(self, data: pd.DataFrame, periods: int = 63) -> float:
        """Calculate historical average volatility (3-month average)"""
        if len(data) < periods:
            return 0.0
            
        returns = data['Close'].pct_change().dropna()
        return returns.tail(periods).std() * np.sqrt(252)  # Annualized
    
    def _should_enter_sector(self, momentum: float, vol_ratio: float, vix_level: float) -> bool:
        """Determine if we should enter this sector"""
        # Basic momentum filter - positive momentum
        if momentum <= 0:
            return False
            
        # VIX filter - don't enter during crisis conditions
        if vix_level > self.vix_exit_threshold:
            return False
            
        # Volume ratio filter - don't enter if volatility too high
        if vol_ratio > self.sector_vol_multiplier:
            return False
            
        # Momentum strength filter - require meaningful momentum
        if momentum < 0.02:  # 2% minimum momentum
            return False
            
        return True
    
    def _should_exit_sector(self, momentum: float, vol_ratio: float, vix_level: float) -> bool:
        """Determine if we should exit this sector"""
        # Exit if momentum turns negative
        if momentum < -0.01:  # -1% momentum threshold
            return True
            
        # Exit if VIX spikes indicating regime change
        if vix_level > self.vix_exit_threshold:
            return True
            
        # Exit if volatility becomes excessive
        if vol_ratio > 2.0:  # 2x historical volatility
            return True
            
        return False
    
    def _calculate_confidence(self, momentum: float, vol_ratio: float, signal_type: str) -> float:
        """Calculate confidence score for the signal"""
        confidence = 0.5  # Base confidence
        
        if signal_type == 'BUY':
            # Higher confidence for stronger momentum
            if momentum > 0.05:  # 5%+ momentum
                confidence += 0.3
            elif momentum > 0.02:  # 2%+ momentum
                confidence += 0.2
                
            # Lower confidence for high volatility
            if vol_ratio > 1.2:
                confidence -= 0.2
            elif vol_ratio < 0.8:  # Low volatility is good
                confidence += 0.1
                
        elif signal_type == 'SELL':
            # Higher confidence for momentum breakdown
            if momentum < -0.05:
                confidence += 0.3
            elif momentum < -0.02:
                confidence += 0.2
                
            # Higher confidence for volatility spike
            if vol_ratio > 1.5:
                confidence += 0.2
                
        return min(max(confidence, 0.1), 1.0)
    
    def _calculate_position_scale(self, vol_ratio: float, vix_level: float) -> float:
        """Calculate position scaling factor based on volatility"""
        scale = 1.0
        
        # Scale down for high sector volatility
        if vol_ratio > 1.5:
            scale *= 0.5
        elif vol_ratio > 1.2:
            scale *= 0.75
            
        # Scale down for high VIX
        if vix_level > self.vix_scale_threshold:
            vix_scale = max(0.25, 1.0 - ((vix_level - self.vix_scale_threshold) / 20))
            scale *= vix_scale
            
        return scale
    
    def rank_sectors(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """Rank all sectors by combined momentum score"""
        sector_scores = {}
        
        for symbol, data in sector_data.items():
            if symbol not in self.sectors or len(data) < 63:
                continue
                
            momentum_1m = self._calculate_momentum(data, 21)
            momentum_3m = self._calculate_momentum(data, 63)
            combined_momentum = (momentum_1m * 0.6) + (momentum_3m * 0.4)
            
            sector_scores[symbol] = combined_momentum
        
        # Rank sectors (1 = highest momentum)
        sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
        rankings = {}
        for rank, (symbol, score) in enumerate(sorted_sectors, 1):
            rankings[symbol] = rank
            
        return rankings
    
    def get_target_sectors(self, sector_data: Dict[str, pd.DataFrame]) -> List[str]:
        """Get sectors currently in target rank range (4-6)"""
        rankings = self.rank_sectors(sector_data)
        
        target_sectors = []
        for symbol, rank in rankings.items():
            if self.target_rank_min <= rank <= self.target_rank_max:
                target_sectors.append(symbol)
                
        return target_sectors
    
    def calculate_sector_allocation(self, account_value: float, vix_level: float) -> Dict[str, float]:
        """Calculate optimal allocation across sectors"""
        base_allocation = account_value * 0.20  # 20% max in sector rotation
        
        # Scale down allocation based on VIX
        if vix_level > self.vix_scale_threshold:
            vix_scale = max(0.25, 1.0 - ((vix_level - self.vix_scale_threshold) / 20))
            base_allocation *= vix_scale
            
        # Divide equally among target sectors (typically 3 sectors)
        per_sector_allocation = base_allocation / 3
        
        return {
            'total_allocation': base_allocation,
            'per_sector': per_sector_allocation,
            'max_sectors': 3
        }