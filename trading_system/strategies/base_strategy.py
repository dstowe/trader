# strategies/base_strategy.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class TradingSignal:
    """Standardized trading signal structure"""
    symbol: str
    signal_type: str  # BUY, SELL
    price: float
    confidence: float
    strategy: str
    timestamp: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'price': self.price,
            'confidence': self.confidence,
            'strategy': self.strategy,
            'timestamp': self.timestamp,
            'metadata': self.metadata or {}
        }

class TradingStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, config_manager):
        self.name = name
        self.config = config_manager
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[TradingSignal]:
        """Generate trading signals for given data"""
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """Return list of required technical indicators"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that data contains required indicators"""
        required = self.get_required_indicators()
        missing = [ind for ind in required if ind not in data.columns]
        if missing:
            raise ValueError(f"Missing required indicators: {missing}")
        return True
    
    def calculate_confidence(self, signal_data: Dict) -> float:
        """Base confidence calculation - can be overridden"""
        return 0.5
    
    def get_strategy_metadata(self) -> Dict:
        """Return strategy-specific metadata"""
        return {
            'name': self.name,
            'required_indicators': self.get_required_indicators(),
            'min_data_points': self.get_min_data_points()
        }
    
    @abstractmethod
    def get_min_data_points(self) -> int:
        """Minimum data points required for strategy"""
        pass