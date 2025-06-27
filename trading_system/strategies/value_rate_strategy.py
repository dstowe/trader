# strategies/value_rate_strategy.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json

class ValueRateStrategy:
    """
    Value-Rate Environment Strategy
    
    Systematically exploits REITs trading 9% below fair value and 
    financial sector opportunities in the 4.25%-4.50% rate environment
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "ValueRate"
        
        # REIT universe with sector classifications
        self.reit_universe = {
            # Industrial REITs
            'PLD': {'sector': 'Industrial', 'type': 'Logistics'},
            'EXR': {'sector': 'Storage', 'type': 'Self Storage'},
            
            # Healthcare REITs  
            'PEAK': {'sector': 'Healthcare', 'type': 'Healthcare Properties'},
            'WELL': {'sector': 'Healthcare', 'type': 'Healthcare Properties'},
            'VTR': {'sector': 'Healthcare', 'type': 'Senior Housing'},
            
            # Retail REITs
            'FRT': {'sector': 'Retail', 'type': 'Shopping Centers'},
            'REG': {'sector': 'Retail', 'type': 'Shopping Centers'},
            'SPG': {'sector': 'Retail', 'type': 'Malls'},
            
            # Specialty REITs
            'CCI': {'sector': 'Infrastructure', 'type': 'Cell Towers'},
            'AMT': {'sector': 'Infrastructure', 'type': 'Cell Towers'},
            'EQIX': {'sector': 'Data Centers', 'type': 'Data Centers'},
            'DLR': {'sector': 'Data Centers', 'type': 'Data Centers'},
            
            # Office REITs
            'BXP': {'sector': 'Office', 'type': 'Office Buildings'},
            'VNO': {'sector': 'Office', 'type': 'Office Buildings'},
            
            # Residential REITs
            'EQR': {'sector': 'Residential', 'type': 'Apartments'},
            'AVB': {'sector': 'Residential', 'type': 'Apartments'},
            'MAA': {'sector': 'Residential', 'type': 'Apartments'},
            
            # REIT ETFs
            'XLRE': {'sector': 'ETF', 'type': 'Broad REIT'},
            'IYR': {'sector': 'ETF', 'type': 'Broad REIT'},
            'SCHH': {'sector': 'ETF', 'type': 'Broad REIT'},
        }
        
        # Financial universe
        self.financial_universe = {
            # Large Banks
            'JPM': {'type': 'Money Center Bank', 'rate_sensitive': 'High'},
            'BAC': {'type': 'Money Center Bank', 'rate_sensitive': 'High'},
            'WFC': {'type': 'Money Center Bank', 'rate_sensitive': 'High'},
            'C': {'type': 'Money Center Bank', 'rate_sensitive': 'High'},
            
            # Regional Banks
            'USB': {'type': 'Regional Bank', 'rate_sensitive': 'Very High'},
            'TFC': {'type': 'Regional Bank', 'rate_sensitive': 'Very High'},
            'PNC': {'type': 'Regional Bank', 'rate_sensitive': 'Very High'},
            
            # Investment Banks
            'GS': {'type': 'Investment Bank', 'rate_sensitive': 'Medium'},
            'MS': {'type': 'Investment Bank', 'rate_sensitive': 'Medium'},
            
            # Insurance
            'BRK-B': {'type': 'Insurance', 'rate_sensitive': 'Medium'},
            'AIG': {'type': 'Insurance', 'rate_sensitive': 'Medium'},
            
            # Financial ETFs
            'XLF': {'type': 'ETF', 'rate_sensitive': 'High'},
            'KBE': {'type': 'Bank ETF', 'rate_sensitive': 'Very High'},
        }
        
        # Value thresholds
        self.reit_discount_threshold = 0.10  # 10% discount to NAV
        self.ffo_yield_threshold = 0.06      # 6% FFO yield minimum
        self.payout_ratio_threshold = 0.85   # 85% max payout ratio
        
        # Financial metrics thresholds
        self.roe_threshold = 0.12           # 12% ROE minimum
        self.tier1_threshold = 0.12         # 12% Tier 1 capital minimum
        self.pb_ratio_threshold = 1.5       # 1.5x max price-to-book
        self.nim_threshold = 0.03           # 3% net interest margin minimum
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate value-rate strategy signals"""
        signals = []
        
        if symbol not in self.reit_universe and symbol not in self.financial_universe:
            return signals
            
        if len(data) < 50:
            return signals
            
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Determine asset type
        if symbol in self.reit_universe:
            signal = self._analyze_reit(data, symbol, latest)
        else:
            signal = self._analyze_financial(data, symbol, latest)
            
        if signal:
            signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(signal)
            
        return signals
    
    def _analyze_reit(self, data: pd.DataFrame, symbol: str, latest: pd.Series) -> Optional[Dict]:
        """Analyze REIT for value opportunity"""
        reit_info = self.reit_universe[symbol]
        
        # Calculate technical indicators
        sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else latest['Close']
        sma_200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else latest['Close']
        
        # Calculate momentum
        momentum_3m = self._calculate_momentum(data, 63)
        momentum_6m = self._calculate_momentum(data, 126)
        
        # Volume analysis
        volume_ratio = self._calculate_volume_ratio(data)
        
        # Yield estimation (would be from fundamental data in real implementation)
        estimated_yield = self._estimate_reit_yield(symbol)
        
        # Value assessment
        value_score = self._calculate_reit_value_score(symbol, latest['Close'], estimated_yield)
        
        # Check for entry signal
        if self._check_reit_entry(latest['Close'], sma_50, sma_200, value_score, 
                                volume_ratio, estimated_yield):
            
            confidence = self._calculate_reit_confidence(
                value_score, momentum_3m, volume_ratio, estimated_yield, reit_info)
            
            return {
                'signal_type': 'BUY',
                'confidence': confidence,
                'metadata': json.dumps({
                    'asset_type': 'REIT',
                    'reit_sector': reit_info['sector'],
                    'reit_type': reit_info['type'],
                    'estimated_yield': estimated_yield,
                    'value_score': value_score,
                    'momentum_3m': momentum_3m,
                    'momentum_6m': momentum_6m,
                    'volume_ratio': volume_ratio,
                    'sma_50': sma_50,
                    'sma_200': sma_200,
                    'price_vs_sma50': (latest['Close'] - sma_50) / sma_50,
                    'strategy_logic': 'reit_value_rate'
                })
            }
            
        # Check for exit signal
        elif self._check_reit_exit(latest['Close'], sma_50, momentum_3m, value_score):
            return {
                'signal_type': 'SELL',
                'confidence': 0.7,
                'metadata': json.dumps({
                    'asset_type': 'REIT',
                    'exit_reason': 'overvalued' if value_score < 0.3 else 'momentum_loss',
                    'reit_sector': reit_info['sector'],
                    'strategy_logic': 'reit_exit'
                })
            }
            
        return None
    
    def _analyze_financial(self, data: pd.DataFrame, symbol: str, latest: pd.Series) -> Optional[Dict]:
        """Analyze financial stock for rate environment opportunity"""
        financial_info = self.financial_universe[symbol]
        
        # Calculate technical indicators
        sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else latest['Close']
        sma_200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else latest['Close']
        
        # Calculate momentum
        momentum_3m = self._calculate_momentum(data, 63)
        momentum_6m = self._calculate_momentum(data, 126)
        
        # Volume analysis
        volume_ratio = self._calculate_volume_ratio(data)
        
        # Rate sensitivity score
        rate_sensitivity = self._get_rate_sensitivity_score(financial_info['rate_sensitive'])
        
        # Value assessment for financials
        value_score = self._calculate_financial_value_score(symbol, latest['Close'])
        
        # Check for entry signal
        if self._check_financial_entry(latest['Close'], sma_50, sma_200, value_score,
                                     volume_ratio, rate_sensitivity):
            
            confidence = self._calculate_financial_confidence(
                value_score, momentum_3m, volume_ratio, rate_sensitivity, financial_info)
            
            return {
                'signal_type': 'BUY',
                'confidence': confidence,
                'metadata': json.dumps({
                    'asset_type': 'Financial',
                    'financial_type': financial_info['type'],
                    'rate_sensitivity': financial_info['rate_sensitive'],
                    'rate_sensitivity_score': rate_sensitivity,
                    'value_score': value_score,
                    'momentum_3m': momentum_3m,
                    'momentum_6m': momentum_6m,
                    'volume_ratio': volume_ratio,
                    'sma_50': sma_50,
                    'sma_200': sma_200,
                    'price_vs_sma50': (latest['Close'] - sma_50) / sma_50,
                    'strategy_logic': 'financial_rate_value'
                })
            }
            
        # Check for exit signal
        elif self._check_financial_exit(latest['Close'], sma_50, momentum_3m, value_score):
            return {
                'signal_type': 'SELL',
                'confidence': 0.7,
                'metadata': json.dumps({
                    'asset_type': 'Financial',
                    'exit_reason': 'overvalued' if value_score < 0.3 else 'momentum_loss',
                    'financial_type': financial_info['type'],
                    'strategy_logic': 'financial_exit'
                })
            }
            
        return None
    
    def _calculate_momentum(self, data: pd.DataFrame, periods: int) -> float:
        """Calculate momentum over specified periods"""
        if len(data) < periods:
            return 0.0
            
        current_price = data['Close'].iloc[-1]
        past_price = data['Close'].iloc[-periods]
        
        return (current_price - past_price) / past_price
    
    def _calculate_volume_ratio(self, data: pd.DataFrame, periods: int = 20) -> float:
        """Calculate volume ratio vs average"""
        if len(data) < periods:
            return 1.0
            
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(periods).mean()
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def _estimate_reit_yield(self, symbol: str) -> float:
        """Estimate REIT yield (would use fundamental data in real implementation)"""
        # Estimated yields based on current market conditions and REIT type
        yield_estimates = {
            'PLD': 0.028, 'EXR': 0.035, 'PEAK': 0.070, 'WELL': 0.055,
            'VTR': 0.045, 'FRT': 0.046, 'REG': 0.040, 'SPG': 0.055,
            'CCI': 0.062, 'AMT': 0.032, 'EQIX': 0.025, 'DLR': 0.030,
            'BXP': 0.065, 'VNO': 0.070, 'EQR': 0.038, 'AVB': 0.035,
            'MAA': 0.042, 'XLRE': 0.040, 'IYR': 0.038, 'SCHH': 0.039
        }
        
        return yield_estimates.get(symbol, 0.045)  # Default 4.5%
    
    def _calculate_reit_value_score(self, symbol: str, price: float, yield_rate: float) -> float:
        """Calculate REIT value score (0-1, higher is better value)"""
        reit_info = self.reit_universe[symbol]
        
        score = 0.5  # Base score
        
        # Yield component (higher yield = better value)
        if yield_rate > 0.06:  # 6%+ yield
            score += 0.3
        elif yield_rate > 0.04:  # 4%+ yield
            score += 0.2
        elif yield_rate > 0.03:  # 3%+ yield
            score += 0.1
            
        # Sector-specific adjustments based on current market conditions
        sector_adjustments = {
            'Industrial': 0.1,    # Strong e-commerce tailwinds
            'Healthcare': 0.15,   # 37% undervaluation mentioned
            'Infrastructure': 0.1, # 5G and data growth
            'Data Centers': 0.1,  # AI and cloud growth
            'Storage': 0.05,      # Steady demand
            'Retail': -0.1,       # Challenged sector
            'Office': -0.2,       # Work-from-home impact
            'ETF': 0.0            # Neutral for broad exposure
        }
        
        sector_adj = sector_adjustments.get(reit_info['sector'], 0)
        score += sector_adj
        
        return max(0.1, min(1.0, score))
    
    def _calculate_financial_value_score(self, symbol: str, price: float) -> float:
        """Calculate financial value score"""
        financial_info = self.financial_universe[symbol]
        
        score = 0.5  # Base score
        
        # Rate environment benefit (higher rates help financials)
        current_rate_environment = 4.375  # Mid-point of 4.25%-4.50% range
        if current_rate_environment > 4.0:
            score += 0.2
        elif current_rate_environment > 3.0:
            score += 0.1
            
        # Type-specific adjustments
        type_adjustments = {
            'Money Center Bank': 0.1,    # Diversified revenue
            'Regional Bank': 0.15,       # Higher rate sensitivity
            'Investment Bank': 0.05,     # Market-dependent
            'Insurance': 0.1,            # Higher rates help reserves
            'ETF': 0.05,                # Broad exposure
            'Bank ETF': 0.12            # Pure rate play
        }
        
        type_adj = type_adjustments.get(financial_info['type'], 0)
        score += type_adj
        
        return max(0.1, min(1.0, score))
    
    def _get_rate_sensitivity_score(self, sensitivity: str) -> float:
        """Convert rate sensitivity to numeric score"""
        sensitivity_scores = {
            'Very High': 1.0,
            'High': 0.8,
            'Medium': 0.6,
            'Low': 0.4
        }
        return sensitivity_scores.get(sensitivity, 0.6)
    
    def _check_reit_entry(self, price: float, sma_50: float, sma_200: float,
                        value_score: float, volume_ratio: float, yield_rate: float) -> bool:
        """Check REIT entry conditions"""
        # Must be good value
        if value_score < 0.6:
            return False
            
        # Must have decent yield
        if yield_rate < 0.03:
            return False
            
        # Technical conditions
        if price < sma_200 * 0.85:  # Don't catch falling knives
            return False
            
        # Price near or above 50-day SMA (momentum building)
        if price < sma_50 * 0.95:
            return False
            
        # Volume confirmation
        if volume_ratio < 1.2:
            return False
            
        return True
    
    def _check_reit_exit(self, price: float, sma_50: float, momentum_3m: float,
                       value_score: float) -> bool:
        """Check REIT exit conditions"""
        # Exit if overvalued
        if value_score < 0.3:
            return True
            
        # Exit if momentum deteriorates
        if momentum_3m < -0.10:  # -10% momentum
            return True
            
        # Exit if breaks below 50-day SMA by significant margin
        if price < sma_50 * 0.92:  # 8% below SMA
            return True
            
        return False
    
    def _check_financial_entry(self, price: float, sma_50: float, sma_200: float,
                             value_score: float, volume_ratio: float, 
                             rate_sensitivity: float) -> bool:
        """Check financial entry conditions"""
        # Must be good value
        if value_score < 0.6:
            return False
            
        # Technical conditions
        if price < sma_200 * 0.90:  # Not too oversold
            return False
            
        # Price above 50-day SMA (momentum)
        if price < sma_50 * 0.98:
            return False
            
        # Volume confirmation
        if volume_ratio < 1.1:
            return False
            
        return True
    
    def _check_financial_exit(self, price: float, sma_50: float, momentum_3m: float,
                            value_score: float) -> bool:
        """Check financial exit conditions"""
        # Exit if overvalued
        if value_score < 0.4:
            return True
            
        # Exit if momentum deteriorates
        if momentum_3m < -0.08:  # -8% momentum
            return True
            
        # Exit if breaks below 50-day SMA
        if price < sma_50 * 0.95:  # 5% below SMA
            return True
            
        return False
    
    def _calculate_reit_confidence(self, value_score: float, momentum: float,
                                 volume_ratio: float, yield_rate: float,
                                 reit_info: Dict) -> float:
        """Calculate confidence for REIT signals"""
        confidence = 0.5
        
        # Value component
        if value_score > 0.8:
            confidence += 0.3
        elif value_score > 0.7:
            confidence += 0.2
        elif value_score > 0.6:
            confidence += 0.1
            
        # Yield component
        if yield_rate > 0.06:
            confidence += 0.2
        elif yield_rate > 0.04:
            confidence += 0.1
            
        # Momentum component
        if momentum > 0.05:
            confidence += 0.1
        elif momentum > 0:
            confidence += 0.05
            
        # Volume component
        if volume_ratio > 1.5:
            confidence += 0.1
            
        # Sector premium for best sectors
        if reit_info['sector'] in ['Healthcare', 'Industrial', 'Infrastructure']:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _calculate_financial_confidence(self, value_score: float, momentum: float,
                                      volume_ratio: float, rate_sensitivity: float,
                                      financial_info: Dict) -> float:
        """Calculate confidence for financial signals"""
        confidence = 0.5
        
        # Value component
        if value_score > 0.8:
            confidence += 0.2
        elif value_score > 0.7:
            confidence += 0.15
        elif value_score > 0.6:
            confidence += 0.1
            
        # Rate sensitivity (higher is better in current environment)
        if rate_sensitivity > 0.8:
            confidence += 0.2
        elif rate_sensitivity > 0.6:
            confidence += 0.1
            
        # Momentum component
        if momentum > 0.03:
            confidence += 0.1
        elif momentum > 0:
            confidence += 0.05
            
        # Volume component
        if volume_ratio > 1.3:
            confidence += 0.1
            
        # Type premium for regional banks (highest rate sensitivity)
        if financial_info['type'] == 'Regional Bank':
            confidence += 0.1
            
        return min(confidence, 1.0)