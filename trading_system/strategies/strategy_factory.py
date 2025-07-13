# strategies/strategy_factory.py
class StrategyFactory:
    """Factory for creating trading strategies"""
    
    _strategies = {
        'BollingerMeanReversion': BollingerMeanReversionStrategy,
        'GapTrading': 'GapTradingStrategy',  # Would import actual class
        'BullishMomentumDip': 'BullishMomentumDipStrategy',
        # ... etc
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str, config_manager) -> TradingStrategy:
        """Create strategy instance"""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class(config_manager)
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategy names"""
        return list(cls._strategies.keys())
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class):
        """Register new strategy"""
        cls._strategies[name] = strategy_class