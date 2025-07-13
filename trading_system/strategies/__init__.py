# trading_system/strategies/__init__.py
"""Trading strategies module with refactored base classes"""

# Import base classes first
from .base_strategy import TradingStrategy, TradingSignal

# Import all strategy implementations
from .bollinger_mean_reversion import BollingerMeanReversionStrategy
from .gap_trading import GapTradingStrategy
from .bullish_momentum_dip import BullishMomentumDipStrategy
from .international_strategy import InternationalStrategy
from .microstructure_breakout import MicrostructureBreakoutStrategy
from .policy_momentum import PolicyMomentumStrategy
from .sector_rotation import SectorRotationStrategy
from .value_rate_strategy import ValueRateStrategy

__all__ = [
    # Base classes
    'TradingStrategy', 
    'TradingSignal',
    # Strategy implementations
    'BollingerMeanReversionStrategy', 
    'GapTradingStrategy',
    'BullishMomentumDipStrategy',
    'InternationalStrategy', 
    'MicrostructureBreakoutStrategy', 
    'PolicyMomentumStrategy', 
    'SectorRotationStrategy', 
    'ValueRateStrategy'
]