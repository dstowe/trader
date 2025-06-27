# strategies/international_strategy.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class InternationalStrategy:
    """
    International Market Outperformance Strategy
    
    Capitalizes on MSCI EAFE's +11.21% YTD outperformance vs US -0.25%
    through systematic international exposure and currency considerations
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "International"
        
        # International ETF universe
        self.international_etfs = {
            # Broad International
            'VEA': {'name': 'FTSE Developed Markets', 'region': 'Developed', 'hedged': False},
            'EFA': {'name': 'MSCI EAFE', 'region': 'Developed', 'hedged': False},
            'VXUS': {'name': 'Total International Stock', 'region': 'All', 'hedged': False},
            'IEFA': {'name': 'Core MSCI EAFE', 'region': 'Developed', 'hedged': False},
            
            # Currency Hedged
            'HEFA': {'name': 'Currency Hedged MSCI EAFE', 'region': 'Developed', 'hedged': True},
            'HEDJ': {'name': 'Currency Hedged Europe', 'region': 'Europe', 'hedged': True},
            
            # Regional
            'VGK': {'name': 'FTSE Europe', 'region': 'Europe', 'hedged': False},
            'EWJ': {'name': 'MSCI Japan', 'region': 'Japan', 'hedged': False},
            'EEMA': {'name': 'MSCI Emerging Markets Asia', 'region': 'Asia', 'hedged': False},
            'VWO': {'name': 'FTSE Emerging Markets', 'region': 'Emerging', 'hedged': False},
            
            # Specific Countries
            'EWG': {'name': 'Germany ETF', 'region': 'Germany', 'hedged': False},
            'EWU': {'name': 'United Kingdom ETF', 'region': 'UK', 'hedged': False},
            'EWY': {'name': 'South Korea ETF', 'region': 'Korea', 'hedged': False},
            'INDA': {'name': 'India ETF', 'region': 'India', 'hedged': False},
        }
        
        # Performance thresholds
        self.outperformance_threshold = 0.02  # 2% outperformance vs SPY
        self.min_volume_ratio = 1.2
        self.momentum_period = 63  # 3-month momentum
        
        # Currency considerations
        self.dxy_strong_threshold = 105  # DXY level for hedging consideration
        self.dxy_weak_threshold = 100    # DXY level favoring unhedged
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate international investment signals"""
        signals = []
        
        if symbol not in self.international_etfs:
            return signals
            
        if len(data) < self.momentum_period:
            return signals
            
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Calculate performance metrics
        momentum = self._calculate_momentum(data)
        relative_strength = self._calculate_relative_strength(data, symbol)
        volume_trend = self._calculate_volume_trend(data)
        
        # Get currency environment
        currency_environment = self._assess_currency_environment(symbol)
        
        # Check for entry signal
        entry_signal = self._check_entry_signal(
            data, latest, momentum, relative_strength, volume_trend, currency_environment)
        
        if entry_signal:
            entry_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(entry_signal)
            
        # Check for exit signal
        exit_signal = self._check_exit_signal(
            data, latest, momentum, relative_strength, currency_environment)
        
        if exit_signal:
            exit_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(exit_signal)
            
        return signals
    
    def _calculate_momentum(self, data: pd.DataFrame) -> Dict:
        """Calculate various momentum metrics"""
        current_price = data['Close'].iloc[-1]
        
        # 1-month momentum
        momentum_1m = (current_price / data['Close'].iloc[-21] - 1) if len(data) >= 21 else 0
        
        # 3-month momentum
        momentum_3m = (current_price / data['Close'].iloc[-63] - 1) if len(data) >= 63 else 0
        
        # 6-month momentum
        momentum_6m = (current_price / data['Close'].iloc[-126] - 1) if len(data) >= 126 else 0
        
        # Combined momentum score
        combined = (momentum_1m * 0.5) + (momentum_3m * 0.3) + (momentum_6m * 0.2)
        
        return {
            '1m': momentum_1m,
            '3m': momentum_3m,
            '6m': momentum_6m,
            'combined': combined
        }
    
    def _calculate_relative_strength(self, data: pd.DataFrame, symbol: str) -> float:
        """Calculate relative strength vs SPY (would need SPY data)"""
        # In a real implementation, this would compare against SPY data
        # For now, use absolute momentum as proxy
        if len(data) < 63:
            return 0.0
            
        # Calculate 3-month performance
        performance = (data['Close'].iloc[-1] / data['Close'].iloc[-63]) - 1
        
        # Assume SPY baseline performance (would be actual SPY data in real implementation)
        spy_baseline = -0.0025  # -0.25% YTD as mentioned in context
        
        return performance - spy_baseline
    
    def _calculate_volume_trend(self, data: pd.DataFrame) -> float:
        """Calculate volume trend"""
        if len(data) < 20:
            return 1.0
            
        recent_volume = data['Volume'].tail(10).mean()
        historical_volume = data['Volume'].tail(50).mean()
        
        return recent_volume / historical_volume if historical_volume > 0 else 1.0
    
    def _assess_currency_environment(self, symbol: str) -> Dict:
        """Assess currency environment for hedging decisions"""
        etf_info = self.international_etfs[symbol]
        
        # This would ideally use real DXY data
        # For now, simulate based on current environment (USD weakness)
        estimated_dxy = 102  # Current estimate - USD slightly weak
        
        currency_assessment = {
            'dxy_level': estimated_dxy,
            'usd_environment': 'weak' if estimated_dxy < self.dxy_weak_threshold else 
                              'strong' if estimated_dxy > self.dxy_strong_threshold else 'neutral',
            'favor_hedged': estimated_dxy > self.dxy_strong_threshold,
            'favor_unhedged': estimated_dxy < self.dxy_weak_threshold,
            'is_hedged_etf': etf_info['hedged']
        }
        
        return currency_assessment
    
    def _check_entry_signal(self, data: pd.DataFrame, latest: pd.Series,
                          momentum: Dict, relative_strength: float,
                          volume_trend: float, currency_env: Dict) -> Optional[Dict]:
        """Check for international entry signal"""
        
        # Must show outperformance vs US markets
        if relative_strength < self.outperformance_threshold:
            return None
            
        # Must have positive momentum
        if momentum['combined'] <= 0:
            return None
            
        # Volume confirmation
        if volume_trend < self.min_volume_ratio:
            return None
            
        # Currency environment check
        etf_info = self.international_etfs.get(latest.name, {})
        currency_favorable = self._is_currency_favorable(currency_env)
        
        if not currency_favorable:
            return None
            
        # Technical confirmation
        sma_20 = data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else sma_20
        
        # Price above moving averages
        price_above_sma = latest['Close'] > sma_20 and latest['Close'] > sma_50
        
        if price_above_sma:
            confidence = self._calculate_entry_confidence(
                momentum, relative_strength, volume_trend, currency_env)
            
            # Calculate position sizing
            allocation = self._calculate_allocation(latest.name, relative_strength)
            
            return {
                'signal_type': 'BUY',
                'confidence': confidence,
                'metadata': json.dumps({
                    'momentum_1m': momentum['1m'],
                    'momentum_3m': momentum['3m'],
                    'momentum_6m': momentum['6m'],
                    'combined_momentum': momentum['combined'],
                    'relative_strength': relative_strength,
                    'volume_trend': volume_trend,
                    'dxy_level': currency_env['dxy_level'],
                    'usd_environment': currency_env['usd_environment'],
                    'currency_favorable': currency_favorable,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'recommended_allocation': allocation,
                    'etf_region': etf_info.get('region', 'Unknown'),
                    'strategy_logic': 'international_outperformance'
                })
            }
            
        return None
    
    def _check_exit_signal(self, data: pd.DataFrame, latest: pd.Series,
                         momentum: Dict, relative_strength: float,
                         currency_env: Dict) -> Optional[Dict]:
        """Check for international exit signal"""
        
        # Exit if momentum deteriorates significantly
        if momentum['combined'] < -0.03:  # -3% combined momentum
            return self._create_exit_signal(latest.name, 'momentum_deterioration', 0.8)
            
        # Exit if relative strength turns negative
        if relative_strength < -0.02:  # -2% underperformance
            return self._create_exit_signal(latest.name, 'relative_weakness', 0.7)
            
        # Exit if currency environment becomes very unfavorable
        if not self._is_currency_favorable(currency_env) and currency_env['dxy_level'] > 110:
            return self._create_exit_signal(latest.name, 'currency_headwinds', 0.6)
            
        # Technical exit - break below 50-day SMA
        if len(data) >= 50:
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            if latest['Close'] < sma_50 * 0.95:  # 5% below 50-day SMA
                return self._create_exit_signal(latest.name, 'technical_breakdown', 0.7)
                
        return None
    
    def _create_exit_signal(self, symbol: str, reason: str, confidence: float) -> Dict:
        """Create standardized exit signal"""
        etf_info = self.international_etfs.get(symbol, {})
        
        return {
            'signal_type': 'SELL',
            'confidence': confidence,
            'metadata': json.dumps({
                'exit_reason': reason,
                'etf_region': etf_info.get('region', 'Unknown'),
                'strategy_logic': 'international_exit'
            })
        }
    
    def _is_currency_favorable(self, currency_env: Dict) -> bool:
        """Determine if currency environment is favorable for this ETF"""
        # For unhedged ETFs, favor when USD is weak (currency tailwind)
        # For hedged ETFs, neutral to currency environment
        
        if currency_env['is_hedged_etf']:
            return True  # Hedged ETFs are currency-neutral
            
        # Unhedged ETFs benefit from USD weakness
        return currency_env['usd_environment'] in ['weak', 'neutral']
    
    def _calculate_entry_confidence(self, momentum: Dict, relative_strength: float,
                                  volume_trend: float, currency_env: Dict) -> float:
        """Calculate confidence for entry signals"""
        confidence = 0.5
        
        # Strong momentum
        if momentum['combined'] > 0.05:
            confidence += 0.2
        elif momentum['combined'] > 0.03:
            confidence += 0.1
            
        # Strong relative performance
        if relative_strength > 0.05:
            confidence += 0.2
        elif relative_strength > 0.03:
            confidence += 0.1
            
        # Volume confirmation
        if volume_trend > 1.5:
            confidence += 0.1
            
        # Favorable currency environment
        if currency_env['favor_unhedged'] and not currency_env['is_hedged_etf']:
            confidence += 0.1
        elif currency_env['is_hedged_etf']:
            confidence += 0.05  # Slight preference for hedged in uncertain times
            
        return min(confidence, 1.0)
    
    def _calculate_allocation(self, symbol: str, relative_strength: float) -> Dict:
        """Calculate recommended allocation for international positions"""
        etf_info = self.international_etfs[symbol]
        
        # Base allocation depends on ETF type
        if etf_info['region'] == 'Developed':
            base_allocation = 0.20  # 20% for broad developed markets
        elif etf_info['region'] == 'Emerging':
            base_allocation = 0.10  # 10% for emerging markets
        elif etf_info['region'] in ['Europe', 'Japan']:
            base_allocation = 0.15  # 15% for major regions
        else:
            base_allocation = 0.05  # 5% for country-specific
            
        # Adjust based on relative strength
        strength_multiplier = 1.0 + min(relative_strength * 2, 0.5)  # Max 50% increase
        adjusted_allocation = base_allocation * strength_multiplier
        
        return {
            'base_allocation': base_allocation,
            'adjusted_allocation': min(adjusted_allocation, 0.30),  # Cap at 30%
            'strength_multiplier': strength_multiplier
        }
    
    def get_recommended_portfolio(self, account_value: float) -> Dict:
        """Get recommended international portfolio allocation"""
        
        # Conservative allocation for international exposure
        total_international = min(account_value * 0.30, account_value)  # Max 30%
        
        recommended_positions = {
            'VEA': total_international * 0.40,   # 40% to broad developed (12% of total)
            'VWO': total_international * 0.20,   # 20% to emerging (6% of total)
            'VGK': total_international * 0.25,   # 25% to Europe (7.5% of total)
            'EWJ': total_international * 0.15,   # 15% to Japan (4.5% of total)
        }
        
        return {
            'total_allocation': total_international,
            'individual_positions': recommended_positions,
            'allocation_percentage': 30.0,
            'currency_hedging_ratio': 0.25  # 25% hedged for diversification
        }
    
    def monitor_currency_hedging(self, current_dxy: float) -> Dict:
        """Monitor and recommend currency hedging adjustments"""
        
        hedging_recommendation = {
            'current_dxy': current_dxy,
            'recommended_hedged_ratio': 0.25,  # Default 25%
            'action': 'hold'
        }
        
        if current_dxy > self.dxy_strong_threshold:
            # Strong USD - increase hedging
            hedging_recommendation.update({
                'recommended_hedged_ratio': 0.50,
                'action': 'increase_hedging',
                'reasoning': 'Strong USD environment favors currency hedging'
            })
        elif current_dxy < self.dxy_weak_threshold:
            # Weak USD - reduce hedging
            hedging_recommendation.update({
                'recommended_hedged_ratio': 0.10,
                'action': 'reduce_hedging',
                'reasoning': 'Weak USD environment favors unhedged exposure'
            })
            
        return hedging_recommendation