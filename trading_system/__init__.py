"""
Trading System Package
A modular trading system with authentication, account management, and trading strategies
"""

__version__ = "2.0.0"

from .main import TradingSystem
# UPDATED: Remove TradingConfig import since we're using PersonalTradingConfig as single source of truth
from .config.stock_lists import StockLists
from .webull.webull import webull

# Import new modular components
from .auth import CredentialManager, LoginManager, SessionManager
from .accounts import AccountManager, AccountInfo

__all__ = [
    'TradingSystem', 
    'StockLists', 
    'webull',
    'CredentialManager',
    'LoginManager', 
    'SessionManager',
    'AccountManager',
    'AccountInfo'
]