# trading_system/strategies/strategy_selector.py
"""
Strategy Selector - Intelligent strategy selection based on market conditions
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class MarketCondition(Enum):
    """Market condition types"""
    TRENDING = "TRENDING"
    RANGE_BOUND = "RANGE_BOUND"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    HIGH_GAP_ENVIRONMENT = "HIGH_GAP_ENVIRONMENT"
    POLICY_UNCERTAINTY = "POLICY_UNCERTAINTY"

class StrategySelector:
    """
    Intelligent strategy selection based on market conditions and configuration
    """
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Strategy mappings based on market conditions
        self.condition_strategy_map = {
            MarketCondition.RANGE_BOUND: 'BollingerMeanReversion',
            MarketCondition.HIGH_VOLATILITY: 'PolicyMomentum',
            MarketCondition.LOW_VOLATILITY: 'SectorRotation',
            MarketCondition.TRENDING: 'BullishMomentumDip',
            MarketCondition.HIGH_GAP_ENVIRONMENT: 'GapTrading',
            MarketCondition.POLICY_UNCERTAINTY: 'PolicyMomentum'
        }
        
        # Strategy priority order (from PersonalTradingConfig)
        self.strategy_priority = getattr(config, 'PREFERRED_STRATEGY_ORDER', [
            'BollingerMeanReversion',
            'BullishMomentumDipStrategy',
            'GapTrading',
            'ValueRateStrategy',
            'SectorRotation',
            'International',
            'PolicyMomentum',
            'MicrostructureBreakout'
        ])
        
        # Strategy risk levels (for risk-based selection)
        self.strategy_risk_levels = {
            'BollingerMeanReversion': 'LOW',
            'ValueRateStrategy': 'LOW',
            'SectorRotation': 'MEDIUM',
            'International': 'MEDIUM',
            'BullishMomentumDipStrategy': 'MEDIUM',
            'PolicyMomentum': 'HIGH',
            'GapTrading': 'HIGH',
            'MicrostructureBreakout': 'HIGH'
        }
    
    def select_strategy(self, market_condition: Dict, override_strategy: str = None, 
                       risk_preference: str = 'MEDIUM') -> Tuple[str, float]:
        """
        Select optimal trading strategy based on market conditions and preferences
        
        Args:
            market_condition: Market condition analysis from MarketConditionAnalyzer
            override_strategy: Manual strategy override from config
            risk_preference: Risk preference ('LOW', 'MEDIUM', 'HIGH')
            
        Returns:
            Tuple of (strategy_name, confidence_score)
        """
        
        # 1. Check for manual override from configuration
        if override_strategy:
            strategy_override, stock_list_override = self.config.get_automated_strategy_override()
            if strategy_override:
                self.logger.info(f"🎯 Using configuration override: {strategy_override}")
                return strategy_override, 1.0
        
        # 2. Check for high-confidence market condition
        condition = market_condition.get('condition', 'RANGE_BOUND')
        confidence = market_condition.get('confidence', 0.5)
        
        # 3. Handle gap environment (special case)
        if market_condition.get('gap_environment', False):
            gap_stats = market_condition.get('gap_stats', {})
            if gap_stats.get('is_high_gap_day', False):
                self.logger.info("🔥 High gap environment detected - selecting GapTrading")
                return 'GapTrading', min(confidence + 0.2, 1.0)
        
        # 4. Map market condition to strategy
        try:
            market_enum = MarketCondition(condition)
            recommended_strategy = self.condition_strategy_map.get(market_enum)
        except ValueError:
            # Fallback for unknown conditions
            recommended_strategy = 'BollingerMeanReversion'
            self.logger.warning(f"Unknown market condition: {condition}, using fallback")
        
        # 5. Apply risk preference filter
        if risk_preference != 'MEDIUM':
            risk_filtered_strategy = self._apply_risk_filter(
                recommended_strategy, risk_preference, market_condition
            )
            if risk_filtered_strategy != recommended_strategy:
                self.logger.info(f"🛡️ Risk filter applied: {recommended_strategy} → {risk_filtered_strategy}")
                recommended_strategy = risk_filtered_strategy
        
        # 6. Validate strategy availability
        if not self._is_strategy_available(recommended_strategy):
            self.logger.warning(f"Strategy {recommended_strategy} not available, using fallback")
            recommended_strategy = self._get_fallback_strategy(risk_preference)
        
        # 7. Calculate final confidence score
        final_confidence = self._calculate_selection_confidence(
            recommended_strategy, market_condition, confidence
        )
        
        self.logger.info(f"📊 Selected strategy: {recommended_strategy} (confidence: {final_confidence:.2f})")
        
        return recommended_strategy, final_confidence
    
    def _apply_risk_filter(self, strategy: str, risk_preference: str, 
                          market_condition: Dict) -> str:
        """Apply risk preference to strategy selection"""
        
        strategy_risk = self.strategy_risk_levels.get(strategy, 'MEDIUM')
        
        # If current strategy risk matches preference, keep it
        if strategy_risk == risk_preference:
            return strategy
        
        # If risk preference is conservative, prefer lower risk strategies
        if risk_preference == 'LOW':
            if strategy_risk in ['MEDIUM', 'HIGH']:
                # Find the highest priority low-risk strategy
                for preferred_strategy in self.strategy_priority:
                    if self.strategy_risk_levels.get(preferred_strategy, 'MEDIUM') == 'LOW':
                        return preferred_strategy
                return 'BollingerMeanReversion'  # Ultimate safe fallback
        
        # If risk preference is aggressive, prefer higher risk strategies
        elif risk_preference == 'HIGH':
            if strategy_risk == 'LOW':
                # Check if market conditions support high-risk strategies
                vix_level = market_condition.get('vix_level', 20)
                if vix_level > 25:  # High volatility supports high-risk strategies
                    for preferred_strategy in self.strategy_priority:
                        if self.strategy_risk_levels.get(preferred_strategy, 'MEDIUM') == 'HIGH':
                            return preferred_strategy
        
        # Default: return original strategy
        return strategy
    
    def _is_strategy_available(self, strategy_name: str) -> bool:
        """Check if strategy is available in the system"""
        # This would check against available strategies in the trading system
        available_strategies = [
            'BollingerMeanReversion',
            'BullishMomentumDipStrategy',
            'BullishMomentumDip',
            'GapTrading',
            'ValueRateStrategy',
            'ValueRate',
            'SectorRotationStrategy',
            'SectorRotation',
            'InternationalStrategy',
            'International',
            'PolicyMomentumStrategy',
            'PolicyMomentum',
            'MicrostructureBreakoutStrategy',
            'MicrostructureBreakout'
        ]
        
        return strategy_name in available_strategies
    
    def _get_fallback_strategy(self, risk_preference: str = 'MEDIUM') -> str:
        """Get fallback strategy based on risk preference"""
        
        fallback_by_risk = {
            'LOW': 'BollingerMeanReversion',
            'MEDIUM': 'BollingerMeanReversion',
            'HIGH': 'GapTrading'
        }
        
        fallback = fallback_by_risk.get(risk_preference, 'BollingerMeanReversion')
        
        # Double-check availability
        if self._is_strategy_available(fallback):
            return fallback
        
        # Ultimate fallback
        return 'BollingerMeanReversion'
    
    def _calculate_selection_confidence(self, strategy: str, market_condition: Dict, 
                                      base_confidence: float) -> float:
        """Calculate confidence in strategy selection"""
        
        confidence = base_confidence
        
        # Boost confidence for strategy-condition alignment
        condition = market_condition.get('condition', 'RANGE_BOUND')
        
        # High confidence scenarios
        if (condition == 'HIGH_GAP_ENVIRONMENT' and strategy == 'GapTrading') or \
           (condition == 'RANGE_BOUND' and strategy == 'BollingerMeanReversion') or \
           (condition == 'HIGH_VOLATILITY' and strategy == 'PolicyMomentum'):
            confidence += 0.2
        
        # VIX-based confidence adjustments
        vix_level = market_condition.get('vix_level', 20)
        
        if strategy == 'PolicyMomentum' and vix_level > 25:
            confidence += 0.15  # High VIX suits policy momentum
        elif strategy == 'BollingerMeanReversion' and 15 <= vix_level <= 25:
            confidence += 0.1   # Moderate VIX suits mean reversion
        elif strategy == 'GapTrading' and vix_level > 30:
            confidence += 0.1   # High VIX creates more gaps
        
        # Market trend alignment
        market_trend = market_condition.get('market_trend', 'SIDEWAYS')
        
        if strategy == 'BullishMomentumDipStrategy' and market_trend == 'BULLISH':
            confidence += 0.15
        elif strategy == 'BollingerMeanReversion' and market_trend == 'SIDEWAYS':
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_strategy_alternatives(self, primary_strategy: str, 
                                market_condition: Dict) -> List[Tuple[str, float]]:
        """
        Get alternative strategies ranked by suitability
        
        Returns:
            List of (strategy_name, confidence_score) tuples
        """
        
        alternatives = []
        
        # Get all available strategies except the primary one
        for strategy in self.strategy_priority:
            if strategy != primary_strategy and self._is_strategy_available(strategy):
                confidence = self._calculate_selection_confidence(
                    strategy, market_condition, 0.5
                )
                alternatives.append((strategy, confidence))
        
        # Sort by confidence score
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def explain_selection(self, strategy: str, market_condition: Dict, 
                         confidence: float) -> Dict:
        """
        Provide explanation for strategy selection
        
        Returns:
            Dictionary with selection reasoning
        """
        
        explanation = {
            'selected_strategy': strategy,
            'confidence': confidence,
            'market_condition': market_condition.get('condition', 'UNKNOWN'),
            'reasoning': [],
            'risk_level': self.strategy_risk_levels.get(strategy, 'MEDIUM'),
            'alternatives': []
        }
        
        # Add reasoning based on market conditions
        condition = market_condition.get('condition', 'RANGE_BOUND')
        vix_level = market_condition.get('vix_level', 20)
        
        if strategy == 'GapTrading':
            if market_condition.get('gap_environment', False):
                explanation['reasoning'].append("High gap environment detected")
            if vix_level > 25:
                explanation['reasoning'].append(f"High VIX ({vix_level:.1f}) supports gap trading")
        
        elif strategy == 'BollingerMeanReversion':
            if condition == 'RANGE_BOUND':
                explanation['reasoning'].append("Range-bound market suits mean reversion")
            if 15 <= vix_level <= 25:
                explanation['reasoning'].append(f"Moderate VIX ({vix_level:.1f}) ideal for BB strategy")
        
        elif strategy == 'PolicyMomentum':
            if condition == 'HIGH_VOLATILITY':
                explanation['reasoning'].append("High volatility indicates policy uncertainty")
            if vix_level > 25:
                explanation['reasoning'].append(f"Elevated VIX ({vix_level:.1f}) suggests policy concerns")
        
        # Add alternatives
        explanation['alternatives'] = self.get_strategy_alternatives(strategy, market_condition)
        
        return explanation

# Usage example and integration
class StrategyManager:
    """
    High-level strategy management that combines selector with trading system
    """
    
    def __init__(self, config, trading_system, logger=None):
        self.config = config
        self.trading_system = trading_system
        self.selector = StrategySelector(config, logger)
        self.logger = logger or logging.getLogger(__name__)
        
        self.current_strategy = None
        self.selection_history = []
    
    def select_and_set_strategy(self, market_condition: Dict, 
                               force_reselection: bool = False) -> bool:
        """
        Select optimal strategy and set it in the trading system
        
        Returns:
            True if strategy was changed, False otherwise
        """
        
        # Get configuration overrides
        strategy_override, _ = self.config.get_automated_strategy_override()
        
        # Select strategy
        selected_strategy, confidence = self.selector.select_strategy(
            market_condition, 
            override_strategy=strategy_override
        )
        
        # Check if we need to change strategy
        if not force_reselection and selected_strategy == self.current_strategy:
            self.logger.info(f"📊 Keeping current strategy: {selected_strategy}")
            return False
        
        # Validate strategy is available in trading system
        if selected_strategy not in self.trading_system.strategies:
            self.logger.error(f"❌ Strategy {selected_strategy} not available in trading system")
            
            # Try fallback
            fallback_strategy = self.selector._get_fallback_strategy()
            if fallback_strategy in self.trading_system.strategies:
                selected_strategy = fallback_strategy
                self.logger.info(f"🔄 Using fallback strategy: {fallback_strategy}")
            else:
                self.logger.error("❌ No available strategies found")
                return False
        
        # Set new strategy
        old_strategy = self.current_strategy
        self.current_strategy = selected_strategy
        self.trading_system.current_strategy = selected_strategy
        
        # Log strategy change
        if old_strategy != selected_strategy:
            self.logger.info(f"🔄 Strategy changed: {old_strategy} → {selected_strategy}")
            
            # Get explanation
            explanation = self.selector.explain_selection(
                selected_strategy, market_condition, confidence
            )
            
            for reason in explanation['reasoning']:
                self.logger.info(f"   📋 {reason}")
        
        # Record selection in history
        self.selection_history.append({
            'timestamp': datetime.now().isoformat(),
            'strategy': selected_strategy,
            'previous_strategy': old_strategy,
            'confidence': confidence,
            'market_condition': market_condition.copy(),
            'reasoning': explanation.get('reasoning', [])
        })
        
        # Keep only last 30 selections
        self.selection_history = self.selection_history[-30:]
        
        return True
    
    def get_selection_summary(self) -> Dict:
        """Get summary of recent strategy selections"""
        
        if not self.selection_history:
            return {'selections': 0, 'current_strategy': self.current_strategy}
        
        recent_selections = self.selection_history[-10:]  # Last 10 selections
        
        strategy_counts = {}
        for selection in recent_selections:
            strategy = selection['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            'current_strategy': self.current_strategy,
            'total_selections': len(self.selection_history),
            'recent_selections': len(recent_selections),
            'strategy_distribution': strategy_counts,
            'last_change': self.selection_history[-1]['timestamp'] if self.selection_history else None,
            'average_confidence': sum(s['confidence'] for s in recent_selections) / len(recent_selections)
        }