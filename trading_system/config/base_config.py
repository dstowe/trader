# config/base_config.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class TradingLimits:
    """Trading limits and risk management settings"""
    max_position_value_percent: float = 0.5
    min_position_value: float = 1.0
    max_positions_total: int = 8
    stop_loss_percent: float = 0.08
    take_profit_percent: float = 0.15
    max_daily_loss_percent: float = 0.05

@dataclass
class TradingHours:
    """Trading time configurations"""
    start_time: str = "00:00"
    end_time: str = "23:30"
    
    def is_market_hours(self) -> bool:
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        return self.start_time <= current_time <= self.end_time

@dataclass
class FractionalSettings:
    """Fractional trading configurations"""
    fund_buffer: float = 0.9
    min_order_amount: float = 5.0
    order_type: str = 'MKT'

class ConfigurationManager:
    """Central configuration manager following composition over inheritance"""
    
    def __init__(self):
        self.trading_limits = TradingLimits()
        self.trading_hours = TradingHours()
        self.fractional_settings = FractionalSettings()
        self.account_configs = self._load_account_configs()
        self.strategy_configs = self._load_strategy_configs()
    
    def _load_account_configs(self) -> Dict:
        """Load account configurations from external source"""
        # This could load from file, environment, or database
        return {
            'CASH': {
                'enabled': True,
                'day_trading_enabled': False,
                'max_position_size': self.trading_limits.max_position_value_percent,
            },
            'MARGIN': {
                'enabled': True,
                'day_trading_enabled': True,
                'max_position_size': self.trading_limits.max_position_value_percent,
            }
        }
    
    def _load_strategy_configs(self) -> Dict:
        """Load strategy configurations"""
        return {
            'mode': 'AUTO',
            'preferred_order': [
                'BollingerMeanReversion',
                'BullishMomentumDipStrategy',
                'GapTrading',
                # ... etc
            ]
        }