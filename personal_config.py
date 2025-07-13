# personal_config.py - COMPLETE VERSION WITH AUTOMATED SYSTEM OVERRIDES
"""
Personal Trading Configuration with Enhanced Rule Enforcement and Strategy Overrides
Extends the base TradingConfig with personal preferences and strict rule enforcement
Now includes full automated system strategy override support
"""

import os
from datetime import datetime
from typing import List, Dict, Tuple, Any
from trading_system.config.settings import TradingConfig

class PersonalTradingConfig(TradingConfig):
    # =================================================================
    # AUTOMATED SYSTEM CONTROL SETTINGS (NEW)
    # =================================================================
    
    # Strategy Selection Mode for Automated System
    AUTOMATED_STRATEGY_MODE = 'FORCE_STRATEGY'  # Options: 'AUTO', 'FORCE_STRATEGY', 'FORCE_STOCK_LIST', 'CUSTOM'
    
    # Strategy Override Settings
    FORCED_STRATEGY = 'PolicyMomentum'  # Used when AUTOMATED_STRATEGY_MODE = 'FORCE_STRATEGY'
    FORCED_STOCK_LIST = 'PolicyMomentum'  # Used when AUTOMATED_STRATEGY_MODE = 'FORCE_STOCK_LIST'
    
    # Custom Override Settings (for advanced users)
    CUSTOM_STRATEGY_OVERRIDE = None     # Set to strategy name to override
    CUSTOM_STOCK_LIST_OVERRIDE = None   # Set to stock list name to override
    
    # Automated System Behavior Controls
    ENABLE_STRATEGY_RETRY = True        # Retry with different strategy if first fails
    FALLBACK_STRATEGY = 'BollingerMeanReversion'  # Strategy to use if preferred fails
    MAX_STRATEGY_ATTEMPTS = 2           # How many strategies to try before giving up
    
    # Market Condition Override
    IGNORE_MARKET_CONDITIONS = True    # If True, always use FORCED_STRATEGY regardless of market
    
    # =================================================================
    # PERSONAL TRADING RULES (CRITICAL - NEVER OVERRIDE) - CLASS LEVEL
    # =================================================================
    ALLOW_SHORT_SELLING = False  # Never allow short selling
    ALLOW_DAY_TRADING = False    # Never allow day trading
    
    # Day trading detection settings
    DAY_TRADING_LOOKBACK_HOURS = 24  # Consider trades within 24 hours as potential day trades
    
    # Position Management
    MAX_POSITION_VALUE_PERCENT = 0.5  # 50% max of account per position
    MIN_POSITION_VALUE = 1          # Minimum $1 position
    MAX_POSITIONS_TOTAL = 8            # Maximum 8 total positions
    
    # Risk Management (Personal)
    PERSONAL_STOP_LOSS = 0.08          # 8% stop loss (more conservative)
    PERSONAL_TAKE_PROFIT = 0.15        # 15% take profit target
    MAX_DAILY_RISK_PERCENT = 0.5      # 5% max account risk per day
    
    # Fractional Order Safety Settings
    FRACTIONAL_FUND_BUFFER = 0.9       # Use only 90% of available funds for fractional orders
    MIN_FRACTIONAL_ORDER = 5.0         # Minimum $5 for fractional orders to avoid API issues
    FRACTIONAL_ORDER_TYPE = 'LMT'      # Use limit orders for better fractional execution
    
    # Signal Filtering
    MIN_SIGNAL_CONFIDENCE = 0.6        # 60% minimum confidence for trades
    REQUIRE_VOLUME_CONFIRMATION = True  # Require volume confirmation
    
    # Strategy-Specific Settings
    MAX_INTERNATIONAL_ALLOCATION = 0.30    # 30% max international exposure
    MAX_SECTOR_ALLOCATION = 0.20           # 20% max sector rotation
    MAX_REIT_ALLOCATION = 0.25             # 25% max REIT exposure
    MAX_FINANCIAL_ALLOCATION = 0.20        # 20% max financials
    
    # VIX-based strategy filtering
    VIX_CONSERVATIVE_THRESHOLD = 25        # Above this, use defensive strategies
    VIX_AGGRESSIVE_THRESHOLD = 30          # Above this, avoid momentum strategies
    
    # Currency preferences for international
    PREFER_CURRENCY_HEDGED = False         # Prefer unhedged in weak USD environment
    USD_STRENGTH_THRESHOLD = 105           # DXY level to prefer hedged ETFs
    
    # Stock Universe Preferences
    EXCLUDE_PENNY_STOCKS = False        # No stocks under $5
    MIN_DAILY_VOLUME = 1_000_000      # 1M minimum daily volume
    PREFER_DIVIDEND_STOCKS = True      # Prefer dividend paying stocks
    
    # Time Preferences
    TRADING_START_TIME = "00:45"  # Wait 15 min after market open
    TRADING_END_TIME = "23:30"    # Stop 30 min before close
    
    # Notification Preferences
    REQUIRE_CONFIRMATION = True       # Always ask before trading
    SHOW_DETAILED_ANALYSIS = True    # Show full signal details
    
    # Holdings to exclude from analysis (buy and hold) - CLASS LEVEL
    BUY_AND_HOLD_POSITIONS = [
        # Add any positions you never want to sell
        # Example: 'AAPL', 'MSFT'
    ]

    def __init__(self):
        super().__init__()  # Call parent constructor
        
        # Database path
        self.DATABASE_PATH = "trading_data.db"
        
        # Account configurations
        self.ACCOUNT_CONFIGURATIONS = {
            'CASH': {
                'enabled': True,
                'day_trading_enabled': False,
                'options_enabled': False,
                'max_position_size': 0.2,  # 20% of account value
                'pdt_protection': False,
                'min_trade_amount': 5,
                'max_trade_amount': 30
            },
            'MARGIN': {
                'enabled': True,
                'day_trading_enabled': True,
                'options_enabled': False,
                'max_position_size': 0.2,  # 20% of account value
                'pdt_protection': True,
                'min_account_value_for_pdt': 25000,
                'min_trade_amount': 5,
                'max_trade_amount': 30
            }
        }
        
        # Preferred Strategies (All 8 strategies in priority order)
        self.PREFERRED_STRATEGY_ORDER = [
            'BollingerMeanReversion',     # Primary strategy - mean reversion
            'BullishMomentumDipStrategy', # Secondary - buy dips in bull markets  
            'GapTrading',                 # Third strategy - gap fills
            'ValueRateStrategy',          # Fourth - REITs/Financials in rate environment
            'SectorRotation',             # Fifth - sector momentum rotation
            'International',              # Sixth - international outperformance
            'PolicyMomentum',             # Seventh - Fed/policy volatility plays
            'MicrostructureBreakout'      # Eighth - precise breakout patterns
        ]
        
        # Expanded Stock Universes for All Strategies
        
        # International ETFs (for International Strategy)
        self.INTERNATIONAL_ETFS = [
            # Broad International
            'VEA', 'EFA', 'VXUS', 'IEFA',
            # Currency Hedged
            'HEFA', 'HEDJ',
            # Regional
            'VGK', 'EWJ', 'EEMA', 'VWO',
            # Specific Countries
            'EWG', 'EWU', 'EWY', 'INDA'
        ]
        
        # Sector ETFs (for Sector Rotation Strategy)
        self.SECTOR_ETFS = [
            'XLK',   # Technology
            'XLF',   # Financials
            'XLE',   # Energy
            'XLV',   # Healthcare
            'XLI',   # Industrials
            'XLP',   # Consumer Staples
            'XLU',   # Utilities
            'XLY',   # Consumer Discretionary
            'XLB',   # Materials
            'XLRE',  # Real Estate
            'XLC'    # Communication Services
        ]
        
        # REIT Universe (for Value-Rate Strategy)
        self.REIT_UNIVERSE = [
            # Industrial/Logistics REITs
            'PLD', 'EXR',
            # Healthcare REITs
            'WELL', 'VTR',
            # Retail REITs
            'FRT', 'REG', 'SPG',
            # Infrastructure REITs
            'CCI', 'AMT', 'EQIX', 'DLR',
            # Office REITs
            'BXP', 'VNO',
            # Residential REITs
            'EQR', 'AVB', 'MAA',
            # REIT ETFs
            'XLRE', 'IYR', 'SCHH'
        ]
        
        # Financial Universe (for Value-Rate Strategy)
        self.FINANCIAL_UNIVERSE = [
            # Large Banks
            'JPM', 'BAC', 'WFC', 'C',
            # Regional Banks
            'USB', 'TFC', 'PNC',
            # Investment Banks
            'GS', 'MS',
            # Insurance
            'BRK-B', 'AIG',
            # Financial ETFs
            'XLF', 'KBE'
        ]
        
        # Policy-Sensitive Stocks (for Policy Momentum Strategy)
        self.POLICY_SENSITIVE_STOCKS = [
            # Rate-sensitive financials
            'JPM', 'BAC', 'USB', 'XLF',
            # Growth stocks (policy sensitive)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
            # Market-sensitive ETFs
            'SPY', 'QQQ', 'IWM'
        ]
        
        # High-Volume Stocks for Microstructure Breakouts
        self.MICROSTRUCTURE_UNIVERSE = [
            # Major ETFs (tight spreads)
            'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
            # Large Cap Tech (tight spreads)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
            # High volume names
            'AMD', 'INTC', 'NFLX', 'CRM', 'ORCL'
        ]
        
        # Watchlist (Personal favorites to always include)
        self.PERSONAL_WATCHLIST = [
            # Blue chip favorites
            'AAPL', 'MSFT', 'JNJ', 'PG', 'KO',
            # Value plays
            'USB', 'TGT', 'CVS', 'XOM', 'CVX',
            # ETFs
            'SPY', 'QQQ', 'VTV', 'SCHD'
        ]

    # =================================================================
    # AUTOMATED SYSTEM CONTROL METHODS
    # =================================================================
    
    @classmethod
    def get_automated_strategy_override(cls) -> Tuple[str, str]:
        """
        Get strategy and stock list overrides for automated system
        
        Returns:
            Tuple of (strategy_override, stock_list_override)
            Both can be None if AUTO mode is selected
        """
        strategy_override = None
        stock_list_override = None
        
        if cls.AUTOMATED_STRATEGY_MODE == 'AUTO':
            # Let the system choose automatically based on market conditions
            strategy_override = None
            stock_list_override = None
            
        elif cls.AUTOMATED_STRATEGY_MODE == 'FORCE_STRATEGY':
            # Force a specific strategy
            strategy_override = cls.FORCED_STRATEGY
            stock_list_override = None
            
        elif cls.AUTOMATED_STRATEGY_MODE == 'FORCE_STOCK_LIST':
            # Force a specific stock list (let strategy be auto-selected)
            strategy_override = None
            stock_list_override = cls.FORCED_STOCK_LIST
            
        elif cls.AUTOMATED_STRATEGY_MODE == 'CUSTOM':
            # Use custom overrides (for advanced users)
            strategy_override = cls.CUSTOM_STRATEGY_OVERRIDE
            stock_list_override = cls.CUSTOM_STOCK_LIST_OVERRIDE
            
        return strategy_override, stock_list_override
    
    @classmethod
    def should_ignore_market_conditions(cls) -> bool:
        """Check if market conditions should be ignored for strategy selection"""
        return cls.IGNORE_MARKET_CONDITIONS
    
    @classmethod
    def get_fallback_strategy(cls) -> str:
        """Get the fallback strategy if preferred strategy fails"""
        return cls.FALLBACK_STRATEGY
    
    @classmethod
    def get_automated_system_summary(cls) -> Dict:
        """Get summary of automated system configuration"""
        strategy_override, stock_list_override = cls.get_automated_strategy_override()
        
        return {
            'mode': cls.AUTOMATED_STRATEGY_MODE,
            'strategy_override': strategy_override,
            'stock_list_override': stock_list_override,
            'ignore_market_conditions': cls.IGNORE_MARKET_CONDITIONS,
            'enable_retry': cls.ENABLE_STRATEGY_RETRY,
            'fallback_strategy': cls.FALLBACK_STRATEGY,
            'max_attempts': cls.MAX_STRATEGY_ATTEMPTS,
            'forced_strategy': cls.FORCED_STRATEGY,
            'forced_stock_list': cls.FORCED_STOCK_LIST
        }
    
    @classmethod
    def validate_strategy_override(cls, strategy_name: str) -> bool:
        """Validate that a strategy override is valid"""
        valid_strategies = [
            'BollingerMeanReversion',
            'GapTrading', 
            'BullishMomentumDipStrategy',
            'BullishMomentumDip',
            'InternationalStrategy',
            'International',
            'MicrostructureBreakoutStrategy', 
            'MicrostructureBreakout',
            'PolicyMomentumStrategy',
            'PolicyMomentum',
            'SectorRotationStrategy',
            'SectorRotation',
            'ValueRateStrategy',
            'ValueRate'
        ]
        return strategy_name in valid_strategies
    
    @classmethod
    def validate_stock_list_override(cls, stock_list_name: str) -> bool:
        """Validate that a stock list override is valid"""
        valid_stock_lists = [
            'BollingerMeanReversion',
            'GapTrading',
            'Core',
            'International',
            'SectorRotation',
            'ValueRate',
            'MicrostructureBreakout',
            'PolicyMomentum'
        ]
        return stock_list_name in valid_stock_lists

    # =================================================================
    # ENHANCED RULE ENFORCEMENT METHODS
    # =================================================================
    
    @classmethod
    def check_day_trading_violation(cls, symbol: str, signal_type: str, 
                                  recent_trades: List[Dict] = None) -> Tuple[bool, str]:
        """
        Check if executing this signal would violate day trading rules
        
        Args:
            symbol: Stock symbol
            signal_type: 'BUY' or 'SELL'
            recent_trades: List of recent trades from database/tracking
            
        Returns:
            Tuple of (is_violation: bool, reason: str)
        """
        if cls.ALLOW_DAY_TRADING:
            return False, "Day trading allowed"
        
        if not recent_trades:
            return False, "No recent trades to check"
        
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=cls.DAY_TRADING_LOOKBACK_HOURS)
        
        # Check for potential day trading violations
        for trade in recent_trades:
            trade_time_str = trade.get('timestamp', trade.get('date', ''))
            if not trade_time_str:
                continue
                
            try:
                trade_time = datetime.fromisoformat(trade_time_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                continue
            
            if trade_time < cutoff_time:
                continue  # Trade too old to matter
            
            trade_symbol = trade.get('symbol', '')
            trade_action = trade.get('action', trade.get('signal_type', ''))
            
            if trade_symbol != symbol:
                continue  # Different stock
            
            # Check for day trading pattern
            if signal_type == 'SELL' and trade_action == 'BUY':
                return True, f"Would be day trading: bought {symbol} at {trade_time.strftime('%H:%M')}, now selling same day"
            elif signal_type == 'BUY' and trade_action == 'SELL':
                return True, f"Would be day trading: sold {symbol} at {trade_time.strftime('%H:%M')}, now buying back same day"
        
        return False, "No day trading violation detected"
    
    @classmethod
    def check_short_selling_violation(cls, signal_type: str, current_positions: List[str], 
                                    symbol: str) -> Tuple[bool, str]:
        """
        Check if executing this signal would violate short selling rules
        
        Args:
            signal_type: 'BUY' or 'SELL'  
            current_positions: List of symbols currently held
            symbol: Stock symbol for the signal
            
        Returns:
            Tuple of (is_violation: bool, reason: str)
        """
        if cls.ALLOW_SHORT_SELLING:
            return False, "Short selling allowed"
        
        if signal_type == 'SELL' and symbol not in current_positions:
            return True, f"Would be short selling: no position in {symbol} to sell"
        
        return False, "No short selling violation detected"
    
    @classmethod
    def validate_signal_against_rules(cls, signal: Dict) -> Tuple[bool, List[str]]:
        """
        Comprehensive signal validation against all personal trading rules
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            Tuple of (is_valid: bool, violations: List[str])
        """
        violations = []
        signal_type = signal.get('signal_type', '')
        
        # Check if signal type violates our rules
        if signal_type not in ['BUY', 'SELL']:
            violations.append(f"Invalid signal type: {signal_type}")
        
        # Never allow SHORT signals 
        if signal_type == 'SHORT':
            violations.append("SHORT SELLING BLOCKED: Short selling not allowed")
        
        # Check for any strategy-specific rule violations
        strategy = signal.get('strategy', '')
        metadata = signal.get('metadata', '{}')
        
        try:
            import json
            metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
            
            # Check for any short-selling indicators in metadata
            if metadata_dict.get('requires_shorting', False):
                violations.append("STRATEGY BLOCKED: Strategy requires short selling")
            
            # Check for day trading strategy indicators
            if metadata_dict.get('is_day_trade', False) and not cls.ALLOW_DAY_TRADING:
                violations.append("DAY TRADING BLOCKED: Strategy marked as day trade")
                
        except (json.JSONDecodeError, TypeError):
            pass  # Ignore metadata parsing errors
        
        return len(violations) == 0, violations

    @classmethod
    def should_execute_signal(cls, signal, current_positions=None, account_value=0.0, 
                            recent_trades=None):
        """
        Enhanced signal execution check with proper rule enforcement
        
        Args:
            signal: Trading signal dictionary
            current_positions: List of current positions
            account_value: Total account value
            recent_trades: List of recent trades for day trading detection
            
        Returns:
            tuple: (should_execute: bool, reason: str)
        """
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        confidence = signal.get('confidence', 0)
        price = signal.get('price', 0)
        
        if current_positions is None:
            current_positions = []
        
        # CRITICAL RULE ENFORCEMENT - CHECK FIRST
        
        # 1. Check short selling rule (HIGHEST PRIORITY)
        is_short_violation, short_reason = cls.check_short_selling_violation(
            signal_type, current_positions, symbol
        )
        if is_short_violation:
            return False, f"SHORT SELLING BLOCKED: {short_reason}"
        
        # 2. Check day trading rule (HIGHEST PRIORITY)
        is_day_trade_violation, day_trade_reason = cls.check_day_trading_violation(
            symbol, signal_type, recent_trades
        )
        if is_day_trade_violation:
            return False, f"DAY TRADING BLOCKED: {day_trade_reason}"
        
        # 3. Validate signal structure
        is_valid, violations = cls.validate_signal_against_rules(signal)
        if not is_valid:
            return False, f"RULE VIOLATION: {'; '.join(violations)}"
        
        # 4. Check minimum confidence
        if confidence < cls.MIN_SIGNAL_CONFIDENCE:
            return False, f"Confidence {confidence:.1%} below minimum {cls.MIN_SIGNAL_CONFIDENCE:.1%}"
        
        # 5. Check if it's a buy-and-hold position
        if symbol in cls.BUY_AND_HOLD_POSITIONS and signal_type == 'SELL':
            return False, f"{symbol} is marked as buy-and-hold"
        
        # 6. Check position size limits for buys
        if signal_type == 'BUY':
            max_position_value = account_value * cls.MAX_POSITION_VALUE_PERCENT
            
            if max_position_value < cls.MIN_POSITION_VALUE:
                return False, f"Max position ${max_position_value:.2f} below minimum ${cls.MIN_POSITION_VALUE:.2f}"
            
            if max_position_value < cls.MIN_FRACTIONAL_ORDER:
                return False, f"Position ${max_position_value:.2f} below fractional minimum ${cls.MIN_FRACTIONAL_ORDER:.2f}"
        
        # 7. Check if we're at max positions
        if signal_type == 'BUY' and current_positions:
            if len(current_positions) >= cls.MAX_POSITIONS_TOTAL:
                return False, f"At maximum positions: {len(current_positions)}/{cls.MAX_POSITIONS_TOTAL}"
        
        return True, "Signal meets all criteria including personal trading rules"

    @classmethod
    def get_personal_scan_universe(cls, account_positions=None, settled_funds=0.0, vix_level=20):
        """
        Get personalized stock universe based on account, preferences, and market conditions
        With fractional shares enabled, focus on quality rather than price affordability
        
        Args:
            account_positions: List of current position symbols
            settled_funds: Available settled funds
            vix_level: Current VIX level for strategy filtering
            
        Returns:
            List of symbols to scan across all strategies
        """
        # This would need to import StockLists from your trading system
        # For now, using the personal watchlist and defined universes
        
        # Start with watchlist - need to access instance attribute through class
        config_instance = cls()
        scan_universe = config_instance.PERSONAL_WATCHLIST.copy()
        
        # Add current positions (except buy-and-hold)
        if account_positions:
            for symbol in account_positions:
                if symbol not in cls.BUY_AND_HOLD_POSITIONS:
                    scan_universe.append(symbol)
        
        # With fractional shares, affordability is based on minimum order size, not stock price
        min_order_affordable = settled_funds >= cls.MIN_FRACTIONAL_ORDER
        
        if min_order_affordable:
            print(f"💰 Fractional shares enabled: All stocks affordable (${cls.MIN_FRACTIONAL_ORDER:.2f} min)")
            
            # Add stocks from all strategy universes based on VIX level and quality
            
            # 2. Add International ETFs (unless VIX too high)
            if vix_level < cls.VIX_AGGRESSIVE_THRESHOLD:
                scan_universe.extend(config_instance.INTERNATIONAL_ETFS)
            
            # 3. Add Sector ETFs for rotation
            scan_universe.extend(config_instance.SECTOR_ETFS)
            
            # 4. Add REITs and Financials (Value-Rate strategy)
            scan_universe.extend(config_instance.REIT_UNIVERSE)
            scan_universe.extend(config_instance.FINANCIAL_UNIVERSE)
            
            # 5. Add Policy-sensitive stocks (if VIX moderate)
            if vix_level < cls.VIX_CONSERVATIVE_THRESHOLD:
                scan_universe.extend(config_instance.POLICY_SENSITIVE_STOCKS)
            
            # 6. Add Microstructure universe (high-volume stocks)
            scan_universe.extend(config_instance.MICROSTRUCTURE_UNIVERSE)
                    
        else:
            print(f"⚠️  Limited funds: ${settled_funds:.2f} < ${cls.MIN_FRACTIONAL_ORDER:.2f} minimum")
            print("   Only including current positions and watchlist")
        
        # Remove duplicates and sort
        scan_universe = list(set(scan_universe))
        scan_universe.sort()
        
        print(f"📊 Scan universe: {len(scan_universe)} stocks (fractional-enabled)")
        
        return scan_universe

    @classmethod
    def is_market_hours(cls):
        """Check if we're in preferred trading hours"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Simple time check (you might want to add market day checking)
        if cls.TRADING_START_TIME <= current_time <= cls.TRADING_END_TIME:
            return True
        
        return False
    
    @classmethod
    def get_position_size(cls, signal_price, account_value, settled_funds):
        """
        Calculate optimal position size with safety buffer for fractional orders
        
        Updated logic: With fractional shares, any stock is theoretically affordable.
        The constraints are:
        1. Minimum fractional order size ($5)
        2. Maximum position percentage (50% of account)
        3. Available settled funds
        4. Minimum position value for meaningful investment
        
        Args:
            signal_price: Price of the stock
            account_value: ACTUAL netLiquidation from Webull account
            settled_funds: Available settled funds
            
        Returns:
            dict: {'type': 'shares'/'dollars'/'none', 'amount': float, 'is_fractional': bool}
        """
        # Use the actual account value (netLiquidation) for percentage calculations
        max_by_percentage = account_value * cls.MAX_POSITION_VALUE_PERCENT
        max_by_funds = settled_funds
        
        max_position_value = min(max_by_percentage, max_by_funds)
        
        # Check if position meets minimum value requirement
        if max_position_value < cls.MIN_POSITION_VALUE:
            return {
                'type': 'none', 
                'amount': 0, 
                'is_fractional': False,
                'reason': f'Max position ${max_position_value:.2f} below minimum ${cls.MIN_POSITION_VALUE:.2f}'
            }
        
        # Check if we can afford minimum fractional order
        if max_position_value < cls.MIN_FRACTIONAL_ORDER:
            return {
                'type': 'none', 
                'amount': 0, 
                'is_fractional': False,
                'reason': f'Max position ${max_position_value:.2f} below fractional minimum ${cls.MIN_FRACTIONAL_ORDER:.2f}'
            }
        
        # Calculate whole shares first (preferred when possible)
        max_whole_shares = int(max_position_value / signal_price)
        
        # If we can afford at least one whole share and it meets minimum value
        if max_whole_shares >= 1:
            whole_share_value = max_whole_shares * signal_price
            if whole_share_value >= cls.MIN_POSITION_VALUE:
                return {
                    'type': 'shares',
                    'amount': float(max_whole_shares),
                    'is_fractional': False,
                    'whole_share_value': whole_share_value
                }
        
        # Use fractional shares with safety buffer
        # Apply buffer to avoid price movement issues and API failures
        buffered_amount = max_position_value * cls.FRACTIONAL_FUND_BUFFER
        
        # Final check against minimum fractional order size
        if buffered_amount < cls.MIN_FRACTIONAL_ORDER:
            return {
                'type': 'none', 
                'amount': 0, 
                'is_fractional': False,
                'reason': f'Buffered amount ${buffered_amount:.2f} below minimum ${cls.MIN_FRACTIONAL_ORDER:.2f}'
            }
        
        # Use buffered dollar-amount ordering for fractional shares
        return {
            'type': 'dollars',
            'amount': round(buffered_amount, 2),  # Round to nearest cent
            'is_fractional': True,
            'buffer_applied': True,
            'original_amount': round(max_position_value, 2),
            'buffer_percentage': cls.FRACTIONAL_FUND_BUFFER,
            'estimated_shares': round(buffered_amount / signal_price, 4)
        }
    
    @classmethod
    def get_fractional_capability_info(cls, account_value, settled_funds):
        """
        Get information about fractional share capabilities
        
        Returns:
            dict: Fractional share capability analysis
        """
        max_position = account_value * cls.MAX_POSITION_VALUE_PERCENT
        available_for_position = min(max_position, settled_funds)
        
        # Fractional capability thresholds
        can_make_any_position = available_for_position >= cls.MIN_FRACTIONAL_ORDER
        can_make_meaningful_position = available_for_position >= cls.MIN_POSITION_VALUE
        
        # Calculate how many different stocks we could theoretically buy
        if can_make_any_position:
            max_fractional_positions = int(settled_funds / cls.MIN_FRACTIONAL_ORDER)
        else:
            max_fractional_positions = 0
        
        return {
            'fractional_enabled': True,
            'can_buy_any_stock': can_make_any_position,
            'can_make_meaningful_position': can_make_meaningful_position,
            'min_order_amount': cls.MIN_FRACTIONAL_ORDER,
            'min_position_value': cls.MIN_POSITION_VALUE,
            'max_position_amount': available_for_position,
            'theoretical_max_positions': min(max_fractional_positions, cls.MAX_POSITIONS_TOTAL),
            'funds_needed_for_min': max(0, cls.MIN_FRACTIONAL_ORDER - settled_funds),
            'buffer_percentage': cls.FRACTIONAL_FUND_BUFFER * 100
        }
    
    @classmethod
    def is_fractional_position(cls, quantity):
        """Check if a quantity represents a fractional position"""
        return quantity != int(quantity) or quantity < 1.0
    
    @classmethod
    def get_account_allocation_info(cls, account_value, settled_funds, current_positions):
        """
        Get detailed account allocation information
        
        Args:
            account_value: ACTUAL netLiquidation from Webull
            settled_funds: Available cash
            current_positions: List of current positions
            
        Returns:
            dict: Allocation analysis
        """
        total_position_value = sum(pos.get('market_value', 0) for pos in current_positions)
        cash_percentage = (settled_funds / account_value * 100) if account_value > 0 else 0
        positions_percentage = (total_position_value / account_value * 100) if account_value > 0 else 0
        
        # Calculate maximum new position size
        max_new_position = account_value * cls.MAX_POSITION_VALUE_PERCENT
        max_affordable_with_cash = settled_funds
        
        return {
            'account_value': account_value,
            'settled_funds': settled_funds,
            'total_position_value': total_position_value,
            'cash_percentage': cash_percentage,
            'positions_percentage': positions_percentage,
            'max_new_position': min(max_new_position, max_affordable_with_cash),
            'positions_count': len(current_positions),
            'max_positions': cls.MAX_POSITIONS_TOTAL,
            'available_position_slots': max(0, cls.MAX_POSITIONS_TOTAL - len(current_positions))
        }
    
    @classmethod
    def format_signal_display(cls, signal, position_data=None):
        """
        Format signal for display with fractional share information
        """
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        price = signal['price']
        confidence = signal.get('confidence', 0)
        
        # Base display
        display = f"{signal_type} {symbol} @ ${price:.2f} ({confidence:.1%})"
        
        # Add fractional indicator for buys
        if signal_type == 'BUY' and signal.get('fractional_order', False):
            display += " 📊"  # Fractional indicator
        
        # Add position info for sells
        if signal_type == 'SELL' and position_data:
            pnl = position_data.get('unrealized_pnl', 0)
            pnl_pct = position_data.get('pnl_rate', 0) * 100
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"
            display += f" {pnl_emoji} P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)"
            
            # Add fractional indicator if it's a fractional position
            if position_data.get('quantity', 1) != int(position_data.get('quantity', 1)):
                display += " 📊"
        
        # Add strategy info if available
        if 'metadata' in signal:
            try:
                import json
                metadata = json.loads(signal['metadata'])
                if 'strategy_logic' in metadata:
                    strategy = metadata['strategy_logic'].replace('_', ' ').title()
                    display += f" [{strategy}]"
            except:
                pass
        
        return display

    @classmethod
    def get_rule_enforcement_summary(cls):
        """Get a summary of current rule enforcement settings"""
        return {
            'short_selling_allowed': cls.ALLOW_SHORT_SELLING,
            'day_trading_allowed': cls.ALLOW_DAY_TRADING,
            'day_trading_lookback_hours': cls.DAY_TRADING_LOOKBACK_HOURS,
            'max_position_percent': cls.MAX_POSITION_VALUE_PERCENT,
            'min_position_value': cls.MIN_POSITION_VALUE,
            'max_positions_total': cls.MAX_POSITIONS_TOTAL,
            'min_signal_confidence': cls.MIN_SIGNAL_CONFIDENCE,
            'personal_stop_loss': cls.PERSONAL_STOP_LOSS,
            'personal_take_profit': cls.PERSONAL_TAKE_PROFIT,
            'min_fractional_order': cls.MIN_FRACTIONAL_ORDER,
            'rule_enforcement_active': True
        }


# Example usage and validation
def validate_personal_config():
    """Validate personal configuration settings"""
    config = PersonalTradingConfig()
    
    print("🔧 PERSONAL TRADING CONFIGURATION")
    print("=" * 50)
    print(f"Short Selling: {'❌ BLOCKED' if not config.ALLOW_SHORT_SELLING else '✅ Enabled'}")
    print(f"Day Trading: {'❌ BLOCKED' if not config.ALLOW_DAY_TRADING else '✅ Enabled'}")
    print(f"Max Position: {config.MAX_POSITION_VALUE_PERCENT:.1%} of account")
    print(f"Min Position: ${config.MIN_POSITION_VALUE}")
    print(f"Max Positions: {config.MAX_POSITIONS_TOTAL}")
    print(f"Stop Loss: {config.PERSONAL_STOP_LOSS:.1%}")
    print(f"Take Profit: {config.PERSONAL_TAKE_PROFIT:.1%}")
    print(f"Min Confidence: {config.MIN_SIGNAL_CONFIDENCE:.1%}")
    print(f"Trading Hours: {config.TRADING_START_TIME} - {config.TRADING_END_TIME}")
    print(f"Watchlist: {len(config.PERSONAL_WATCHLIST)} stocks")
    
    print("\n🤖 AUTOMATED SYSTEM CONFIGURATION")
    print("=" * 50)
    
    # Get current automated system settings
    summary = config.get_automated_system_summary()
    
    print(f"Strategy Mode: {summary['mode']}")
    print(f"Strategy Override: {summary['strategy_override']}")
    print(f"Stock List Override: {summary['stock_list_override']}")
    print(f"Ignore Market Conditions: {summary['ignore_market_conditions']}")
    print(f"Enable Retry: {summary['enable_retry']}")
    print(f"Fallback Strategy: {summary['fallback_strategy']}")
    print(f"Max Attempts: {summary['max_attempts']}")
    
    # Test rule enforcement
    print(f"\n🛡️ RULE ENFORCEMENT TEST")
    print("=" * 50)
    
    # Test short selling detection
    is_violation, reason = config.check_short_selling_violation('SELL', [], 'AAPL')
    print(f"Short Selling Test: {'❌ BLOCKED' if is_violation else '✅ Allowed'} - {reason}")
    
    # Test signal validation
    test_signal = {
        'symbol': 'AAPL',
        'signal_type': 'BUY',
        'price': 150.0,
        'confidence': 0.75
    }
    
    should_execute, reason = config.should_execute_signal(
        test_signal, 
        current_positions=['MSFT', 'JNJ'], 
        account_value=10000
    )
    
    print(f"\nTest Signal: {test_signal['symbol']} {test_signal['signal_type']}")
    print(f"Should Execute: {'✅ Yes' if should_execute else '❌ No'}")
    print(f"Reason: {reason}")
    
    # Test invalid signal
    invalid_signal = {
        'symbol': 'AAPL',
        'signal_type': 'SHORT',  # This should be blocked
        'price': 150.0,
        'confidence': 0.75
    }
    
    is_valid, violations = config.validate_signal_against_rules(invalid_signal)
    print(f"\nInvalid Signal Test: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if violations:
        print(f"Violations: {'; '.join(violations)}")
    
    # Test position sizing
    print(f"\n💰 POSITION SIZING TEST")
    print("=" * 50)
    position_info = config.get_position_size(150.0, 10000, 1000)
    print(f"Stock Price: $150.00")
    print(f"Account Value: $10,000")
    print(f"Available Cash: $1,000")
    print(f"Position Type: {position_info['type']}")
    print(f"Position Amount: {position_info['amount']}")
    print(f"Is Fractional: {position_info['is_fractional']}")
    
    print(f"\n📋 AVAILABLE STRATEGY MODES:")
    print("  • AUTO: Let system choose based on market conditions")
    print("  • FORCE_STRATEGY: Always use specific strategy")
    print("  • FORCE_STOCK_LIST: Use specific stock list, auto strategy")
    print("  • CUSTOM: Use custom strategy and stock list overrides")
    
    print(f"\n🎯 AVAILABLE STRATEGIES:")
    strategies = [
        'BollingerMeanReversion', 'GapTrading', 'BullishMomentumDipStrategy',
        'International', 'MicrostructureBreakout', 'PolicyMomentum',
        'SectorRotation', 'ValueRateStrategy'
    ]
    for strategy in strategies:
        print(f"  • {strategy}")
    
    print(f"\n📊 AVAILABLE STOCK LISTS:")
    stock_lists = [
        'BollingerMeanReversion', 'GapTrading', 'Core', 'International',
        'SectorRotation', 'ValueRate', 'MicrostructureBreakout', 'PolicyMomentum'
    ]
    for stock_list in stock_lists:
        print(f"  • {stock_list}")

if __name__ == "__main__":
    validate_personal_config()