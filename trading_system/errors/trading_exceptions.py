# errors/trading_exceptions.py
class TradingSystemError(Exception):
    """Base exception for trading system"""
    def __init__(self, message: str, error_code: str = None, context: dict = None):
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()

class AuthenticationError(TradingSystemError):
    """Authentication related errors"""
    pass

class AccountError(TradingSystemError):
    """Account related errors"""
    pass

class TradingRuleViolation(TradingSystemError):
    """Trading rule violation errors"""
    pass

class DataError(TradingSystemError):
    """Data fetching/processing errors"""
    pass

class OrderExecutionError(TradingSystemError):
    """Order execution errors"""
    pass