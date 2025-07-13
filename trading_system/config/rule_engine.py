# config/rule_engine.py
class TradingRuleEngine:
    """Separate rule validation from configuration"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        
    def validate_signal(self, signal: Dict, context: Dict) -> tuple[bool, str]:
        """Validate trading signal against all rules"""
        validators = [
            self._validate_short_selling,
            self._validate_day_trading,
            self._validate_position_limits,
            self._validate_confidence_threshold
        ]
        
        for validator in validators:
            is_valid, reason = validator(signal, context)
            if not is_valid:
                return False, reason
        
        return True, "Signal passed all validations"
    
    def _validate_short_selling(self, signal: Dict, context: Dict) -> tuple[bool, str]:
        """Validate short selling rules"""
        if signal['signal_type'] == 'SELL' and signal['symbol'] not in context.get('current_positions', []):
            return False, "Short selling not allowed"
        return True, ""
    
    def _validate_day_trading(self, signal: Dict, context: Dict) -> tuple[bool, str]:
        """Validate day trading rules"""
        # Implementation here
        return True, ""
    
    def _validate_position_limits(self, signal: Dict, context: Dict) -> tuple[bool, str]:
        """Validate position size limits"""
        # Implementation here
        return True, ""
    
    def _validate_confidence_threshold(self, signal: Dict, context: Dict) -> tuple[bool, str]:
        """Validate confidence threshold"""
        confidence = signal.get('confidence', 0)
        if confidence < 0.6:  # This should come from config
            return False, f"Confidence {confidence:.1%} below minimum threshold"
        return True, ""