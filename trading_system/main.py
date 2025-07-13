# main.py
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import TradingConfig
from config.stock_lists import StockLists
from database.models import DatabaseManager
from data.webull_client import DataFetcher
from indicators.technical import TechnicalIndicators

# Import ALL strategies
from strategies.bollinger_mean_reversion import BollingerMeanReversionStrategy
from strategies.gap_trading import GapTradingStrategy
from strategies.bullish_momentum_dip import BullishMomentumDipStrategy
from strategies.international_strategy import InternationalStrategy
from strategies.microstructure_breakout import MicrostructureBreakoutStrategy
from strategies.policy_momentum import PolicyMomentumStrategy
from strategies.sector_rotation import SectorRotationStrategy
from strategies.value_rate_strategy import ValueRateStrategy

from ai.market_analyzer import MarketConditionAnalyzer

class TradingSystem:
    """Main trading system orchestrator"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        self.data_fetcher = DataFetcher()
        self.market_analyzer = MarketConditionAnalyzer()
        self.indicators = TechnicalIndicators()
        
        # Initialize ALL strategies
        self.strategies = {
            'BollingerMeanReversion': BollingerMeanReversionStrategy(self.config),
            'GapTrading': GapTradingStrategy(self.config),
            'BullishMomentumDipStrategy': BullishMomentumDipStrategy(self.config),
            'BullishMomentumDip': BullishMomentumDipStrategy(self.config),  # Alternative name
            'InternationalStrategy': InternationalStrategy(self.config),
            'International': InternationalStrategy(self.config),  # Alternative name
            'MicrostructureBreakoutStrategy': MicrostructureBreakoutStrategy(self.config),
            'MicrostructureBreakout': MicrostructureBreakoutStrategy(self.config),  # Alternative name
            'PolicyMomentumStrategy': PolicyMomentumStrategy(self.config),
            'PolicyMomentum': PolicyMomentumStrategy(self.config),  # Alternative name
            'SectorRotationStrategy': SectorRotationStrategy(self.config),
            'SectorRotation': SectorRotationStrategy(self.config),  # Alternative name
            'ValueRateStrategy': ValueRateStrategy(self.config),
            'ValueRate': ValueRateStrategy(self.config)  # Alternative name
        }
        
        self.current_strategy = 'BollingerMeanReversion'
        self.stock_data_cache = {}  # Cache for gap environment analysis
        
    def run_daily_analysis(self, strategy_override=None, stock_list_override=None):
        """Run the complete daily trading analysis"""
        print(f"Starting daily analysis at {datetime.now()}")
        
        # Step 1: Fetch market data
        print("1. Fetching market data...")
        self._fetch_and_store_data()
        
        # Step 2: Analyze market conditions
        print("2. Analyzing market conditions...")
        market_condition = self._analyze_market_conditions()
        
        # Step 3: Select optimal strategy (with optional override)
        print("3. Selecting optimal strategy...")
        if strategy_override:
            if strategy_override in self.strategies:
                self.current_strategy = strategy_override
                print(f"✅ Strategy overridden to: {self.current_strategy}")
            else:
                print(f"❌ Strategy '{strategy_override}' not found!")
                print(f"Available strategies: {list(self.strategies.keys())}")
                self.current_strategy = 'BollingerMeanReversion'  # Fallback
                print(f"Using fallback strategy: {self.current_strategy}")
        else:
            self._select_strategy(market_condition)
        
        # Step 4: Generate trading signals
        print("4. Generating trading signals...")
        signals = self._generate_signals(stock_list_override)
        
        # Step 5: Display results
        print("5. Analysis complete!")
        self._display_results(market_condition, signals)
        
        # Return structured results that match what enhanced_trading_example.py expects
        buy_signals = [s for s in signals if s['signal_type'] == 'BUY']
        sell_signals = [s for s in signals if s['signal_type'] == 'SELL']
        
        # Determine stock universe based on current strategy and overrides
        if stock_list_override:
            if stock_list_override == 'GapTrading':
                stock_universe = StockLists.GAP_TRADING
            elif stock_list_override == 'BollingerMeanReversion':
                stock_universe = StockLists.BOLLINGER_MEAN_REVERSION
            elif stock_list_override == 'Core':
                stock_universe = StockLists.BOLLINGER_MEAN_REVERSION  # Use this as default for 'Core'
            else:
                stock_universe = StockLists.GAP_TRADING_UNIVERSE
        elif self.current_strategy == 'GapTrading':
            stock_universe = StockLists.GAP_TRADING_UNIVERSE
        else:
            stock_universe = StockLists.BOLLINGER_MEAN_REVERSION
        
        return {
            'strategy_used': self.current_strategy,
            'stock_universe': stock_universe,
            'total_signals': len(signals),
            'signals': signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'market_condition': market_condition
        }
    
    def _fetch_and_store_data(self):
        """Fetch and store stock data"""
        # Always fetch base stock list first
        base_stock_list = StockLists.BOLLINGER_MEAN_REVERSION
        
        # Determine which stock universe to use based on strategy mode
        if self.config.STRATEGY_MODE == 'FORCE_GAP':
            stock_list = StockLists.GAP_TRADING_UNIVERSE
        elif self.config.STRATEGY_MODE == 'AUTO':
            # For AUTO mode, fetch full universe to enable gap detection
            stock_list = StockLists.GAP_TRADING_UNIVERSE
        else:
            stock_list = base_stock_list
        
        print(f"Fetching data for {len(stock_list)} stocks...")
        stock_data = self.data_fetcher.fetch_multiple_stocks(stock_list, "3mo")
        
        # Cache stock data for gap environment analysis
        self.stock_data_cache = {}
        
        for symbol, data in stock_data.items():
            if not data.empty:
                # Store raw data
                self.db.insert_stock_data(symbol, data)
                
                # Calculate and store indicators with gap analysis
                indicators = self.indicators.calculate_all_indicators_with_gaps(data)
                self.db.insert_indicators(symbol, indicators)
                
                # Cache for gap analysis
                self.stock_data_cache[symbol] = indicators
                
                print(f"✅ Updated data for {symbol}")
    
    def _analyze_market_conditions(self):
        """Analyze current market conditions with gap environment detection"""
        # Get SPY data for market analysis
        spy_data = self.db.get_stock_data('SPY', 100)
        
        if spy_data.empty:
            print("Warning: No SPY data available, using default conditions")
            return self.market_analyzer._default_condition()
        
        # Get actual VIX data (not VXX proxy)
        vix_data = self.db.get_stock_data('^VIX', 50)
        
        # Enhanced market analysis with gap environment detection
        if self.config.STRATEGY_MODE in ['AUTO', 'FORCE_GAP'] and self.stock_data_cache:
            market_condition = self.market_analyzer.analyze_market_with_gaps(
                spy_data, self.stock_data_cache, self.config, vix_data if not vix_data.empty else None)
        else:
            market_condition = self.market_analyzer.analyze_market_condition(
                spy_data, vix_data if not vix_data.empty else None)
        
        # Override strategy based on STRATEGY_MODE
        if self.config.STRATEGY_MODE == 'FORCE_BB':
            market_condition['recommended_strategy'] = 'BollingerMeanReversion'
        elif self.config.STRATEGY_MODE == 'FORCE_GAP':
            market_condition['recommended_strategy'] = 'GapTrading'
        
        # Store market condition
        with self.db as conn:
            conn.execute('''
                INSERT OR REPLACE INTO market_conditions 
                (date, condition, vix_level, market_trend, recommended_strategy, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                market_condition['date'],
                market_condition['condition'],
                market_condition['vix_level'],
                market_condition['market_trend'],
                market_condition['recommended_strategy'],
                market_condition['confidence']
            ))
        
        return market_condition
    
    def _select_strategy(self, market_condition: dict):
        """Select optimal strategy based on market conditions"""
        recommended_strategy = market_condition['recommended_strategy']
        
        if recommended_strategy in self.strategies:
            self.current_strategy = recommended_strategy
            print(f"✅ Selected strategy: {self.current_strategy}")
        else:
            print(f"⚠ Strategy {recommended_strategy} not available, using {self.current_strategy}")
    
    def _generate_signals(self, stock_list_override=None):
        """Generate trading signals using selected strategy"""
        strategy = self.strategies[self.current_strategy]
        all_signals = []
        
        # Select appropriate stock list based on override or current strategy
        if stock_list_override:
            if stock_list_override == 'GapTrading':
                stock_list = StockLists.GAP_TRADING
            elif stock_list_override == 'BollingerMeanReversion':
                stock_list = StockLists.BOLLINGER_MEAN_REVERSION
            elif stock_list_override == 'Core':
                stock_list = StockLists.BOLLINGER_MEAN_REVERSION  # Use this as default
            else:
                stock_list = StockLists.GAP_TRADING_UNIVERSE
        elif self.current_strategy == 'GapTrading':
            stock_list = StockLists.GAP_TRADING_UNIVERSE
        else:
            stock_list = StockLists.BOLLINGER_MEAN_REVERSION
        
        print(f"🔍 Generating signals for {len(stock_list)} stocks using {self.current_strategy}")
        
        signals_found = 0
        for symbol in stock_list:
            # Get data with indicators
            data = self.db.get_stock_data(symbol, 50)
            if data.empty:
                print(f"❌ No data for {symbol}")
                continue
            
            # Use appropriate indicator calculation based on strategy
            if self.current_strategy == 'GapTrading':
                data_with_indicators = self.indicators.calculate_all_indicators_with_gaps(data)
            else:
                data_with_indicators = self.indicators.calculate_all_indicators(data)
            
            # Generate signals
            try:
                signals = strategy.generate_signals(data_with_indicators, symbol)
                
                if signals:
                    print(f"📈 {symbol}: Found {len(signals)} signals")
                    signals_found += len(signals)
                
                # Store signals in database
                for signal in signals:
                    self.db.insert_signal(**signal)
                    all_signals.append(signal)
                    
            except Exception as e:
                print(f"❌ Error generating signals for {symbol}: {e}")
        
        print(f"📊 Total signals found: {signals_found}")
        return all_signals
    
    def _fetch_market_data(self, symbols):
        """Fetch market data for specified symbols (used by enhanced_trading_example.py)"""
        stock_data = self.data_fetcher.fetch_multiple_stocks(symbols, "3mo")
        
        # Convert to DataFrame format expected by the example
        all_data = []
        for symbol, data in stock_data.items():
            if not data.empty:
                data_copy = data.copy()
                # Ensure Date column is properly set as datetime index
                if 'Date' in data_copy.columns:
                    data_copy.set_index('Date', inplace=True)
                data_copy.index = pd.to_datetime(data_copy.index)
                data_copy['symbol'] = symbol
                all_data.append(data_copy)
        
        if all_data:
            result = pd.concat(all_data, ignore_index=False)
            return result
        else:
            return pd.DataFrame()
    
    def _display_results(self, market_condition: dict, signals: list):
        """Display analysis results"""
        print("\n" + "="*60)
        print("ENHANCED TRADING SYSTEM ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\n📊 Market Condition: {market_condition['condition']}")
        print(f"📈 Market Trend: {market_condition['market_trend']}")
        print(f"📉 VIX Level: {market_condition['vix_level']:.2f}")
        print(f"🎯 Recommended Strategy: {market_condition['recommended_strategy']}")
        print(f"🔍 Confidence: {market_condition['confidence']:.2f}")
        print(f"⚙️  Strategy Mode: {self.config.STRATEGY_MODE}")
        
        # Display gap environment info if available
        if 'gap_stats' in market_condition:
            gap_stats = market_condition['gap_stats']
            print(f"\n🔥 GAP ENVIRONMENT ANALYSIS:")
            print(f"   Total Stocks Analyzed: {gap_stats['total_stocks']}")
            print(f"   Stocks with Gaps: {gap_stats['stocks_with_gaps']}")
            print(f"   Significant Gaps (>2%): {gap_stats['significant_gaps']}")
            print(f"   Gap Frequency: {gap_stats['gap_frequency']:.1%}")
            print(f"   High Gap Day: {'YES' if gap_stats['is_high_gap_day'] else 'NO'}")
            print(f"   Gap Environment Score: {gap_stats['gap_environment_score']:.2f}")
            
            if gap_stats.get('gap_stocks'):
                print(f"\n📊 TOP GAP STOCKS:")
                for gap_stock in gap_stats['gap_stocks'][:5]:  # Show top 5
                    print(f"   • {gap_stock['symbol']}: {gap_stock['gap_size']:.1%} {gap_stock['gap_direction']} "
                          f"({gap_stock['quality']} quality)")
        
        print(f"\n🚀 Current Strategy: {self.current_strategy}")
        
        if signals:
            print(f"\n📋 Trading Signals ({len(signals)} total):")
            buy_signals = [s for s in signals if s['signal_type'] == 'BUY']
            sell_signals = [s for s in signals if s['signal_type'] == 'SELL']
            
            if buy_signals:
                print(f"\n💰 BUY SIGNALS ({len(buy_signals)}):")
                for signal in buy_signals:
                    strategy_info = ""
                    if 'gap_strategy' in signal:
                        strategy_info = f" [{signal['gap_strategy']}]"
                    confidence = signal.get('confidence', 0)
                    print(f"  • {signal['symbol']}: ${signal['price']:.2f} "
                          f"(Confidence: {confidence:.2f}){strategy_info}")
            
            if sell_signals:
                print(f"\n💸 SELL SIGNALS ({len(sell_signals)}):")
                for signal in sell_signals:
                    strategy_info = ""
                    if 'gap_strategy' in signal:
                        strategy_info = f" [{signal['gap_strategy']}]"
                    confidence = signal.get('confidence', 0)
                    print(f"  • {signal['symbol']}: ${signal['price']:.2f} "
                          f"(Confidence: {confidence:.2f}){strategy_info}")
        else:
            print("\n📭 No trading signals generated")
        
        print(f"\n📈 STOCK UNIVERSE: {len(StockLists.GAP_TRADING_UNIVERSE if self.current_strategy == 'GapTrading' else StockLists.BOLLINGER_MEAN_REVERSION)} stocks")
        print("="*60)

def main():
    """Main entry point"""
    print("Initializing Trading System...")
    
    # Create trading system
    trading_system = TradingSystem()
    
    # Run analysis
    try:
        signals = trading_system.run_daily_analysis()
        return signals
    except Exception as e:
        print(f"Error during analysis: {e}")
        return []

if __name__ == "__main__":
    main()