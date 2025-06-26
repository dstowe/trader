# personal_config.py
"""
Personal Trading Configuration
Extends the base TradingConfig with personal preferences
"""

import os
from datetime import datetime
from trading_system.config.settings import TradingConfig

class PersonalTradingConfig(TradingConfig):
    """Extended configuration for personal trading system"""
    
    # Personal Trading Rules
    ALLOW_SHORT_SELLING = False  # Never allow short selling
    ALLOW_DAY_TRADING = False    # Never allow day trading
    
    # Position Management
    MAX_POSITION_VALUE_PERCENT = 1  # 50% max of account per position
    MIN_POSITION_VALUE = 1          # Minimum $20 position
    MAX_POSITIONS_TOTAL = 8            # Maximum 8 total positions
    
    # Risk Management (Personal)
    PERSONAL_STOP_LOSS = 0.08          # 8% stop loss (more conservative)
    PERSONAL_TAKE_PROFIT = 0.15        # 15% take profit target
    MAX_DAILY_RISK_PERCENT = 0.05      # 5% max account risk per day
    
    # Fractional Order Safety Settings
    FRACTIONAL_FUND_BUFFER = 0.9       # Use only 50% of available funds for fractional orders
    MIN_FRACTIONAL_ORDER = 5.0         # Minimum $2 for fractional orders to avoid API issues
    FRACTIONAL_ORDER_TYPE = 'MKT'      # Use limit orders for better fractional execution
    
    # Signal Filtering
    MIN_SIGNAL_CONFIDENCE = 0.6        # 60% minimum confidence for trades
    REQUIRE_VOLUME_CONFIRMATION = True  # Require volume confirmation
    
    # Preferred Strategies
    PREFERRED_STRATEGY_ORDER = [
        'BollingerMeanReversion',  # Primary strategy
        'GapTrading'               # Secondary strategy
    ]
    
    # Stock Universe Preferences
    EXCLUDE_PENNY_STOCKS = False        # No stocks under $5
    MIN_DAILY_VOLUME = 1_000_000      # 1M minimum daily volume
    PREFER_DIVIDEND_STOCKS = True      # Prefer dividend paying stocks
    
    # Watchlist (Personal favorites to always include)
    PERSONAL_WATCHLIST = [
        # Blue chip favorites
        'AAPL', 'MSFT', 'JNJ', 'PG', 'KO',
        # Value plays
        'USB', 'TGT', 'CVS', 'XOM', 'CVX',
        # ETFs
        'SPY', 'QQQ', 'VTV', 'SCHD'
    ]
    
    # Holdings to exclude from analysis (buy and hold)
    BUY_AND_HOLD_POSITIONS = [
        # Add any positions you never want to sell
    ]
    
    # Time Preferences
    TRADING_START_TIME = "09:45"  # Wait 15 min after market open
    TRADING_END_TIME = "15:30"    # Stop 30 min before close
    
    # Notification Preferences
    REQUIRE_CONFIRMATION = True       # Always ask before trading
    SHOW_DETAILED_ANALYSIS = True    # Show full signal details
    
    @classmethod
    def get_personal_scan_universe(cls, account_positions=None, settled_funds=0.0):
        """
        Get personalized stock universe based on account and preferences
        
        Args:
            account_positions: List of current position symbols
            settled_funds: Available settled funds
            
        Returns:
            List of symbols to scan
        """
        from trading_system.config.stock_lists import StockLists
        
        # Start with watchlist
        scan_universe = cls.PERSONAL_WATCHLIST.copy()
        
        # Add current positions (except buy-and-hold)
        if account_positions:
            for symbol in account_positions:
                if symbol not in cls.BUY_AND_HOLD_POSITIONS:
                    scan_universe.append(symbol)
        
        # Add affordable stocks from main universe
        main_universe = list(set(
            StockLists.BOLLINGER_MEAN_REVERSION + 
            StockLists.GAP_TRADING
        ))
        
        # Filter by preferences and affordability
        for symbol in main_universe:
            if symbol in scan_universe:
                continue
                
            # Add stocks we can afford (with some buffer for volatility)
            affordable_threshold = settled_funds * 0.9  # 10% buffer
            
            # You would add price checking logic here
            # For now, just add high-quality stocks
            if symbol in StockLists.DIVIDEND_ARISTOCRATS_VALUE:
                scan_universe.append(symbol)
        
        # Remove duplicates and sort
        scan_universe = list(set(scan_universe))
        scan_universe.sort()
        
        return scan_universe
    
    @classmethod
    def should_execute_signal(cls, signal, current_positions=None, account_value=0.0):
        """
        Check if a signal meets personal criteria for execution
        
        Args:
            signal: Trading signal dictionary
            current_positions: List of current positions
            account_value: Total account value
            
        Returns:
            tuple: (should_execute: bool, reason: str)
        """
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        confidence = signal.get('confidence', 0)
        price = signal.get('price', 0)
        
        # Check minimum confidence
        if confidence < cls.MIN_SIGNAL_CONFIDENCE:
            return False, f"Confidence {confidence:.1%} below minimum {cls.MIN_SIGNAL_CONFIDENCE:.1%}"
        
        # Check if it's a buy-and-hold position
        if symbol in cls.BUY_AND_HOLD_POSITIONS and signal_type == 'SELL':
            return False, f"{symbol} is marked as buy-and-hold"
        
        # Check position size limits for buys
        if signal_type == 'BUY':
            max_position_value = account_value * cls.MAX_POSITION_VALUE_PERCENT
            if price > max_position_value:
                return False, f"Position too large: ${price:.2f} > ${max_position_value:.2f}"
            
            if price < cls.MIN_POSITION_VALUE:
                return False, f"Position too small: ${price:.2f} < ${cls.MIN_POSITION_VALUE:.2f}"
        
        # Check penny stock exclusion
        if cls.EXCLUDE_PENNY_STOCKS and price < 5.0:
            return False, f"Penny stock excluded: ${price:.2f} < $5.00"
        
        # Check if we're at max positions
        if signal_type == 'BUY' and current_positions:
            if len(current_positions) >= cls.MAX_POSITIONS_TOTAL:
                return False, f"At maximum positions: {len(current_positions)}/{cls.MAX_POSITIONS_TOTAL}"
        
        return True, "Signal meets all criteria"
    
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
        Returns either whole shares or buffered dollar amounts for fractional investing
        
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
            return {'type': 'none', 'amount': 0, 'is_fractional': False}
        
        # Calculate whole shares first
        max_whole_shares = int(max_position_value / signal_price)
        
        # If we can afford at least one whole share and it meets minimum value
        if max_whole_shares >= 1:
            whole_share_value = max_whole_shares * signal_price
            if whole_share_value >= cls.MIN_POSITION_VALUE:
                return {
                    'type': 'shares',
                    'amount': float(max_whole_shares),
                    'is_fractional': False
                }
        
        # For fractional shares, apply safety buffer and minimum order size
        # Use only a portion of available funds to avoid Webull API issues
        buffered_amount = max_position_value * cls.FRACTIONAL_FUND_BUFFER
        
        # Check if buffered amount meets minimum fractional order size
        if buffered_amount < cls.MIN_FRACTIONAL_ORDER:
            return {
                'type': 'none', 
                'amount': 0, 
                'is_fractional': False,
                'reason': f'Buffered amount ${buffered_amount:.2f} below minimum ${cls.MIN_FRACTIONAL_ORDER:.2f}'
            }
        
        # Use buffered dollar-amount ordering for fractional shares
        # This provides safety margin and avoids price movement issues
        return {
            'type': 'dollars',
            'amount': round(buffered_amount, 2),  # Round to nearest cent
            'is_fractional': True,
            'buffer_applied': True,
            'original_amount': round(max_position_value, 2),
            'buffer_percentage': cls.FRACTIONAL_FUND_BUFFER
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
        Format signal for display with personal preferences
        
        Args:
            signal: Signal dictionary
            position_data: Current position data if selling
            
        Returns:
            str: Formatted display string
        """
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        price = signal['price']
        confidence = signal.get('confidence', 0)
        
        # Base display
        display = f"{signal_type} {symbol} @ ${price:.2f} ({confidence:.1%})"
        
        # Add position info for sells
        if signal_type == 'SELL' and position_data:
            pnl = position_data.get('unrealized_pnl', 0)
            pnl_pct = position_data.get('pnl_rate', 0) * 100
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"
            display += f" {pnl_emoji} P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)"
        
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


# Example usage and validation
def validate_personal_config():
    """Validate personal configuration settings"""
    config = PersonalTradingConfig()
    
    print("🔧 Personal Trading Configuration")
    print("=" * 40)
    print(f"Short Selling: {'❌ Disabled' if not config.ALLOW_SHORT_SELLING else '✅ Enabled'}")
    print(f"Day Trading: {'❌ Disabled' if not config.ALLOW_DAY_TRADING else '✅ Enabled'}")
    print(f"Max Position: {config.MAX_POSITION_VALUE_PERCENT:.1%} of account")
    print(f"Min Position: ${config.MIN_POSITION_VALUE}")
    print(f"Max Positions: {config.MAX_POSITIONS_TOTAL}")
    print(f"Stop Loss: {config.PERSONAL_STOP_LOSS:.1%}")
    print(f"Take Profit: {config.PERSONAL_TAKE_PROFIT:.1%}")
    print(f"Min Confidence: {config.MIN_SIGNAL_CONFIDENCE:.1%}")
    print(f"Trading Hours: {config.TRADING_START_TIME} - {config.TRADING_END_TIME}")
    print(f"Watchlist: {len(config.PERSONAL_WATCHLIST)} stocks")
    
    # Test signal evaluation
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

if __name__ == "__main__":
    validate_personal_config()
