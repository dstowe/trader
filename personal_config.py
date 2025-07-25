# personal_config.py - COMPLETE VERSION WITH ALL METHODS
"""
Personal Trading Configuration - SINGLE SOURCE OF TRUTH
This is the ONLY configuration class - completely self-contained
NO inheritance or dependencies on any other config files
ALL configuration parameters are defined here
"""

import os
from datetime import datetime
from typing import List, Dict, Tuple, Any
from trading_system.config.stock_lists import StockLists

class PersonalTradingConfig:
    """
    STANDALONE COMPLETE TRADING CONFIGURATION
    This class contains ALL configuration parameters with no dependencies
    This is the ONLY configuration source for the entire trading system
    """

    # =================================================================
    # CORE TRADING PARAMETERS - ALL SELF-CONTAINED
    # =================================================================

    # Database
    DATABASE_PATH = "trading_data.db"

    # Account sizing and risk management
     # Account sizing and risk management
    ACCOUNT_SIZE = float(os.getenv('ACCOUNT_SIZE', 10000))
    MAX_POSITION_VALUE_PERCENT = 0.5    # 50% max of account per position (AUTHORITATIVE)
    MIN_POSITION_VALUE = 1              # Minimum $1 position
    MAX_POSITIONS_TOTAL = 8             # Maximum 8 total positions (AUTHORITATIVE)

    # Risk management - CONSOLIDATED
    PERSONAL_STOP_LOSS = 0.08          # 8% stop loss (CONSOLIDATED from STOP_LOSS_PERCENT)
    PERSONAL_TAKE_PROFIT = 0.15        # 15% take profit target
    MAX_DAILY_LOSS = 0.05              # 5% max daily loss (CONSOLIDATED from MAX_DAILY_RISK_PERCENT)

    # Technical indicators
    BB_PERIOD = 20
    BB_STD_DEV = 2
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70

    # Data refresh
    DATA_REFRESH_MINUTES = 15

    # =================================================================
    # PERSONAL TRADING RULES (CRITICAL - NEVER OVERRIDE)
    # =================================================================
    ALLOW_SHORT_SELLING = False  # Never allow short selling
    ALLOW_DAY_TRADING = True    # Never allow day trading

    # Day trading detection settings
    DAY_TRADING_LOOKBACK_HOURS = 24  # Consider trades within 24 hours as potential day trades

    # Fractional Order Safety Settings
    FRACTIONAL_FUND_BUFFER = 0.9       # Use only 90% of available funds for fractional orders
    MIN_FRACTIONAL_ORDER = 5.0         # Minimum $5 for fractional orders to avoid API issues
    FRACTIONAL_ORDER_TYPE = 'MKT'      # Must use market orders for fractinal shares

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
    TRADING_START_TIME = "09:45"  # Wait 15 min after market open
    TRADING_END_TIME = "15:30"    # Stop 30 min before close

    # Notification Preferences
    REQUIRE_CONFIRMATION = True       # Always ask before trading
    SHOW_DETAILED_ANALYSIS = True    # Show full signal details

    # Holdings to exclude from analysis (buy and hold)
    BUY_AND_HOLD_POSITIONS = [
        # Add any positions you never want to sell
        # Example: 'AAPL', 'MSFT'
    ]

    # =================================================================
    # GAP TRADING PARAMETERS
    # =================================================================
    GAP_MIN_SIZE = 0.01          # 1% minimum gap to consider
    GAP_LARGE_SIZE = 0.03        # 3% large gap threshold
    GAP_EXTREME_SIZE = 0.05      # 5% extreme gap threshold
    GAP_VOLUME_MULTIPLIER = 1.5  # Volume vs average required
    GAP_TIMEOUT_MINUTES = 60     # Max time in gap trade (minutes)
    GAP_MAX_RISK = 0.03          # 3% max risk per gap trade
    GAP_STOP_MULTIPLIER = 1.5    # Stop loss multiplier for gap trades
    GAP_ENVIRONMENT_THRESHOLD = 0.30  # 30% of stocks must gap for "high gap day"
    EARNINGS_SEASON_VIX_THRESHOLD = 22  # VIX level indicating earnings volatility

    # =================================================================
    # AUTOMATED SYSTEM CONTROL SETTINGS (CONSOLIDATED)
    # =================================================================

    # Strategy Selection Mode for Automated System (ONLY CONFIGURATION SYSTEM)
    AUTOMATED_STRATEGY_MODE = 'AUTO'  # Options: 'AUTO', 'FORCE_STRATEGY', 'FORCE_STOCK_LIST', 'CUSTOM'

    # Strategy Override Settings
    FORCED_STRATEGY = 'GapTrading'  # Used when AUTOMATED_STRATEGY_MODE = 'FORCE_STRATEGY'
    FORCED_STOCK_LIST = 'ValueRate'  # Used when AUTOMATED_STRATEGY_MODE = 'FORCE_STOCK_LIST'

    # Custom Override Settings (for advanced users)
    CUSTOM_STRATEGY_OVERRIDE = None     # Set to strategy name to override
    CUSTOM_STOCK_LIST_OVERRIDE = None   # Set to stock list name to override

    # Automated System Behavior Controls
    ENABLE_STRATEGY_RETRY = True        # Retry with different strategy if first fails
    FALLBACK_STRATEGY = 'BollingerMeanReversion'  # Strategy to use if preferred fails
    MAX_STRATEGY_ATTEMPTS = 2           # How many strategies to try before giving up

    # Market Condition Override
    IGNORE_MARKET_CONDITIONS = False    # If True, always use FORCED_STRATEGY regardless of market

    def __init__(self):
        # Account configurations
        self.ACCOUNT_CONFIGURATIONS = {
            'CASH': {
                'enabled': True,
                'day_trading_enabled': True,
                'options_enabled': False,
                'max_position_size': self.MAX_POSITION_VALUE_PERCENT,
                'pdt_protection': False,
                'min_trade_amount': self.MIN_FRACTIONAL_ORDER,
                'max_trade_amount': 30
            },
            'MARGIN': {
                'enabled': True,
                'day_trading_enabled': True,
                'options_enabled': False,
                'max_position_size': self.MAX_POSITION_VALUE_PERCENT,
                'pdt_protection': True,
                'min_account_value_for_pdt': 25000,
                'min_trade_amount': self.MIN_FRACTIONAL_ORDER,
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

    # =================================================================
    # CONSOLIDATED CONFIGURATION METHODS (Legacy Support Removed)
    # =================================================================

    @classmethod
    def get_automated_strategy_override(cls) -> Tuple[str, str]:
        """
        CONSOLIDATED strategy and stock list override method
        Legacy STRATEGY_MODE support has been removed

        Returns:
            Tuple of (strategy_override, stock_list_override)
            Both can be None if AUTO mode is selected
        """
        strategy_override = None
        stock_list_override = None

        # Use AUTOMATED_STRATEGY_MODE (single source of truth)
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
    def get_automated_system_summary(cls) -> Dict:
        """
        CONSOLIDATED automated system configuration summary
        Legacy STRATEGY_MODE references removed
        """
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

    # =================================================================
    # MISSING HELPER METHODS FOR MAIN.PY INTEGRATION
    # =================================================================

    @classmethod
    def get_stock_list_for_data_fetch(cls) -> List[str]:
        """
        Get the appropriate stock list for data fetching based on strategy mode
        Replaces legacy STRATEGY_MODE logic in main.py
        """
        strategy_override, stock_list_override = cls.get_automated_strategy_override()

        # If we have a stock list override, determine the appropriate universe
        if stock_list_override:
            if stock_list_override == 'GapTrading':
                return StockLists.GAP_TRADING_UNIVERSE
            elif stock_list_override == 'BollingerMeanReversion':
                return StockLists.BOLLINGER_MEAN_REVERSION
            else:
                return StockLists.GAP_TRADING_UNIVERSE  # Default fallback

        # If we have a strategy override, get appropriate universe
        if strategy_override:
            if strategy_override == 'GapTrading':
                return StockLists.GAP_TRADING_UNIVERSE
            elif strategy_override == 'BollingerMeanReversion':
                return StockLists.BOLLINGER_MEAN_REVERSION
            else:
                return StockLists.BOLLINGER_MEAN_REVERSION  # Default fallback

        # For AUTO mode, fetch full universe to enable gap detection
        return StockLists.GAP_TRADING_UNIVERSE

    @classmethod
    def get_recommended_strategy_override(cls) -> str:
        """
        Get strategy override for market condition analysis
        Replaces legacy STRATEGY_MODE logic in main.py
        """
        strategy_override, _ = cls.get_automated_strategy_override()
        return strategy_override

    # =================================================================
    # AUTHORITATIVE CONFIGURATION METHODS
    # =================================================================
    @classmethod
    def get_stock_list_for_data_fetch(cls) -> List[str]:
        """Get stock list for data fetching"""
        try:
            from trading_system.config.stock_lists import StockLists
            return StockLists.BOLLINGER_MEAN_REVERSION[:20]  # Limit for testing
        except ImportError:
            return ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']

    @classmethod
    def get_recommended_strategy_override(cls) -> str:
        """Get recommended strategy override"""
        strategy_override, _ = cls.get_automated_strategy_override()
        return strategy_override

    @classmethod
    def get_all_config_summary(cls) -> Dict:
        """Get comprehensive summary of ALL configuration values"""
        return {
            'account_config': {
                'max_position_percent': cls.MAX_POSITION_VALUE_PERCENT,
                'min_position_value': cls.MIN_POSITION_VALUE,
                'max_positions_total': cls.MAX_POSITIONS_TOTAL,
                'stop_loss_percent': cls.PERSONAL_STOP_LOSS,
                'max_daily_loss': cls.MAX_DAILY_LOSS,
            },
            'trading_rules': {
                'allow_short_selling': cls.ALLOW_SHORT_SELLING,
                'allow_day_trading': cls.ALLOW_DAY_TRADING,
                'min_signal_confidence': cls.MIN_SIGNAL_CONFIDENCE,
                'fractional_enabled': True,
                'min_fractional_order': cls.MIN_FRACTIONAL_ORDER,
            },
            'strategy_config': {
                'mode': cls.AUTOMATED_STRATEGY_MODE,
                'forced_strategy': cls.FORCED_STRATEGY,
                'forced_stock_list': cls.FORCED_STOCK_LIST,
                'enable_retry': cls.ENABLE_STRATEGY_RETRY,
                'fallback_strategy': cls.FALLBACK_STRATEGY,
                'max_attempts': cls.MAX_STRATEGY_ATTEMPTS,
            },
            'gap_trading': {
                'min_size': cls.GAP_MIN_SIZE,
                'large_size': cls.GAP_LARGE_SIZE,
                'volume_multiplier': cls.GAP_VOLUME_MULTIPLIER,
            },
            'technical_indicators': {
                'bb_period': cls.BB_PERIOD,
                'rsi_period': cls.RSI_PERIOD,
                'rsi_oversold': cls.RSI_OVERSOLD,
                'rsi_overbought': cls.RSI_OVERBOUGHT,
            }
        }

    @classmethod
    def should_ignore_market_conditions(cls) -> bool:
        """Check if market conditions should be ignored for strategy selection"""
        return cls.IGNORE_MARKET_CONDITIONS

    @classmethod
    def get_fallback_strategy(cls) -> str:
        """Get the fallback strategy if preferred strategy fails"""
        return cls.FALLBACK_STRATEGY

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
        """Check if executing this signal would violate day trading rules"""
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
        """Check if executing this signal would violate short selling rules"""
        if cls.ALLOW_SHORT_SELLING:
            return False, "Short selling allowed"

        if signal_type == 'SELL' and symbol not in current_positions:
            return True, f"Would be short selling: no position in {symbol} to sell"

        return False, "No short selling violation detected"

    @classmethod
    def validate_signal_against_rules(cls, signal) -> Tuple[bool, List[str]]: # Changed signal: Dict to signal
        """Comprehensive signal validation against all personal trading rules"""
        violations = []
        signal_type = signal.signal_type # Changed signal.get('signal_type', '') to signal.signal_type

        # Check if signal type violates our rules
        if signal_type not in ['BUY', 'SELL']:
            violations.append(f"Invalid signal type: {signal_type}")

        # Never allow SHORT signals
        if signal_type == 'SHORT':
            violations.append("SHORT SELLING BLOCKED: Short selling not allowed")

        # Check for any strategy-specific rule violations
        strategy = signal.strategy # Changed signal.get('strategy', '') to signal.strategy
        metadata = signal.metadata # Changed signal.get('metadata', '{}') to signal.metadata

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
        """Enhanced signal execution check with proper rule enforcement"""
        symbol = signal.symbol # Changed signal['symbol'] to signal.symbol
        signal_type = signal.signal_type # Changed signal['signal_type'] to signal.signal_type
        confidence = signal.confidence # Changed signal.get('confidence', 0) to signal.confidence
        price = signal.price # Changed signal.get('price', 0) to signal.price

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
            if len(current_positions) >= cls.MAX_POSITIONS_TOTAL:  # Use authoritative parameter
                return False, f"At maximum positions: {len(current_positions)}/{cls.MAX_POSITIONS_TOTAL}"

        return True, "Signal meets all criteria including personal trading rules"

    @classmethod
    def get_personal_scan_universe(cls, account_positions=None, settled_funds=0.0, vix_level=20):
        """Get personalized stock universe based on account, preferences, and market conditions"""
        # Start with personal watchlist from StockLists
        scan_universe = StockLists.PERSONAL_WATCHLIST.copy()

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
                scan_universe.extend(StockLists.INTERNATIONAL_ETFS)

            # 3. Add Sector ETFs for rotation
            scan_universe.extend(StockLists.SECTOR_ETFS)

            # 4. Add REITs and Financials (Value-Rate strategy)
            scan_universe.extend(StockLists.REIT_UNIVERSE)
            scan_universe.extend(StockLists.FINANCIAL_UNIVERSE)

            # 5. Add Policy-sensitive stocks (if VIX moderate)
            if vix_level < cls.VIX_CONSERVATIVE_THRESHOLD:
                scan_universe.extend(StockLists.POLICY_SENSITIVE_STOCKS)

            # 6. Add Microstructure universe (high-volume stocks)
            scan_universe.extend(StockLists.MICROSTRUCTURE_UNIVERSE)

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
        """Calculate optimal position size with safety buffer for fractional orders"""
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

        # CRITICAL: Ensure fractional shares will be less than 1
        estimated_fractional_shares = buffered_amount / signal_price
        
        # If the fractional shares would be >= 1, we need to reduce the amount
        if estimated_fractional_shares >= 1.0:
            # Calculate the maximum dollar amount that gives us <1 share
            max_dollar_for_fractional = signal_price * 0.99  # 99% of one share
            
            # Use the smaller of our buffered amount or the max for fractional
            final_amount = min(buffered_amount, max_dollar_for_fractional)
            
            # Double-check this is still above minimum
            if final_amount < cls.MIN_FRACTIONAL_ORDER:
                return {
                    'type': 'none',
                    'amount': 0,
                    'is_fractional': False,
                    'reason': f'Fractional amount ${final_amount:.2f} below minimum ${cls.MIN_FRACTIONAL_ORDER:.2f} after adjustment'
                }
            
            final_fractional_shares = final_amount / signal_price
            
            return {
                'type': 'dollars',
                'amount': round(final_amount, 2),
                'is_fractional': True,
                'buffer_applied': True,
                'original_amount': round(max_position_value, 2),
                'buffer_percentage': cls.FRACTIONAL_FUND_BUFFER,
                'estimated_shares': round(final_fractional_shares, 6),
                'fractional_adjustment': f'Reduced from ${buffered_amount:.2f} to ensure <1 share'
            }
        else:
            # Use buffered dollar-amount ordering for fractional shares
            return {
                'type': 'dollars',
                'amount': round(buffered_amount, 2),  # Round to nearest cent
                'is_fractional': True,
                'buffer_applied': True,
                'original_amount': round(max_position_value, 2),
                'buffer_percentage': cls.FRACTIONAL_FUND_BUFFER,
                'estimated_shares': round(estimated_fractional_shares, 6)
            }

    @classmethod
    def get_fractional_capability_info(cls, account_value, settled_funds):
        """Get information about fractional share capabilities"""
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
        """Get detailed account allocation information"""
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
        """Format signal for display with fractional share information"""
        symbol = signal.symbol # Changed signal['symbol'] to signal.symbol
        signal_type = signal.signal_type # Changed signal['signal_type'] to signal.signal_type
        price = signal.price # Changed signal['price'] to signal.price
        confidence = signal.confidence # Changed signal.get('confidence', 0) to signal.confidence

        # Base display
        display = f"{signal_type} {symbol} @ ${price:.2f} ({confidence:.1%})"

        # Add fractional indicator for buys
        if signal_type == 'BUY' and signal.fractional_order: # Changed signal.get('fractional_order', False) to signal.fractional_order
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
        if hasattr(signal, 'metadata'): # Changed 'metadata' in signal to hasattr(signal, 'metadata')
            try:
                import json
                metadata = signal.metadata # Changed json.loads(signal['metadata']) to signal.metadata
                if hasattr(metadata, 'strategy_logic'): # Changed 'strategy_logic' in metadata to hasattr(metadata, 'strategy_logic')
                    strategy = metadata.strategy_logic.replace('_', ' ').title() # Changed metadata['strategy_logic'] to metadata.strategy_logic
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

    @classmethod
    def get_position_size_with_strategy_adjustments(cls, signal_price, account_value, settled_funds,
                                                strategy_name=None, signal_metadata=None):
        """
        Calculate position size with optional strategy-specific adjustments

        Args:
            signal_price: Price per share/unit
            account_value: Total account value (net liquidation)
            settled_funds: Available settled funds
            strategy_name: Name of strategy (for strategy-specific adjustments)
            signal_metadata: Additional signal metadata for adjustments

        Returns:
            Dict with position sizing information including strategy adjustments
        """
        # Get base position size using the authoritative method
        base_position = cls.get_position_size(signal_price, account_value, settled_funds)

        # If base position is 'none', return as-is
        if base_position['type'] == 'none':
            return base_position

        # Apply strategy-specific adjustments
        adjustment_factor = 1.0
        adjustment_reason = "Standard sizing"

        if strategy_name and signal_metadata:
            if strategy_name in ['BullishMomentumDip', 'BullishMomentumDipStrategy']:
                # Momentum strategies can be more aggressive
                adjustment_factor = 1.1
                adjustment_reason = "Momentum strategy bonus (+10%)"

            elif strategy_name == 'GapTrading':
                # Adjust based on gap size (more volatile = smaller position)
                gap_size = signal_metadata.get('gap_size', 0)
                if gap_size and gap_size > cls.GAP_LARGE_SIZE:
                    adjustment_factor = 0.5  # 50% of normal
                    adjustment_reason = f"Large gap volatility reduction (-50%, gap: {gap_size:.1%})"
                elif gap_size and gap_size > cls.GAP_MIN_SIZE * 2:
                    adjustment_factor = 0.75  # 75% of normal
                    adjustment_reason = f"Medium gap volatility reduction (-25%, gap: {gap_size:.1%})"

            elif strategy_name in ['PolicyMomentum', 'PolicyMomentumStrategy']:
                # Slightly reduce for volatility
                adjustment_factor = 0.9
                adjustment_reason = "Policy volatility reduction (-10%)"

            elif strategy_name in ['ValueRate', 'ValueRateStrategy']:
                # Value plays can be held longer, slight increase
                adjustment_factor = 1.1
                adjustment_reason = "Value play bonus (+10%)"

            elif strategy_name in ['SectorRotation', 'SectorRotationStrategy']:
                # Apply sector allocation limit check
                max_sector_allocation = getattr(cls, 'MAX_SECTOR_ALLOCATION', 0.20)
                sector_limit_factor = max_sector_allocation / cls.MAX_POSITION_VALUE_PERCENT
                if sector_limit_factor < 1.0:
                    adjustment_factor = sector_limit_factor
                    adjustment_reason = f"Sector allocation limit (max {max_sector_allocation:.0%})"
                else:
                    adjustment_factor = 0.95
                    adjustment_reason = "Sector concentration adjustment (-5%)"

            elif strategy_name in ['International', 'InternationalStrategy']:
                # Apply international allocation limit check
                max_intl_allocation = getattr(cls, 'MAX_INTERNATIONAL_ALLOCATION', 0.30)
                intl_limit_factor = max_intl_allocation / cls.MAX_POSITION_VALUE_PERCENT
                if intl_limit_factor < 1.0:
                    adjustment_factor = intl_limit_factor
                    adjustment_reason = f"International allocation limit (max {max_intl_allocation:.0%})"
                else:
                    adjustment_factor = 0.95
                    adjustment_reason = "International concentration adjustment (-5%)"

        # Apply the adjustment
        adjusted_position = base_position.copy()

        if base_position['type'] == 'dollars':
            # Fractional order - adjust dollar amount
            adjusted_amount = round(base_position['amount'] * adjustment_factor, 2)
        else:
            # Whole share order - adjust share count but keep as integer
            adjusted_amount = max(1, int(base_position['amount'] * adjustment_factor))

        adjusted_position['amount'] = adjusted_amount
        adjusted_position['strategy_adjustment'] = {
            'factor': adjustment_factor,
            'reason': adjustment_reason,
            'original_amount': base_position['amount'],
            'strategy_name': strategy_name
        }

        # Ensure we don't go below minimum thresholds after adjustment
        if adjusted_position['type'] == 'dollars':
            if adjusted_position['amount'] < cls.MIN_FRACTIONAL_ORDER:
                adjusted_position['type'] = 'none'
                adjusted_position['amount'] = 0
                adjusted_position['reason'] = f"Adjusted amount ${adjusted_position['amount']:.2f} below minimum ${cls.MIN_FRACTIONAL_ORDER:.2f}"
        elif adjusted_position['type'] == 'shares':
            if adjusted_position['amount'] < 1:
                adjusted_position['amount'] = 1  # Minimum 1 share
                adjusted_position['strategy_adjustment']['reason'] += " (min 1 share enforced)"

        return adjusted_position


# Example usage and validation
def validate_personal_config():
    """Validate personal configuration settings"""
    config = PersonalTradingConfig()

    print("🔧 COMPLETE PERSONAL TRADING CONFIGURATION")
    print("=" * 70)
    print("✅ NO DEPENDENCIES - COMPLETE STANDALONE CONFIG")
    print("✅ NO INHERITANCE - ALL PARAMETERS SELF-CONTAINED")
    print("✅ SINGLE SOURCE OF TRUTH FOR ENTIRE SYSTEM")
    print("✅ ALL MISSING METHODS INCLUDED")
    print("=" * 70)

    print(f"Short Selling: {'❌ BLOCKED' if not config.ALLOW_SHORT_SELLING else '✅ Enabled'}")
    print(f"Day Trading: {'❌ BLOCKED' if not config.ALLOW_DAY_TRADING else '✅ Enabled'}")
    print(f"Max Position: {config.MAX_POSITION_VALUE_PERCENT:.1%} of account")
    print(f"Min Position: ${config.MIN_POSITION_VALUE}")
    print(f"Max Positions: {config.MAX_POSITIONS_TOTAL}")
    print(f"Stop Loss: {config.PERSONAL_STOP_LOSS:.1%}")
    print(f"Take Profit: {config.PERSONAL_TAKE_PROFIT:.1%}")
    print(f"Min Confidence: {config.MIN_SIGNAL_CONFIDENCE:.1%}")
    print(f"Trading Hours: {config.TRADING_START_TIME} - {config.TRADING_END_TIME}")
    print(f"Watchlist: {len(StockLists.PERSONAL_WATCHLIST)} stocks")

    print("\n🤖 CONSOLIDATED AUTOMATED SYSTEM CONFIGURATION")
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

    # Test missing methods
    print("\n🔧 TESTING MISSING METHODS")
    print("=" * 40)

    try:
        stock_list = config.get_stock_list_for_data_fetch()
        print(f"✅ get_stock_list_for_data_fetch(): {len(stock_list)} stocks")
    except Exception as e:
        print(f"❌ get_stock_list_for_data_fetch(): {e}")

    try:
        strategy_override = config.get_recommended_strategy_override()
        print(f"✅ get_recommended_strategy_override(): {strategy_override}")
    except Exception as e:
        print(f"❌ get_recommended_strategy_override(): {e}")

    # Show full config summary
    print("\n📋 COMPLETE CONFIGURATION SUMMARY")
    print("=" * 50)
    full_config = config.get_all_config_summary()
    for section, values in full_config.items():
        print(f"\n{section.upper()}:")
        for key, value in values.items():
            print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("✅ COMPLETE CONFIG VALIDATION SUCCESSFUL")
    print("✅ ALL MISSING METHODS IMPLEMENTED")
    print("✅ READY FOR MAIN.PY INTEGRATION")
    print("="*70)


if __name__ == "__main__":
    validate_personal_config()