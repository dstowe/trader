"""
Trading System Package
A modular Bollinger Band mean reversion trading system
"""

__version__ = "1.0.0"

from .main import TradingSystem
from .config.settings import TradingConfig
from .config.stock_lists import StockLists
from .webull.webull import webull
__all__ = ['TradingSystem', 'TradingConfig', 'StockLists', 'webull']
