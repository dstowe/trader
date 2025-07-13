# errors/error_handler.py
import logging
from typing import Optional, Callable
from functools import wraps

class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_callbacks = {}
    
    def register_error_callback(self, error_type: type, callback: Callable):
        """Register callback for specific error types"""
        self.error_callbacks[error_type] = callback
    
    def handle_error(self, error: Exception, context: dict = None) -> bool:
        """Handle error with appropriate logging and callbacks"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        
        # Log error
        self.logger.error(f"Error occurred: {error_info['type']} - {error_info['message']}")
        if context:
            self.logger.error(f"Context: {context}")
        
        # Call registered callback if exists
        error_type = type(error)
        if error_type in self.error_callbacks:
            try:
                return self.error_callbacks[error_type](error, context)
            except Exception as callback_error:
                self.logger.error(f"Error in error callback: {callback_error}")
        
        return False

def with_error_handling(error_handler: ErrorHandler, 
                       reraise: bool = False,
                       error_return_value = None):
    """Decorator for standardized error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate for logging
                    'kwargs': str(kwargs)[:100]
                }
                
                handled = error_handler.handle_error(e, context)
                
                if reraise or not handled:
                    raise e
                
                return error_return_value
        return wrapper
    return decorator