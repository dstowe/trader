# ai/market_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

class MarketConditionAnalyzer:
    """
    AI-powered market condition analyzer with gap environment detection
    Determines current market regime and recommends optimal strategy
    """
    
    def __init__(self):
        self.market_conditions = {
            'TRENDING': 'Use momentum strategies',
            'RANGE_BOUND': 'Use mean reversion strategies (Bollinger Bands)',
            'HIGH_VOLATILITY': 'Use volatility-based strategies',
            'LOW_VOLATILITY': 'Use covered calls and income strategies',
            'HIGH_GAP_ENVIRONMENT': 'Use gap trading strategies'
        }
    
    def analyze_market_condition(self, spy_data: pd.DataFrame, 
                               vix_data: pd.DataFrame = None) -> Dict:
        """
        Analyze current market conditions
        
        Args:
            spy_data: SPY price data
            vix_data: VIX data (optional)
            
        Returns:
            Dictionary with market condition analysis
        """
        if len(spy_data) < 50:
            return self._default_condition()
        
        # Calculate market features
        features = self._calculate_market_features(spy_data, vix_data)
        
        # Determine market condition
        condition = self._classify_market_condition(features)
        
        # Calculate confidence
        confidence = self._calculate_condition_confidence(features)
        
        # Get recommended strategy
        recommended_strategy = self._get_recommended_strategy(condition, features)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'condition': condition,
            'market_trend': features['trend'],
            'vix_level': features.get('vix_level', 20),
            'recommended_strategy': recommended_strategy,
            'confidence': confidence,
            'features': features
        }
    
    def detect_gap_environment(self, stock_data_dict: Dict[str, pd.DataFrame], 
                             config) -> Dict:
        """
        Detect if current market environment is favorable for gap trading
        
        Args:
            stock_data_dict: Dictionary of stock symbols to their dataframes
            config: TradingConfig object
            
        Returns:
            Dictionary with gap environment analysis
        """
        from indicators.technical import TechnicalIndicators
        
        gap_stats = {
            'total_stocks': 0,
            'stocks_with_gaps': 0,
            'significant_gaps': 0,
            'average_gap_size': 0,
            'high_volume_gaps': 0,
            'gap_frequency': 0,
            'is_high_gap_day': False,
            'gap_environment_score': 0
        }
        
        total_gap_size = 0
        gap_stocks = []
        
        for symbol, data in stock_data_dict.items():
            if len(data) < 2:
                continue
                
            gap_stats['total_stocks'] += 1
            
            # Calculate gap for latest day
            gap_percent = TechnicalIndicators.detect_gaps(data).iloc[-1]
            volume_ratio = TechnicalIndicators.gap_volume_ratio(data).iloc[-1]
            
            if abs(gap_percent) >= config.GAP_MIN_SIZE:
                gap_stats['stocks_with_gaps'] += 1
                total_gap_size += abs(gap_percent)
                
                gap_classification = TechnicalIndicators.classify_gap(gap_percent, volume_ratio)
                gap_stocks.append({
                    'symbol': symbol,
                    'gap_size': abs(gap_percent),
                    'gap_direction': gap_classification['direction'],
                    'quality': gap_classification['quality']
                })
                
                if abs(gap_percent) >= config.GAP_MIN_SIZE * 2:  # 2% or larger
                    gap_stats['significant_gaps'] += 1
                
                if volume_ratio >= config.GAP_VOLUME_MULTIPLIER:
                    gap_stats['high_volume_gaps'] += 1
        
        # Calculate statistics
        if gap_stats['total_stocks'] > 0:
            gap_stats['gap_frequency'] = gap_stats['stocks_with_gaps'] / gap_stats['total_stocks']
            
        if gap_stats['stocks_with_gaps'] > 0:
            gap_stats['average_gap_size'] = total_gap_size / gap_stats['stocks_with_gaps']
        
        # Determine if it's a high gap environment
        gap_stats['is_high_gap_day'] = (
            gap_stats['gap_frequency'] >= config.GAP_ENVIRONMENT_THRESHOLD or
            gap_stats['significant_gaps'] >= 3 or
            gap_stats['high_volume_gaps'] >= 2
        )
        
        # Calculate gap environment score (0-1)
        score = 0
        score += min(gap_stats['gap_frequency'] * 2, 0.4)  # Max 0.4 for frequency
        score += min(gap_stats['significant_gaps'] * 0.1, 0.3)  # Max 0.3 for significant gaps
        score += min(gap_stats['high_volume_gaps'] * 0.15, 0.3)  # Max 0.3 for volume
        gap_stats['gap_environment_score'] = min(score, 1.0)
        
        gap_stats['gap_stocks'] = gap_stocks
        
        return gap_stats
    
    def analyze_market_with_gaps(self, spy_data: pd.DataFrame, 
                               stock_data_dict: Dict[str, pd.DataFrame],
                               config, vix_data: pd.DataFrame = None) -> Dict:
        """
        Enhanced market analysis including gap environment detection
        
        Args:
            spy_data: SPY price data
            stock_data_dict: Dictionary of all stock data
            config: TradingConfig object
            vix_data: VIX data (optional)
            
        Returns:
            Enhanced market condition analysis with gap environment
        """
        # Get base market analysis
        market_analysis = self.analyze_market_condition(spy_data, vix_data)
        
        # Add gap environment analysis
        gap_analysis = self.detect_gap_environment(stock_data_dict, config)
        
        # Override strategy recommendation if high gap environment
        if gap_analysis['is_high_gap_day']:
            market_analysis['recommended_strategy'] = 'GapTrading'
            market_analysis['gap_environment'] = True
            market_analysis['condition'] = 'HIGH_GAP_ENVIRONMENT'
        else:
            market_analysis['gap_environment'] = False
        
        # Add gap statistics to output
        market_analysis['gap_stats'] = gap_analysis
        
        return market_analysis
    
    def _calculate_market_features(self, spy_data: pd.DataFrame, 
                                 vix_data: pd.DataFrame = None) -> Dict:
        """Calculate features for market condition analysis"""
        close_prices = spy_data['Close']
        
        # Trend features
        sma_20 = close_prices.rolling(20).mean()
        sma_50 = close_prices.rolling(50).mean()
        trend_strength = (close_prices.iloc[-1] - sma_20.iloc[-1]) / sma_20.iloc[-1]
        
        # Volatility features
        returns = close_prices.pct_change().dropna()
        volatility_20d = returns.tail(20).std() * np.sqrt(252)  # Annualized
        
        # Range-bound detection
        high_20d = spy_data['High'].tail(20).max()
        low_20d = spy_data['Low'].tail(20).min()
        current_price = close_prices.iloc[-1]
        range_position = (current_price - low_20d) / (high_20d - low_20d)
        
        # Momentum features
        momentum_5d = (close_prices.iloc[-1] / close_prices.iloc[-6]) - 1
        momentum_20d = (close_prices.iloc[-1] / close_prices.iloc[-21]) - 1
        
        # Volume analysis
        avg_volume = spy_data['Volume'].tail(20).mean()
        recent_volume = spy_data['Volume'].tail(5).mean()
        volume_ratio = recent_volume / avg_volume
        
        # VIX level (if available)
        vix_level = 20  # Default
        if vix_data is not None and not vix_data.empty:
            vix_level = vix_data['Close'].iloc[-1]
        
        # Market trend classification
        if close_prices.iloc[-1] > sma_20.iloc[-1] > sma_50.iloc[-1]:
            trend = 'BULLISH'
        elif close_prices.iloc[-1] < sma_20.iloc[-1] < sma_50.iloc[-1]:
            trend = 'BEARISH'
        else:
            trend = 'SIDEWAYS'
        
        return {
            'trend_strength': trend_strength,
            'volatility_20d': volatility_20d,
            'range_position': range_position,
            'momentum_5d': momentum_5d,
            'momentum_20d': momentum_20d,
            'volume_ratio': volume_ratio,
            'vix_level': vix_level,
            'trend': trend,
            'current_price': current_price,
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1]
        }
    
    def _classify_market_condition(self, features: Dict) -> str:
        """Classify market condition based on features"""
        # High volatility condition
        if features['volatility_20d'] > 0.25 or features['vix_level'] > 30:
            return 'HIGH_VOLATILITY'
        
        # Low volatility condition
        if features['volatility_20d'] < 0.15 and features['vix_level'] < 15:
            return 'LOW_VOLATILITY'
        
        # Trending condition
        if abs(features['momentum_20d']) > 0.05 and abs(features['trend_strength']) > 0.03:
            return 'TRENDING'
        
        # Range-bound condition (default for 2025 market)
        return 'RANGE_BOUND'
    
    def _calculate_condition_confidence(self, features: Dict) -> float:
        """Calculate confidence in the market condition classification"""
        base_confidence = 0.6
        
        # Higher confidence for extreme readings
        if features['vix_level'] > 35 or features['vix_level'] < 12:
            base_confidence += 0.2
        
        if features['volatility_20d'] > 0.3 or features['volatility_20d'] < 0.1:
            base_confidence += 0.15
        
        if abs(features['momentum_20d']) > 0.08:
            base_confidence += 0.1
        
        return min(base_confidence, 0.95)
    
    def _get_recommended_strategy(self, condition: str, features: Dict) -> str:
        """Get recommended trading strategy based on market condition"""
        strategy_map = {
            'RANGE_BOUND': 'BollingerMeanReversion',
            'HIGH_VOLATILITY': 'IronCondor',
            'LOW_VOLATILITY': 'CoveredCall',
            'TRENDING': 'Momentum'
        }
        
        # Special case for 2025 market conditions
        if features['vix_level'] > 25 and condition == 'RANGE_BOUND':
            return 'BollingerMeanReversion'  # Perfect for current market
        
        return strategy_map.get(condition, 'BollingerMeanReversion')
    
    def _default_condition(self) -> Dict:
        """Return default market condition when insufficient data"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'condition': 'RANGE_BOUND',
            'market_trend': 'SIDEWAYS',
            'vix_level': 20,
            'recommended_strategy': 'BollingerMeanReversion',
            'confidence': 0.5
        }
