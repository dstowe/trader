# automated_system.py - REFACTORED: Single Source of Truth Integration
"""
Enhanced Automated Multi-Account Personal Trading System - REFACTORED
Now uses PersonalTradingConfig as the ONLY source of configuration truth
All duplicate configuration logic removed - PersonalTradingConfig is authoritative
Simplified and streamlined for better maintainability
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import traceback
from typing import List, Dict

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


try:
    from trading_system import TradingSystem, StockLists
    from trading_system.webull.webull import webull
    from trading_system.database.models import DatabaseManager
    from trading_system.auth import CredentialManager, LoginManager, SessionManager
    from trading_system.accounts import AccountManager, AccountInfo
    from enhanced_day_trading_protection import EnhancedDayTradingProtection
    TRADING_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Trading system imports failed: {e}")
    TRADING_SYSTEM_AVAILABLE = False
    
    # Create minimal fallback
    class TradingSystem:
        def __init__(self, config=None):
            self.config = config
        def run_daily_analysis(self, **kwargs):
            return {'error': 'TradingSystem not available'}

# Import PersonalTradingConfig
from personal_config import PersonalTradingConfig


# SINGLE SOURCE OF TRUTH: PersonalTradingConfig
from personal_config import PersonalTradingConfig

class EnhancedAutomatedTradingSystem:
    """
    Enhanced Automated Multi-Account Trading System - REFACTORED
    Now uses PersonalTradingConfig as the SINGLE SOURCE OF TRUTH for ALL configuration
    No competing configuration logic - everything defers to PersonalTradingConfig
    """
    
    def __init__(self):
        # SINGLE SOURCE OF TRUTH: Use PersonalTradingConfig for ALL configuration
        self.config = PersonalTradingConfig()
        self.wb = webull()
        # FIXED: Pass PersonalTradingConfig to TradingSystem to ensure single source of truth
        self.trading_system = TradingSystem(config=self.config)
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize auth components
        self.credential_manager = CredentialManager(logger=self.logger)
        self.login_manager = LoginManager(self.wb, self.credential_manager, self.logger)
        self.session_manager = SessionManager(logger=self.logger)
        
        # Account management with PersonalTradingConfig integration
        self.account_manager = AccountManager(self.wb, self.config, self.logger)
        self.trading_accounts = []  # Enabled accounts for trading
        
        # Trading state
        self.is_logged_in = False

        # Initialize day trading protection as None (will be set after authentication)
        self.day_trade_protection = None
        
        # Safety checks - ALL values now from PersonalTradingConfig
        self.today = datetime.now().date()
        
        # Trade tracking for day trading detection
        self.todays_trades = []  # Track trades executed today across all accounts
        self.trade_log_file = "enhanced_automated_trades.json"
        self.load_todays_trades()
        
        # Load configuration summaries (using PersonalTradingConfig methods)
        self.rule_summary = self.config.get_rule_enforcement_summary()
        self.logger.debug(f"🛡️ Rule Enforcement Active: {self.rule_summary}")
        
        # Load automated system configuration (AUTHORITATIVE from PersonalTradingConfig)
        self.automated_config = self.config.get_automated_system_summary()
        self.logger.info(f"🤖 Automated System Config: {self.automated_config}")
        
    def load_todays_trades(self):
        """Load today's trades for day trading detection across all accounts"""
        try:
            if os.path.exists(self.trade_log_file):
                with open(self.trade_log_file, 'r') as f:
                    all_trades = json.load(f)
                
                today = datetime.now().date().isoformat()
                self.todays_trades = [
                    trade for trade in all_trades
                    if trade.get('date', '').startswith(today)
                ]
            else:
                self.todays_trades = []
                
        except Exception as e:
            self.logger.warning(f"Could not load today's trades: {e}")
            self.todays_trades = []
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create daily log file
        log_filename = f"enhanced_automated_trading_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        # Configure logging with UTF-8 encoding for the file handler
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Keep only last 30 days of logs
        self.cleanup_old_logs(log_dir, days=30)
    
    def cleanup_old_logs(self, log_dir, days=30):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            for log_file in log_dir.glob("enhanced_automated_trading_*.log"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")
        except Exception as e:
            self.logger.warning(f"Could not clean up old logs: {e}")
    
    def authenticate(self) -> bool:
        """Handle authentication using the new modular system"""
        try:
            self.logger.info("🔐 Step: Authentication")
            
            # Try to load existing session first
            if self.session_manager.auto_manage_session(self.wb):
                self.logger.info("✅ Using existing session")
                # Verify login status and ensure account context is properly initialized
                if self.login_manager.check_login_status():
                    self.is_logged_in = True
                    return True
                else:
                    self.logger.warning("Session loaded but login verification failed")
                    # Clear potentially bad session and try fresh login
                    self.session_manager.clear_session()
            
            # If no valid session or verification failed, perform fresh login
            self.logger.info("Attempting fresh login...")
            if self.login_manager.login_automatically():
                self.logger.info("✅ Fresh login successful")
                self.is_logged_in = True                
                
                # ✅ ADD: Initialize day trading protection after successful login
                self.day_trade_protection = EnhancedDayTradingProtection(
                    self.wb, self.config, self.logger
                )
                self.logger.info("✅ Enhanced day trading protection initialized")
                
                # Save the new session
                self.session_manager.save_session(self.wb)
                return True
            else:
                self.logger.error("❌ CRITICAL: Authentication failed after all retries")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return False
    
    def discover_and_setup_accounts(self) -> bool:
        """Discover and setup accounts for automated trading"""
        try:
            self.logger.info("🔍 Step: Account Discovery and Setup")
            
            # Discover all accounts
            if not self.account_manager.discover_accounts():
                self.logger.error("❌ Failed to discover accounts")
                return False
            
            # Get enabled accounts from PersonalTradingConfig
            self.trading_accounts = self.account_manager.get_enabled_accounts()
            
            if not self.trading_accounts:
                self.logger.error("❌ No accounts enabled for trading in PersonalTradingConfig")
                self.logger.error("   Check ACCOUNT_CONFIGURATIONS in personal_config.py")
                return False
            
            # Log account summary
            summary = self.account_manager.get_account_summary()
            self.logger.info(f"💼 ENHANCED MULTI-ACCOUNT SUMMARY:")
            self.logger.info(f"   Total Accounts: {summary['total_accounts']}")
            self.logger.info(f"   Enabled for Trading: {summary['enabled_accounts']}")
            self.logger.info(f"   Combined Value: ${summary['total_value']:.2f}")
            self.logger.info(f"   Combined Cash: ${summary['total_cash']:.2f}")
            self.logger.info(f"   Total Positions: {summary['total_positions']}")
            
            for account in self.trading_accounts:
                self.logger.info(f"📊 Trading Account: {account.account_type}")
                self.logger.info(f"   Net Liquidation: ${account.net_liquidation:.2f}")
                self.logger.info(f"   Settled Funds: ${account.settled_funds:.2f}")
                self.logger.info(f"   Positions: {len(account.positions)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in account discovery: {e}")
            return False
    
    def check_market_hours(self):
        """Check if we're in trading hours using PersonalTradingConfig"""
        # Use PersonalTradingConfig method (SINGLE SOURCE OF TRUTH)
        if not self.config.is_market_hours():
            current_time = datetime.now().strftime("%H:%M")
            self.logger.info(f"Not running - outside configured trading hours")
            self.logger.info(f"   Current time: {current_time}")
            self.logger.info(f"   Trading window: {self.config.TRADING_START_TIME} - {self.config.TRADING_END_TIME}")
            return False
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        weekday = datetime.now().weekday()
        is_weekday = weekday < 5  # Monday-Friday
        
        if not is_weekday:
            self.logger.info("Not running - market closed (weekend)")
            return False
        
        return True
    
    def check_safety_limits_for_accounts(self):
        """Enhanced safety checks - FIXED to allow individual account trading"""
        safety_issues = []
        eligible_accounts = []  # Track accounts that can trade
        
        total_trades_today = len(self.todays_trades)
        total_accounts = len(self.trading_accounts)
        
        # Use PersonalTradingConfig values (AUTHORITATIVE)
        max_total_trades = self.config.MAX_POSITIONS_TOTAL * total_accounts
        
        # Check total daily trade limit across all accounts
        if total_trades_today >= max_total_trades:
            safety_issues.append(f"Total daily trade limit reached: {total_trades_today}/{max_total_trades} across all accounts")
            return False  # This is a system-wide limit
        
        # Check each account individually using PersonalTradingConfig
        for account in self.trading_accounts:
            account_issues = []
            account_trades_today = len([t for t in self.todays_trades if t.get('account_id') == account.account_id])
            
            # Check per-account trade limit using PersonalTradingConfig (AUTHORITATIVE)
            if account_trades_today >= self.config.MAX_POSITIONS_TOTAL:
                account_issues.append(f"Daily trade limit reached ({account_trades_today}/{self.config.MAX_POSITIONS_TOTAL})")
            
            # Check minimum account value using PersonalTradingConfig (AUTHORITATIVE)
            if account.net_liquidation < self.config.MIN_POSITION_VALUE:
                account_issues.append(f"Account value too low (${account.net_liquidation:.2f} < ${self.config.MIN_POSITION_VALUE})")
            
            # Check settled funds using PersonalTradingConfig (AUTHORITATIVE)
            if account.settled_funds < self.config.MIN_FRACTIONAL_ORDER:
                account_issues.append(f"Insufficient settled funds (${account.settled_funds:.2f} < ${self.config.MIN_FRACTIONAL_ORDER})")
            
            # If account has issues, log them but don't fail entire system
            if account_issues:
                for issue in account_issues:
                    safety_issues.append(f"{account.account_type}: {issue}")
                self.logger.warning(f"⚠️ {account.account_type} excluded from trading: {'; '.join(account_issues)}")
            else:
                eligible_accounts.append(account)
                self.logger.info(f"✅ {account.account_type} eligible for trading: ${account.settled_funds:.2f} available")
        
        # Update trading_accounts to only include eligible accounts
        if eligible_accounts:
            original_count = len(self.trading_accounts)
            self.trading_accounts = eligible_accounts
            
            if len(eligible_accounts) < original_count:
                self.logger.info(f"🎯 Trading with {len(eligible_accounts)}/{original_count} accounts that meet safety requirements")
            
            # Log safety check results for eligible accounts
            total_available = sum(min(
                account.net_liquidation * self.config.MAX_POSITION_VALUE_PERCENT,
                account.settled_funds
            ) for account in self.trading_accounts)
            
            self.logger.info("✅ Enhanced safety checks passed for eligible accounts")
            self.logger.info(f"   💰 Combined available for trading: ${total_available:.2f}")
            self.logger.info(f"   📊 Eligible accounts: {len(eligible_accounts)}")
            
            return True
        else:
            # All accounts failed safety checks
            self.logger.warning("⚠️ No accounts meet safety requirements:")
            for issue in safety_issues:
                self.logger.warning(f"   • {issue}")
            return False
    
    def get_combined_scan_universe(self) -> List[str]:
        """Get combined scan universe using PersonalTradingConfig method (SINGLE SOURCE OF TRUTH)"""
        all_position_symbols = set()
        total_settled_funds = 0.0
        
        for account in self.trading_accounts:
            position_symbols = [pos['symbol'] for pos in account.positions]
            all_position_symbols.update(position_symbols)
            total_settled_funds += account.settled_funds
        
        # Use PersonalTradingConfig method (AUTHORITATIVE)
        vix_level = 20  # Could be enhanced to get real VIX data
        scan_universe = self.config.get_personal_scan_universe(
            account_positions=list(all_position_symbols),
            settled_funds=total_settled_funds,
            vix_level=vix_level
        )
        
        return scan_universe
    
    def filter_signals_for_account(self, signals: List[Dict], account: AccountInfo) -> List[Dict]:
        """Filter signals for specific account using ENHANCED PersonalTradingConfig rule enforcement"""
        filtered_signals = []
        position_symbols = [pos['symbol'] for pos in account.positions]
        account_trades = [t for t in self.todays_trades if t.get('account_id') == account.account_id]
        
        # Check per-account trade limit using PersonalTradingConfig (AUTHORITATIVE)
        if len(account_trades) >= self.config.MAX_POSITIONS_TOTAL:
            self.logger.debug(f"🚫 {account.account_type}: Daily trade limit reached ({len(account_trades)}/{self.config.MAX_POSITIONS_TOTAL})")
            return []
        
        for signal in signals:
            symbol = signal.symbol
            signal_type = signal.signal_type
            
            # ✅ ENHANCED: Use live Webull day trading protection instead of basic check
            if self.day_trade_protection:
                should_execute, reason = self.day_trade_protection.enhanced_should_execute_signal(
                    signal,
                    current_positions=position_symbols,
                    account_value=account.net_liquidation,
                    account_id=account.account_id
                )
            else:
                # Fallback to original method if day trading protection not initialized
                should_execute, reason = self.config.should_execute_signal(
                    signal,
                    current_positions=position_symbols,
                    account_value=account.net_liquidation,
                    recent_trades=account_trades
                )
            
            if not should_execute:
                self.logger.debug(f"⚠️ {account.account_type}: Filtered {symbol} - {reason}")
                continue
            
            # Check buy-and-hold protection from PersonalTradingConfig (AUTHORITATIVE)
            if symbol in self.config.BUY_AND_HOLD_POSITIONS and signal_type == 'SELL':
                self.logger.debug(f"🚨 {account.account_type}: BUY-AND-HOLD PROTECTION for {symbol}")
                continue
            
            # Position sizing for BUY signals using CENTRALIZED method
            if signal_type == 'BUY':
                strategy_name = signal.strategy
                signal_metadata = signal.metadata
                
                position_info = self.config.get_position_size_with_strategy_adjustments(
                    signal.price,
                    account.net_liquidation,
                    account.settled_funds,
                    strategy_name=strategy_name,
                    signal_metadata=signal_metadata
                )
                
                if position_info['type'] == 'none':
                    self.logger.debug(f"⚠️ {account.account_type}: Insufficient funds for {symbol} - {position_info.get('reason', 'Unknown')}")
                    continue
                
                signal.calculated_position_info = position_info
                signal.target_account = account.account_id
            
            filtered_signals.append(signal)
        
        return filtered_signals
    
    def execute_trade_automatically_on_account(self, account: AccountInfo, signal) -> bool:
        """Execute trade automatically with comprehensive fractional share support"""
        max_attempts = 3
        base_delay = 10
        
        symbol = signal.symbol
        signal_type = signal.signal_type
        price = signal.price
        
        self.logger.info(f"💰 EXECUTING: {signal_type} {symbol} @ ${price:.2f} on {account.account_type}")
        
        # SESSION CHECK: Verify session before trading
        try:
            test_account = self.wb.get_account_id()
            if not test_account:
                raise Exception("Session test failed")
        except Exception as e:
            self.logger.warning(f"🔄 Session appears expired ({e}), refreshing...")
            if hasattr(self, 'login_manager') and self.login_manager.login_automatically():
                self.logger.info("✅ Session refreshed successfully")
                if hasattr(self, 'session_manager'):
                    self.session_manager.save_session(self.wb)
            else:
                self.logger.error("❌ Failed to refresh session")
                return False
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Switch to account
                if not self.account_manager.switch_to_account(account):
                    self.logger.error(f"❌ Failed to switch to {account.account_type}")
                    return False
                
                # Calculate position sizing
                if signal_type == 'BUY':
                    if hasattr(signal, 'calculated_position_info'):
                        position_info = signal.calculated_position_info
                    else:
                        strategy_name = signal.strategy
                        signal_metadata = signal.metadata
                        position_info = self.config.get_position_size_with_strategy_adjustments(
                            price, account.net_liquidation, account.settled_funds,
                            strategy_name=strategy_name, signal_metadata=signal_metadata
                        )
                    
                    if position_info['type'] == 'none':
                        self.logger.warning(f"Skipping {symbol} - {position_info.get('reason', 'Position sizing failed')}")
                        return False
                    
                    # ENHANCED FRACTIONAL HANDLING
                    if position_info['type'] == 'dollars':
                        dollar_amount = position_info['amount']
                        fractional_shares = dollar_amount / price
                        
                        # Check if fractional shares are supported for this stock
                        if not self._supports_fractional_shares(symbol):
                            self.logger.warning(f"⚠️ {symbol} doesn't support fractional shares, converting to whole shares")
                            # Convert to whole shares
                            whole_shares = int(fractional_shares)
                            if whole_shares >= 1:
                                quantity = float(whole_shares)
                                order_mode = 'whole_shares'
                                self.logger.info(f"Using whole shares: {whole_shares} shares of {symbol}")
                            else:
                                self.logger.warning(f"❌ Cannot afford even 1 whole share of {symbol} (${price:.2f})")
                                return False
                        else:
                            # Use fractional shares
                            if fractional_shares >= 1.0:
                                self.logger.warning(f"❌ Fractional shares >= 1.0: {fractional_shares:.6f}")
                                return False
                            
                            # Round to 5 decimal places (common for fractional shares)
                            quantity = round(fractional_shares, 5)
                            order_mode = 'fractional_shares'
                            self.logger.info(f"Using fractional order: {quantity:.5f} shares (${dollar_amount:.2f} worth) of {symbol}")
                            
                            # Validate minimum fractional amount
                            if quantity < 0.00001:
                                self.logger.warning(f"❌ Fractional quantity too small: {quantity:.6f}")
                                return False
                        
                        if 'strategy_adjustment' in position_info:
                            adj = position_info['strategy_adjustment']
                            self.logger.info(f"Applied {adj['reason']}: {adj['factor']:.2f}x")
                            
                    else:
                        # Whole share order
                        quantity = position_info['amount']
                        order_mode = 'whole_shares'
                        
                elif signal_type == 'SELL':
                    # Find position to sell
                    position = None
                    for pos in account.positions:
                        if pos['symbol'] == symbol:
                            position = pos
                            break
                    
                    if not position:
                        self.logger.warning(f"No position found for {symbol} - skipping sell")
                        return False
                    
                    quantity = position['quantity']
                    order_mode = 'fractional_shares' if quantity != int(quantity) else 'whole_shares'
                
                # Execute order with appropriate parameters
                order_type = self.config.FRACTIONAL_ORDER_TYPE
                
                # ENHANCED ORDER PLACEMENT
                if order_mode == 'fractional_shares' and signal_type == 'BUY':
                    self.logger.info(f"Placing {signal_type} fractional order: {quantity:.5f} shares of {symbol} ({order_type})")
                    
                    # For fractional shares, try different approaches
                    order_result = self._place_fractional_order(
                        symbol=symbol,
                        price=price,
                        action=signal_type,
                        quantity=quantity,
                        order_type=order_type
                    )
                else:
                    self.logger.info(f"Placing {signal_type} whole share order: {quantity} shares of {symbol} ({order_type})")
                    
                    order_result = self.wb.place_order(
                        stock=symbol,
                        price=price,
                        action=signal_type,
                        orderType=order_type,
                        enforce='DAY',
                        quant=int(quantity) if order_mode == 'whole_shares' else quantity,
                        outsideRegularTradingHour=False
                    )
                
                # Check order result
                success, order_id, error_message = self._parse_order_result(order_result)
                
                if success:
                    self.logger.info(f"✅ Order executed successfully on {account.account_type} (attempt {attempt})")
                    self.logger.info(f"   Order ID: {order_id}")
                    self.logger.info(f"   Symbol: {symbol}")
                    self.logger.info(f"   Action: {signal_type}")
                    self.logger.info(f"   Quantity: {quantity}")
                    self.logger.info(f"   Price: ${price:.2f}")
                    self.logger.info(f"   Mode: {order_mode}")
                    
                    self.log_trade_execution(signal, quantity, order_result, account)
                    return True
                else:
                    # Handle specific fractional share errors
                    if self._is_fractional_share_error(error_message):
                        self.logger.warning(f"🔄 Fractional share error, trying whole shares instead")
                        # Retry with whole shares if possible
                        if order_mode == 'fractional_shares' and signal_type == 'BUY':
                            whole_shares = int(quantity * price / position_info['amount'])
                            if whole_shares >= 1:
                                self.logger.info(f"Converting to {whole_shares} whole shares")
                                order_result = self.wb.place_order(
                                    stock=symbol,
                                    price=price,
                                    action=signal_type,
                                    orderType=order_type,
                                    enforce='DAY',
                                    quant=whole_shares,
                                    outsideRegularTradingHour=False
                                )
                                success, order_id, error_message = self._parse_order_result(order_result)
                                if success:
                                    self.logger.info(f"✅ Whole share order successful: {whole_shares} shares")
                                    self.log_trade_execution(signal, whole_shares, order_result, account)
                                    return True
                    
                    # Check if retryable
                    if not self._is_retryable_trade_error(order_result, error_message):
                        self.logger.error(f"❌ Non-retryable error: {error_message}")
                        return False
                    
                    self.logger.warning(f"❌ Trade attempt {attempt} failed: {error_message}")
                    
            except Exception as e:
                self.logger.warning(f"❌ Trade execution exception (attempt {attempt}): {e}")
                if not self._is_retryable_exception(e):
                    return False
            
            # Wait before retry
            if attempt < max_attempts:
                delay = base_delay * attempt
                self.logger.info(f"⏳ Waiting {delay} seconds before retry...")
                import time
                time.sleep(delay)
        
        self.logger.error(f"❌ Failed to execute trade after {max_attempts} attempts")
        return False

    def _supports_fractional_shares(self, symbol: str) -> bool:
        """Check if stock supports fractional shares"""
        # Stocks that typically DON'T support fractional shares
        no_fractional_stocks = {
            'BRK-A',  # Berkshire Hathaway (too expensive/special rules)
            # Add others as discovered
        }
        
        # For now, assume most stocks support fractional shares except known exceptions
        if symbol in no_fractional_stocks:
            return False
        
        # Could also check price - very expensive stocks often don't support fractional
        # if price > 1000:  # Example threshold
        #     return False
        
        return True

    def _place_fractional_order(self, symbol: str, price: float, action: str, 
                            quantity: float, order_type: str):
        """Place fractional order with multiple fallback approaches"""
        
        # Method 1: Standard fractional order
        try:
            self.logger.debug(f"🔍 Trying standard fractional order: {quantity:.5f} shares")
            return self.wb.place_order(
                stock=symbol,
                price=price,
                action=action,
                orderType=order_type,
                enforce='DAY',
                quant=quantity,
                outsideRegularTradingHour=False
            )
        except Exception as e:
            self.logger.debug(f"Standard fractional order failed: {e}")
        
        # Method 2: Round to different precision
        try:
            rounded_qty = round(quantity, 4)  # Try 4 decimal places
            self.logger.debug(f"🔍 Trying rounded fractional order: {rounded_qty:.4f} shares")
            return self.wb.place_order(
                stock=symbol,
                price=price,
                action=action,
                orderType=order_type,
                enforce='DAY',
                quant=rounded_qty,
                outsideRegularTradingHour=False
            )
        except Exception as e:
            self.logger.debug(f"Rounded fractional order failed: {e}")
        
        # Method 3: If available, try dollar-based order (some brokers prefer this)
        try:
            dollar_amount = quantity * price
            self.logger.debug(f"🔍 Note: Fractional order attempts failed, will fall back to whole shares")
            # Return a failure indicator so we can try whole shares
            return {'success': False, 'msg': 'Fractional order methods exhausted'}
        except Exception as e:
            return {'success': False, 'msg': f'All fractional methods failed: {e}'}

    def _is_fractional_share_error(self, error_message: str) -> bool:
        """Check if error is related to fractional share issues"""
        if not error_message:
            return False
        
        fractional_errors = [
            'minimum fractional number',
            'fractional shares not supported',
            'fractional trading not available',
            'does not support fractional',
            'fractional order failed'
        ]
        
        error_lower = error_message.lower()
        return any(err in error_lower for err in fractional_errors)

    def _parse_order_result(self, order_result):
        """Parse order result and return success, order_id, error_message"""
        if order_result is None:
            return False, None, "No order result received"
        
        if isinstance(order_result, dict):
            if order_result.get('success') == True:
                return True, order_result.get('orderId', 'Unknown'), None
            elif 'data' in order_result and 'orderId' in order_result['data']:
                return True, order_result['data']['orderId'], None
            elif 'orderId' in order_result:
                return True, order_result['orderId'], None
            else:
                error_msg = order_result.get('msg', f'Order failed: {order_result}')
                return False, None, error_msg
        
        return False, None, f"Unexpected order result format: {order_result}"
    
    def _is_retryable_trade_error(self, order_result, error_message):
        """Determine if a trade error is retryable"""
        if not error_message:
            error_message = str(order_result)
        
        error_msg_lower = error_message.lower()
        
        # Non-retryable trade errors
        non_retryable_messages = [
            'insufficient funds',
            'insufficient buying power',
            'account restricted',
            'stock not tradable',
            'invalid symbol',
            'market closed',
            'order rejected',
            'position not found',
            'invalid price',
            'invalid quantity'
        ]
        
        for msg in non_retryable_messages:
            if msg in error_msg_lower:
                return False
        
        # Default to retryable for unknown errors
        return True
    
    def _is_retryable_exception(self, exception):
        """Determine if an exception is retryable"""
        import requests
        
        # Network-related exceptions are retryable
        retryable_exceptions = [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            ConnectionError,
            TimeoutError,
            OSError  # Can include network issues
        ]
        
        for exc_type in retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default to retryable for unknown exceptions
        return True
    
    def log_trade_execution(self, signal, quantity: float, order_result: Dict, account: AccountInfo): # Changed signal type hint to reflect object
        """Log automated trade execution for enhanced multi-account system"""
        try:
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().date().isoformat(),
                'account_id': account.account_id,
                'account_type': account.account_type,
                'symbol': signal.symbol, # Access using dot notation
                'action': signal.signal_type, # Access using dot notation
                'quantity': quantity,
                'price': signal.price, # Access using dot notation
                'automated': True,
                'enhanced_system': True,
                'order_id': order_result.get('orderId', 'N/A'),
                'strategy': signal.strategy, # Access using dot notation
                'rule_enforcement': True,
                'fractional_enabled': True
            }
            
            self.todays_trades.append(trade_record)
            
            # Save to file
            all_trades = []
            if os.path.exists(self.trade_log_file):
                with open(self.trade_log_file, 'r') as f:
                    all_trades = json.load(f)
            
            all_trades.append(trade_record)
            
            # Keep only last 30 days of trades
            cutoff_date = (datetime.now() - timedelta(days=30)).date().isoformat()
            all_trades = [t for t in all_trades if t.get('date', '') >= cutoff_date]
            
            with open(self.trade_log_file, 'w') as f:
                json.dump(all_trades, f, indent=2)
                
            self.logger.info(f"📝 Enhanced trade logged: {signal.signal_type} {signal.symbol} on {account.account_type}") # Access using dot notation
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error logging enhanced trade: {e}")
    
    def sync_all_positions_to_db(self):
        """Sync positions from all accounts to database"""
        try:
            sync_date = datetime.now().strftime('%Y-%m-%d')
            total_positions_synced = 0
            
            with self.db as conn:
                # ✅ Table creation is now handled centrally in DatabaseManager.init_database()
                # ❌ REMOVED: No need to create table here anymore
                
                for account in self.trading_accounts:
                    for pos in account.positions:
                        is_fractional = self.config.is_fractional_position(pos['quantity'])
                        is_buy_and_hold = pos['symbol'] in self.config.BUY_AND_HOLD_POSITIONS
                        
                        conn.execute('''
                            INSERT OR REPLACE INTO enhanced_position_history
                            (sync_date, account_id, account_type, symbol, quantity, cost_price, current_price,
                            market_value, unrealized_pnl, pnl_rate, last_open_time,
                            account_value, settled_funds, is_fractional, is_buy_and_hold, enhanced_system)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            sync_date, account.account_id, account.account_type, pos['symbol'], pos['quantity'],
                            pos['cost_price'], pos['current_price'], pos['market_value'], pos['unrealized_pnl'],
                            pos['pnl_rate'], pos['last_open_time'], account.net_liquidation,
                            account.settled_funds, 1 if is_fractional else 0, 1 if is_buy_and_hold else 0, 1
                        ))
                        total_positions_synced += 1
            
            self.logger.info(f"Synced {total_positions_synced} positions from {len(self.trading_accounts)} accounts to enhanced database")
            
        except Exception as e:
            self.logger.error(f"Error syncing enhanced positions: {e}")
    
    def run_enhanced_automated_analysis(self):
        """Enhanced automated analysis with PersonalTradingConfig as SINGLE SOURCE OF TRUTH"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🛡️ ENHANCED AUTOMATED MULTI-ACCOUNT TRADING SYSTEM - REFACTORED")
            self.logger.info("=" * 80)
            
            # Log that we're using PersonalTradingConfig as single source of truth
            self.logger.info(f"🔧 Configuration: Using {type(self.config).__name__} as SINGLE SOURCE OF TRUTH")
            
            # Log automated system configuration (from PersonalTradingConfig - AUTHORITATIVE)
            self.logger.info(f"🤖 Strategy Mode: {self.automated_config['mode']}")
            if self.automated_config['strategy_override']:
                self.logger.info(f"🎯 Forced Strategy: {self.automated_config['strategy_override']}")
            if self.automated_config['stock_list_override']:
                self.logger.info(f"📊 Forced Stock List: {self.automated_config['stock_list_override']}")
            self.logger.info(f"🚫 Ignore Market Conditions: {self.automated_config['ignore_market_conditions']}")
            self.logger.info(f"🔄 Enable Retry: {self.automated_config['enable_retry']}")
            self.logger.info(f"🛡️ Fallback Strategy: {self.automated_config['fallback_strategy']}")
            
            # Log all configuration from PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            config_summary = self.config.get_all_config_summary()
            self.logger.info(f"📋 Enhanced Rules: Short Selling {self.config.ALLOW_SHORT_SELLING} | Day Trading {self.config.ALLOW_DAY_TRADING}")
            self.logger.info(f"📅 Analysis Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"⏰ Trading Hours: {self.config.TRADING_START_TIME} - {self.config.TRADING_END_TIME}")
            self.logger.info(f"🎯 Min Confidence: {self.config.MIN_SIGNAL_CONFIDENCE:.1%}")
            self.logger.info(f"💰 Min Position: ${self.config.MIN_POSITION_VALUE}")
            self.logger.info(f"📊 Max Positions: {self.config.MAX_POSITIONS_TOTAL}")
            
            # Pre-flight safety checks using PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            if not self.check_market_hours():
                self.logger.info("✅ Enhanced system ran successfully - market not open")
                return True  # Not an error condition
            
            # Step 1: Authenticate with new modular system
            if not self.authenticate():
                return False
            
            # ✅ ADD: Day Trading Summary (after authentication)
            if self.day_trade_protection:
                try:
                    dt_summary = self.day_trade_protection.get_day_trading_summary()
                    self.logger.info("📊 LIVE DAY TRADING SUMMARY:")
                    self.logger.info(f"   Total trades today: {dt_summary['total_trades']}")
                    self.logger.info(f"   Symbols traded: {dt_summary['symbols_traded']}")
                    self.logger.info(f"   Buy trades: {dt_summary['buy_count']}")
                    self.logger.info(f"   Sell trades: {dt_summary['sell_count']}")
                    self.logger.info(f"   Potential day trades: {dt_summary['potential_day_trades']}")
                    
                    if dt_summary['symbols_with_day_trade_risk']:
                        self.logger.warning(f"   ⚠️ Day trade risk symbols: {', '.join(dt_summary['symbols_with_day_trade_risk'])}")
                    
                    if dt_summary['total_trades'] > 0:
                        self.logger.info("   🔍 Enhanced day trading protection is ACTIVE")
                    
                except Exception as e:
                    self.logger.warning(f"Could not generate day trading summary: {e}")            
            
            # Step 2: Discover and setup accounts
            self.logger.info("💼 Step 2: Enhanced account discovery and setup...")
            if not self.discover_and_setup_accounts():
                self.logger.error("❌ CRITICAL: Failed to setup trading accounts")
                return False
            
            # Step 3: Enhanced safety checks using PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            self.logger.info("🛡️ Step 3: Running enhanced safety checks...")
            if not self.check_safety_limits_for_accounts():
                self.logger.warning("⚠️ Enhanced safety limits not met - system will not trade today")
                self.logger.info("✅ Enhanced system ran successfully - safety limits prevented trading")
                return True  # Not an error condition
            
            # Log enhanced combined status using PersonalTradingConfig methods
            total_value = sum(account.net_liquidation for account in self.trading_accounts)
            total_funds = sum(account.settled_funds for account in self.trading_accounts)
            total_positions = sum(len(account.positions) for account in self.trading_accounts)
            
            # Get fractional capability info from PersonalTradingConfig (AUTHORITATIVE)
            fractional_info = self.config.get_fractional_capability_info(total_value, total_funds)
            
            self.logger.info("📊 Enhanced Combined Account Status:")
            self.logger.info(f"   💰 Total Account Value: ${total_value:.2f}")
            self.logger.info(f"   💵 Total Settled Funds: ${total_funds:.2f}")
            self.logger.info(f"   📋 Total Positions: {total_positions}")
            self.logger.info(f"   🏦 Trading Accounts: {len(self.trading_accounts)}")
            self.logger.info(f"   🛡️ Today's Trades: {len(self.todays_trades)} executed across all accounts")
            self.logger.info(f"   📊 Fractional Enabled: {fractional_info['fractional_enabled']}")
            self.logger.info(f"   💸 Min Order Amount: ${fractional_info['min_order_amount']}")
            
            # Step 4: Build scan universe using PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            self.logger.info("🔍 Step 4: Building enhanced scan universe...")
            scan_universe = self.get_combined_scan_universe()
            self.logger.info(f"   📈 Scanning {len(scan_universe)} stocks using PersonalTradingConfig preferences")
            
            if len(scan_universe) == 0:
                self.logger.warning("⚠️ No stocks in enhanced scan universe - nothing to analyze")
                return True
            
            # Step 5: Run trading system analysis with strategy override from PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            self.logger.info("🤖 Step 5: Running enhanced market analysis...")
            
            # Get strategy and stock list overrides from PersonalTradingConfig (AUTHORITATIVE)
            strategy_override, stock_list_override = self.config.get_automated_strategy_override()
            
            if strategy_override:
                self.logger.info(f"🎯 Strategy Override Active: {strategy_override}")
            if stock_list_override:
                self.logger.info(f"📊 Stock List Override Active: {stock_list_override}")
            
            analysis_attempts = self.automated_config['max_attempts'] if self.automated_config['enable_retry'] else 1
            results = None
            
            for attempt in range(1, analysis_attempts + 1):
                try:
                    self.logger.info(f"   Analysis attempt {attempt}/{analysis_attempts}")
                    
                    # Override stock lists temporarily
                    original_bb_list = StockLists.BOLLINGER_MEAN_REVERSION
                    original_gap_list = StockLists.GAP_TRADING
                    
                    try:
                        StockLists.BOLLINGER_MEAN_REVERSION = scan_universe
                        StockLists.GAP_TRADING = scan_universe
                        
                        # Pass strategy and stock list overrides to run_daily_analysis
                        results = self.trading_system.run_daily_analysis(
                            strategy_override=strategy_override,
                            stock_list_override=stock_list_override
                        )
                        
                    finally:
                        StockLists.BOLLINGER_MEAN_REVERSION = original_bb_list
                        StockLists.GAP_TRADING = original_gap_list
                    
                    self.logger.info("✅ Enhanced market analysis completed successfully")
                    break
                except Exception as e:
                    self.logger.warning(f"❌ Analysis attempt {attempt} failed: {e}")
                    if attempt < analysis_attempts:
                        import time
                        time.sleep(30)  # Wait 30 seconds before retry
                        
                        # Try fallback strategy if enabled and not on last attempt
                        if self.automated_config['enable_retry'] and attempt == 1:
                            self.logger.info(f"🔄 Trying fallback strategy: {self.automated_config['fallback_strategy']}")
                            strategy_override = self.automated_config['fallback_strategy']
                    else:
                        self.logger.error("❌ CRITICAL: Enhanced market analysis failed after all retries")
                        return False
            
            # Step 6: Process and distribute signals with PersonalTradingConfig rule enforcement (SINGLE SOURCE OF TRUTH)
            self.logger.info("📋 Step 6: Processing signals with enhanced rule enforcement...")
            # Assuming results['buy_signals'] and results['sell_signals'] contain TradingSignal objects
            all_signals = results['buy_signals'] + results['sell_signals']
            
            self.logger.info(f"   📊 Strategy Used: {results['strategy_used']}")
            self.logger.info(f"   📈 Market Condition: {results.get('market_condition', {}).get('condition', 'Unknown')}")
            self.logger.info(f"   🎯 Raw Signals: {len(all_signals)}")
            
            if not all_signals:
                self.logger.info("📭 No trading signals generated today")
                # Still sync positions and complete successfully
                self.sync_all_positions_to_db()
                return True
            
            # Enhanced signal processing with PersonalTradingConfig (SINGLE SOURCE OF TRUTH)
            executed_trades = 0
            total_rule_violations = 0
            confidence_filtered = 0
            buy_and_hold_protected = 0
            
            for i, signal in enumerate(all_signals, 1):
                # Access attributes using dot notation
                self.logger.debug(f"\n📊 Signal {i}/{len(all_signals)}: {signal.signal_type} {signal.symbol} @ ${signal.price:.2f}")
                self.logger.debug(f"   Confidence: {signal.confidence:.1%}")
                
                # Check minimum confidence using PersonalTradingConfig (AUTHORITATIVE)
                if signal.confidence < self.config.MIN_SIGNAL_CONFIDENCE:
                    self.logger.debug(f"   ❌ Below minimum confidence threshold ({self.config.MIN_SIGNAL_CONFIDENCE:.1%})")
                    confidence_filtered += 1
                    continue
                
                # Check buy-and-hold protection using PersonalTradingConfig (AUTHORITATIVE)
                if (signal.symbol in self.config.BUY_AND_HOLD_POSITIONS and
                    signal.signal_type == 'SELL'):
                    self.logger.debug(f"   🛡️ BUY-AND-HOLD PROTECTION: {signal.symbol}")
                    buy_and_hold_protected += 1
                    continue
                
                # Find suitable accounts for this signal with enhanced filtering
                suitable_accounts = []
                for account in self.trading_accounts:
                    filtered_signals = self.filter_signals_for_account([signal], account)
                    if filtered_signals:
                        # If filter_signals_for_account returns a non-empty list, it means the signal
                        # was suitable for this account and potentially modified (e.g., added calculated_position_info)
                        # We should use the modified signal from filtered_signals for execution
                        suitable_accounts.append((account, filtered_signals[0])) # Store account and modified signal
                    else:
                        total_rule_violations += 1
                
                if not suitable_accounts:
                    self.logger.debug("🚨 No accounts can execute this signal due to enhanced rule violations")
                    continue
                
                # Automatically select best account using enhanced logic
                if len(suitable_accounts) > 1:
                    # Select based on settled funds, using the (account, signal) tuple
                    best_account_tuple = max(suitable_accounts, key=lambda x: x[0].settled_funds)
                    best_account = best_account_tuple[0]
                    signal_to_execute = best_account_tuple[1]
                    self.logger.info(f"   🎯 Auto-selected: {best_account.account_type} (${best_account.settled_funds:.2f} available)")
                else:
                    best_account = suitable_accounts[0][0]
                    signal_to_execute = suitable_accounts[0][1]
                    self.logger.info(f"   🎯 Using: {best_account.account_type}")
                
                # Execute trade on selected account with enhanced logging
                if self.execute_trade_automatically_on_account(best_account, signal_to_execute): # Pass the modified signal
                    executed_trades += 1
                    self.logger.info(f"   ✅ Enhanced trade {executed_trades} executed successfully on {best_account.account_type}")
                    
                    # Refresh account info after successful trade
                    if not self.account_manager.refresh_account_details(best_account):
                        self.logger.warning("   ⚠️ Could not refresh account info after trade")
                    
                    # Small delay between trades to avoid rate limiting
                    if i < len(all_signals):
                        import time
                        time.sleep(5)
                else:
                    self.logger.warning(f"   ❌ Enhanced trade failed for {signal.symbol}") # Access using dot notation
            
            # Step 7: Final summary and cleanup
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Sync all positions to enhanced database
            self.sync_all_positions_to_db()
            
            self.logger.info("="*80)
            self.logger.info("✅ ENHANCED AUTOMATED MULTI-ACCOUNT ANALYSIS COMPLETE - REFACTORED")
            self.logger.info("="*80)
            self.logger.info(f"📊 Enhanced Execution Summary:")
            self.logger.info(f"   ⏱️ Duration: {duration.total_seconds():.1f} seconds")
            self.logger.info(f"   🤖 Strategy Mode: {self.automated_config['mode']}")
            if strategy_override:
                self.logger.info(f"   🎯 Strategy Used: {strategy_override} (overridden)")
            else:
                self.logger.info(f"   🎯 Strategy Used: {results['strategy_used']} (auto-selected)")
            self.logger.info(f"   🏦 Trading Accounts: {len(self.trading_accounts)}")
            self.logger.info(f"   📈 Signals Analyzed: {len(all_signals)}")
            self.logger.info(f"   💰 Trades Executed: {executed_trades}")
            self.logger.info(f"   🚨 Rule Violations Blocked: {total_rule_violations}")
            self.logger.info(f"   🎯 Confidence Filtered: {confidence_filtered}")
            self.logger.info(f"   🛡️ Buy-and-Hold Protected: {buy_and_hold_protected}")
            self.logger.info(f"   📊 Daily Trade Count: {len(self.todays_trades)} across all accounts")
            
            # Final enhanced account status using PersonalTradingConfig methods
            self.logger.info(f"📊 Final Enhanced Multi-Account Status:")
            for account in self.trading_accounts:
                account_trades = len([t for t in self.todays_trades if t.get('account_id') == account.account_id])
                allocation_info = account.get_allocation_info(self.config)
                
                self.logger.info(f"   🏦 {account.account_type}:")
                self.logger.info(f"      💰 Account Value: ${account.net_liquidation:.2f}")
                self.logger.info(f"      💵 Settled Funds: ${account.settled_funds:.2f}")
                self.logger.info(f"      📋 Positions: {len(account.positions)}/{allocation_info['max_positions']}")
                self.logger.info(f"      📊 Today's Trades: {account_trades}")
                self.logger.info(f"      💸 Cash %: {allocation_info['cash_percentage']:.1f}%")
            
            if executed_trades > 0:
                self.logger.info("📱 Check your Webull app for order confirmations")
            
            self.logger.info("="*80)
            
           
            # ✅ ADD: Final day trading protection summary
            if executed_trades > 0 and self.day_trade_protection:
                try:
                    # Refresh the summary after trades
                    final_summary = self.day_trade_protection.get_day_trading_summary()
                    self.logger.info("📊 FINAL DAY TRADING STATUS:")
                    self.logger.info(f"   Total trades after execution: {final_summary['total_trades']}")
                    self.logger.info(f"   New potential day trades: {final_summary['potential_day_trades']}")
                    
                    if final_summary['symbols_with_day_trade_risk']:
                        self.logger.warning(f"   ⚠️ Symbols now requiring day trade protection: {', '.join(final_summary['symbols_with_day_trade_risk'])}")
                
                except Exception as e:
                    self.logger.warning(f"Could not generate final day trading summary: {e}")
            
            return True

        except Exception as e:
            self.logger.error(f"❌ CRITICAL ENHANCED SYSTEM ERROR: {e}")
            self.logger.error("📋 Full error details:", exc_info=True)
            return False
        

def setup_credentials():
    """One-time setup to encrypt and store credentials using new modular system"""
    from trading_system.auth.credentials import setup_credentials_interactive
    return setup_credentials_interactive()

def main():
    """Main entry point for enhanced automated system - REFACTORED with PersonalTradingConfig as SINGLE SOURCE OF TRUTH"""
    try:
        system = EnhancedAutomatedTradingSystem()
        success = system.run_enhanced_automated_analysis()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logging.error(f"Critical enhanced system error: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    # Check if this is a setup run
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_credentials()
    else:
        main()