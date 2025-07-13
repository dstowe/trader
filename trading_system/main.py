# trading_system/main.py - FIXED VERSION
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

class TradingSystem:
    """Main Trading System with PersonalTradingConfig integration - FIXED"""
    
    def __init__(self, config=None):
        # Import here to avoid circular imports
        if config is None:
            from personal_config import PersonalTradingConfig
            self.config = PersonalTradingConfig()
        else:
            self.config = config
            
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize strategy registry
        self.strategies = {}
        self._register_strategies()
        
        # Current strategy
        self.current_strategy = None
        
        # Data storage
        self.stock_data = {}
        
    def _register_strategies(self):
        """Register all available strategies"""
        try:
            # Import strategies with error handling
            from .strategies.bollinger_mean_reversion import BollingerMeanReversionStrategy
            from .strategies.gap_trading import GapTradingStrategy
            from .strategies.bullish_momentum_dip import BullishMomentumDipStrategy
            from .strategies.international_strategy import InternationalStrategy
            from .strategies.microstructure_breakout import MicrostructureBreakoutStrategy
            from .strategies.policy_momentum import PolicyMomentumStrategy
            from .strategies.sector_rotation import SectorRotationStrategy
            from .strategies.value_rate_strategy import ValueRateStrategy
            
            # Register strategies
            self.strategies = {
                'BollingerMeanReversion': BollingerMeanReversionStrategy(self.config),
                'GapTrading': GapTradingStrategy(self.config),
                'BullishMomentumDip': BullishMomentumDipStrategy(self.config),
                'BullishMomentumDipStrategy': BullishMomentumDipStrategy(self.config),  # Alias
                'International': InternationalStrategy(self.config),
                'InternationalStrategy': InternationalStrategy(self.config),  # Alias
                'MicrostructureBreakout': MicrostructureBreakoutStrategy(self.config),
                'MicrostructureBreakoutStrategy': MicrostructureBreakoutStrategy(self.config),  # Alias
                'PolicyMomentum': PolicyMomentumStrategy(self.config),
                'PolicyMomentumStrategy': PolicyMomentumStrategy(self.config),  # Alias
                'SectorRotation': SectorRotationStrategy(self.config),
                'SectorRotationStrategy': SectorRotationStrategy(self.config),  # Alias
                'ValueRate': ValueRateStrategy(self.config),
                'ValueRateStrategy': ValueRateStrategy(self.config),  # Alias
            }
            
            self.logger.info(f"Registered {len(self.strategies)} strategies")
            
        except ImportError as e:
            self.logger.error(f"Error importing strategies: {e}")
            # Fallback: register at least BollingerMeanReversion if available
            try:
                from .strategies.bollinger_mean_reversion import BollingerMeanReversionStrategy
                self.strategies['BollingerMeanReversion'] = BollingerMeanReversionStrategy(self.config)
                self.logger.warning("Only BollingerMeanReversion strategy available")
            except ImportError:
                self.logger.error("No strategies could be loaded")
    
    def run_daily_analysis(self, strategy_override=None, stock_list_override=None) -> Dict:
        """Run daily analysis with strategy selection"""
        try:
            self.logger.info("Starting daily analysis...")
            
            # 1. Select strategy
            strategy_name = self._select_strategy(strategy_override)
            if not strategy_name:
                return {'error': 'No strategy available'}
            
            # 2. Get stock list
            stock_list = self._get_stock_list(stock_list_override, strategy_name)
            if not stock_list:
                return {'error': 'No stocks to analyze'}
            
            # 3. Fetch and prepare data
            data_dict = self._fetch_stock_data(stock_list)
            if not data_dict:
                return {'error': 'No data available'}
            
            # 4. Generate signals
            all_signals = self._generate_signals(strategy_name, data_dict)
            
            # 5. Return results
            results = {
                'strategy_used': strategy_name,
                'stocks_analyzed': len(data_dict),
                'buy_signals': [s for s in all_signals if s.signal_type == 'BUY'],
                'sell_signals': [s for s in all_signals if s.signal_type == 'SELL'],
                'total_signals': len(all_signals),
                'market_condition': self._get_market_condition(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Analysis complete: {len(all_signals)} signals generated")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in daily analysis: {e}")
            return {'error': str(e)}
    
    def _select_strategy(self, override=None) -> Optional[str]:
        """Select trading strategy"""
        if override and override in self.strategies:
            self.current_strategy = override
            return override
        
        # Get strategy from config
        strategy_override, _ = self.config.get_automated_strategy_override()
        if strategy_override and strategy_override in self.strategies:
            self.current_strategy = strategy_override
            return strategy_override
        
        # Default fallback
        if 'BollingerMeanReversion' in self.strategies:
            self.current_strategy = 'BollingerMeanReversion'
            return 'BollingerMeanReversion'
        
        # Last resort: any available strategy
        if self.strategies:
            strategy_name = list(self.strategies.keys())[0]
            self.current_strategy = strategy_name
            return strategy_name
        
        return None
    
    def _get_stock_list(self, override=None, strategy_name=None) -> List[str]:
        """Get stock list for analysis"""
        if override:
            return override
        
        # Get from config
        try:
            return self.config.get_stock_list_for_data_fetch()
        except AttributeError:
            # Fallback to strategy-specific list
            if strategy_name:
                from .config.stock_lists import StockLists
                return StockLists.get_stocks_for_strategy(strategy_name)
            
            # Ultimate fallback
            return ['SPY', 'QQQ', 'AAPL', 'MSFT']
    
    def _fetch_stock_data(self, stock_list: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch stock data with indicators"""
        data_dict = {}
        
        try:
            from .data.webull_client import DataFetcher
            fetcher = DataFetcher()
            
            for symbol in stock_list[:10]:  # Limit to 10 for testing
                try:
                    data = fetcher.fetch_stock_data(symbol)
                    if not data.empty:
                        # Add technical indicators
                        data_with_indicators = self._add_technical_indicators(data)
                        data_dict[symbol] = data_with_indicators
                        
                except Exception as e:
                    self.logger.warning(f"Failed to fetch data for {symbol}: {e}")
                    continue
            
        except ImportError:
            self.logger.error("DataFetcher not available")
        
        return data_dict
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to data"""
        try:
            from .indicators.technical import TechnicalIndicators
            
            # Calculate all indicators
            return TechnicalIndicators.calculate_all_indicators_with_gaps(
                data, 
                bb_period=getattr(self.config, 'BB_PERIOD', 20),
                rsi_period=getattr(self.config, 'RSI_PERIOD', 14)
            )
            
        except ImportError:
            self.logger.warning("TechnicalIndicators not available, using raw data")
            return data
    
    def _generate_signals(self, strategy_name: str, data_dict: Dict[str, pd.DataFrame]) -> List:
        """Generate trading signals"""
        all_signals = []
        
        if strategy_name not in self.strategies:
            self.logger.error(f"Strategy {strategy_name} not found")
            return []
        
        strategy = self.strategies[strategy_name]
        
        for symbol, data in data_dict.items():
            try:
                signals = strategy.generate_signals(data, symbol)
                all_signals.extend(signals)
                
            except Exception as e:
                self.logger.warning(f"Error generating signals for {symbol}: {e}")
                continue
        
        return all_signals
    
    def _get_market_condition(self) -> Dict:
        """Get current market condition"""
        return {
            'condition': 'RANGE_BOUND',  # Default
            'confidence': 0.5,
            'vix_level': 20,
            'market_trend': 'SIDEWAYS'
        }