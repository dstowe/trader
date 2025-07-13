# trading_system/strategies/strategy_factory.py - FIXED VERSION
from typing import Dict, List, Optional, Type
import logging

# Import base strategy classes
from .base_strategy import TradingStrategy, TradingSignal

class StrategyFactory(TradingStrategy):
    """Factory for creating trading strategies with proper error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._strategies: Dict[str, Type[TradingStrategy]] = {}
        self._register_available_strategies()
    
    def _register_available_strategies(self):
        """Register all available strategies with error handling"""
        
        # Strategy import map with error handling
        strategy_imports = {
            'BollingerMeanReversion': ('bollinger_mean_reversion', 'BollingerMeanReversionStrategy'),
            'GapTrading': ('gap_trading', 'GapTradingStrategy'),
            'BullishMomentumDip': ('bullish_momentum_dip', 'BullishMomentumDipStrategy'),
            'International': ('international_strategy', 'InternationalStrategy'),
            'MicrostructureBreakout': ('microstructure_breakout', 'MicrostructureBreakoutStrategy'),
            'PolicyMomentum': ('policy_momentum', 'PolicyMomentumStrategy'),
            'SectorRotation': ('sector_rotation', 'SectorRotationStrategy'),
            'ValueRate': ('value_rate_strategy', 'ValueRateStrategy'),
        }
        
        for strategy_name, (module_name, class_name) in strategy_imports.items():
            try:
                # Dynamic import with error handling
                module = __import__(f'.{module_name}', package=__package__, fromlist=[class_name])
                strategy_class = getattr(module, class_name)
                
                # Verify it's a proper strategy class
                if issubclass(strategy_class, TradingStrategy):
                    self._strategies[strategy_name] = strategy_class
                    
                    # Add common aliases
                    self._strategies[f'{strategy_name}Strategy'] = strategy_class
                    if strategy_name == 'BullishMomentumDip':
                        self._strategies['BullishMomentumDipStrategy'] = strategy_class
                    elif strategy_name == 'International':
                        self._strategies['InternationalStrategy'] = strategy_class
                    elif strategy_name == 'MicrostructureBreakout':
                        self._strategies['MicrostructureBreakoutStrategy'] = strategy_class
                    elif strategy_name == 'PolicyMomentum':
                        self._strategies['PolicyMomentumStrategy'] = strategy_class
                    elif strategy_name == 'SectorRotation':
                        self._strategies['SectorRotationStrategy'] = strategy_class
                    elif strategy_name == 'ValueRate':
                        self._strategies['ValueRateStrategy'] = strategy_class
                    
                    self.logger.debug(f"Registered strategy: {strategy_name}")
                else:
                    self.logger.warning(f"Class {class_name} is not a TradingStrategy subclass")
                    
            except ImportError as e:
                self.logger.warning(f"Could not import strategy {strategy_name}: {e}")
            except AttributeError as e:
                self.logger.warning(f"Strategy class {class_name} not found in module {module_name}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error registering strategy {strategy_name}: {e}")
        
        self.logger.info(f"Successfully registered {len(self._strategies)} strategy variants")
    
    def create_strategy(self, strategy_name: str, config) -> Optional[TradingStrategy]:
        """
        Create strategy instance with error handling
        
        Args:
            strategy_name: Name of the strategy to create
            config: Configuration object (PersonalTradingConfig)
            
        Returns:
            Strategy instance or None if creation fails
        """
        if strategy_name not in self._strategies:
            self.logger.error(f"Unknown strategy: {strategy_name}")
            self.logger.info(f"Available strategies: {list(self._strategies.keys())}")
            return None
        
        try:
            strategy_class = self._strategies[strategy_name]
            strategy_instance = strategy_class(config)
            self.logger.debug(f"Created strategy instance: {strategy_name}")
            return strategy_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create strategy {strategy_name}: {e}")
            return None
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        # Return unique strategy names (without aliases)
        unique_strategies = []
        seen = set()
        
        for name in self._strategies.keys():
            # Remove 'Strategy' suffix for cleaner names
            clean_name = name.replace('Strategy', '') if name.endswith('Strategy') else name
            if clean_name not in seen:
                unique_strategies.append(clean_name)
                seen.add(clean_name)
        
        return sorted(unique_strategies)
    
    def get_all_strategy_names(self) -> List[str]:
        """Get all strategy names including aliases"""
        return sorted(list(self._strategies.keys()))
    
    def is_strategy_available(self, strategy_name: str) -> bool:
        """Check if a strategy is available"""
        return strategy_name in self._strategies
    
    def register_strategy(self, name: str, strategy_class: Type[TradingStrategy]) -> bool:
        """
        Register a new strategy class
        
        Args:
            name: Strategy name
            strategy_class: Strategy class that inherits from TradingStrategy
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if not issubclass(strategy_class, TradingStrategy):
                self.logger.error(f"Strategy class {strategy_class} must inherit from TradingStrategy")
                return False
            
            self._strategies[name] = strategy_class
            self.logger.info(f"Registered custom strategy: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register strategy {name}: {e}")
            return False
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict]:
        """Get information about a strategy"""
        if strategy_name not in self._strategies:
            return None
        
        try:
            strategy_class = self._strategies[strategy_name]
            
            # Create temporary instance to get metadata (with dummy config)
            class DummyConfig:
                def __getattr__(self, name):
                    return getattr(self, name, None)
            
            temp_strategy = strategy_class(DummyConfig())
            
            return {
                'name': strategy_name,
                'class_name': strategy_class.__name__,
                'module': strategy_class.__module__,
                'required_indicators': getattr(temp_strategy, 'get_required_indicators', lambda: [])(),
                'min_data_points': getattr(temp_strategy, 'get_min_data_points', lambda: 20)(),
                'description': strategy_class.__doc__ or 'No description available'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting strategy info for {strategy_name}: {e}")
            return None

# Global factory instance
_strategy_factory = None

def get_strategy_factory() -> StrategyFactory:
    """Get global strategy factory instance"""
    global _strategy_factory
    if _strategy_factory is None:
        _strategy_factory = StrategyFactory()
    return _strategy_factory

def create_strategy(strategy_name: str, config) -> Optional[TradingStrategy]:
    """Convenience function to create a strategy"""
    factory = get_strategy_factory()
    return factory.create_strategy(strategy_name, config)

def get_available_strategies() -> List[str]:
    """Convenience function to get available strategies"""
    factory = get_strategy_factory()
    return factory.get_available_strategies()

# For backward compatibility
class LegacyStrategyFactory:
    """Legacy strategy factory for backward compatibility"""
    
    _strategies = {
        'BollingerMeanReversion': 'BollingerMeanReversionStrategy',
        'GapTrading': 'GapTradingStrategy',
        'BullishMomentumDip': 'BullishMomentumDipStrategy',
        # Add more as needed
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str, config_manager) -> Optional[TradingStrategy]:
        """Create strategy using new factory"""
        factory = get_strategy_factory()
        return factory.create_strategy(strategy_name, config_manager)
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get available strategies using new factory"""
        factory = get_strategy_factory()
        return factory.get_available_strategies()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class):
        """Register strategy using new factory"""
        factory = get_strategy_factory()
        return factory.register_strategy(name, strategy_class)