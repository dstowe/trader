# automated_system.py (Refactored)
"""
Enhanced Automated Multi-Account Personal Trading System
Fully integrated with PersonalTradingConfig for consistent rule enforcement
Runs daily at configured trading hours via Windows Task Scheduler
No user interaction required - respects all personal trading preferences

Refactored version with modular authentication and account management
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

from trading_system import TradingSystem, StockLists
from trading_system.webull.webull import webull
from trading_system.database.models import DatabaseManager
from trading_system.auth import CredentialManager, LoginManager, SessionManager
from trading_system.accounts import AccountManager, AccountInfo
from personal_config import PersonalTradingConfig

class EnhancedAutomatedTradingSystem:
    """
    Enhanced Automated Multi-Account Trading System
    Fully integrated with PersonalTradingConfig for complete consistency
    Now with modular authentication and account management
    """
    
    def __init__(self):
        # Use PersonalTradingConfig as the single source of truth
        self.config = PersonalTradingConfig()
        self.wb = webull()
        self.trading_system = TradingSystem()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize auth components
        self.credential_manager = CredentialManager(logger=self.logger)
        self.login_manager = LoginManager(self.wb, self.credential_manager, self.logger)
        self.session_manager = SessionManager(logger=self.logger)
        
        # Account management with config integration
        self.account_manager = AccountManager(self.wb, self.config, self.logger)
        self.trading_accounts = []  # Enabled accounts for trading
        
        # Trading state
        self.is_logged_in = False
        
        # Safety checks - now using PersonalTradingConfig values
        self.today = datetime.now().date()
        
        # Trade tracking for day trading detection
        self.todays_trades = []  # Track trades executed today across all accounts
        self.trade_log_file = "enhanced_automated_trades.json"
        self.load_todays_trades()
        
        # Load rule enforcement summary
        self.rule_summary = self.config.get_rule_enforcement_summary()
        self.logger.info(f"🛡️ Rule Enforcement Active: {self.rule_summary}")
        
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
        # Use PersonalTradingConfig trading hours instead of hardcoded values
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
        """Enhanced safety checks using PersonalTradingConfig limits"""
        safety_issues = []
        
        total_trades_today = len(self.todays_trades)
        total_accounts = len(self.trading_accounts)
        
        # Use PersonalTradingConfig max positions instead of hardcoded values
        max_total_trades = self.config.MAX_POSITIONS_TOTAL * total_accounts
        
        # Check total daily trade limit across all accounts
        if total_trades_today >= max_total_trades:
            safety_issues.append(f"Total daily trade limit reached: {total_trades_today}/{max_total_trades} across all accounts")
        
        # Check each account individually
        for account in self.trading_accounts:
            account_trades_today = len([t for t in self.todays_trades if t.get('account_id') == account.account_id])
            
            # Check per-account trade limit using PersonalTradingConfig
            if account_trades_today >= self.config.MAX_POSITIONS_TOTAL:
                safety_issues.append(f"{account.account_type}: Daily trade limit reached ({account_trades_today}/{self.config.MAX_POSITIONS_TOTAL})")
            
            # Check minimum account value using PersonalTradingConfig
            if account.net_liquidation < self.config.MIN_POSITION_VALUE:
                safety_issues.append(f"{account.account_type}: Account value too low (${account.net_liquidation:.2f} < ${self.config.MIN_POSITION_VALUE})")
            
            # Check settled funds using PersonalTradingConfig
            if account.settled_funds < self.config.MIN_FRACTIONAL_ORDER:
                safety_issues.append(f"{account.account_type}: Insufficient settled funds (${account.settled_funds:.2f} < ${self.config.MIN_FRACTIONAL_ORDER})")
        
        # Calculate combined available funds using PersonalTradingConfig method
        total_available = sum(min(
            account.net_liquidation * self.config.MAX_POSITION_VALUE_PERCENT,
            account.settled_funds
        ) for account in self.trading_accounts)
        
        if total_available < self.config.MIN_POSITION_VALUE:
            safety_issues.append(f"Insufficient combined funds for minimum position: ${total_available:.2f} < ${self.config.MIN_POSITION_VALUE}")
        
        # Log safety check results
        if safety_issues:
            self.logger.warning("⚠️ Safety limit violations detected:")
            for issue in safety_issues:
                self.logger.warning(f"   • {issue}")
            return False
        else:
            self.logger.info("✅ All enhanced safety checks passed")
            self.logger.info(f"   💰 Combined available for trading: ${total_available:.2f}")
            self.logger.info(f"   📊 Trades remaining today: {max_total_trades - total_trades_today}")
            return True
    
    def get_combined_scan_universe(self) -> List[str]:
        """Get combined scan universe using PersonalTradingConfig method"""
        all_position_symbols = set()
        total_settled_funds = 0.0
        
        for account in self.trading_accounts:
            position_symbols = [pos['symbol'] for pos in account.positions]
            all_position_symbols.update(position_symbols)
            total_settled_funds += account.settled_funds
        
        # Use PersonalTradingConfig method with combined data and current VIX estimate
        vix_level = 20  # Could be enhanced to get real VIX data
        scan_universe = self.config.get_personal_scan_universe(
            account_positions=list(all_position_symbols),
            settled_funds=total_settled_funds,
            vix_level=vix_level
        )
        
        return scan_universe
    
    def filter_signals_for_account(self, signals: List[Dict], account: AccountInfo) -> List[Dict]:
        """Filter signals for specific account using PersonalTradingConfig rule enforcement"""
        filtered_signals = []
        position_symbols = [pos['symbol'] for pos in account.positions]
        account_trades = [t for t in self.todays_trades if t.get('account_id') == account.account_id]
        
        # Check per-account trade limit using PersonalTradingConfig
        if len(account_trades) >= self.config.MAX_POSITIONS_TOTAL:
            self.logger.info(f"🚫 {account.account_type}: Daily trade limit reached ({len(account_trades)}/{self.config.MAX_POSITIONS_TOTAL})")
            return []
        
        for signal in signals:
            symbol = signal['symbol']
            signal_type = signal['signal_type']
            
            # Use PersonalTradingConfig comprehensive signal validation
            should_execute, reason = self.config.should_execute_signal(
                signal, 
                current_positions=position_symbols,
                account_value=account.net_liquidation,
                recent_trades=account_trades
            )
            
            if not should_execute:
                self.logger.info(f"⚠️ {account.account_type}: Filtered {symbol} - {reason}")
                continue
            
            # Check buy-and-hold protection from PersonalTradingConfig
            if symbol in self.config.BUY_AND_HOLD_POSITIONS and signal_type == 'SELL':
                self.logger.info(f"🚨 {account.account_type}: BUY-AND-HOLD PROTECTION for {symbol}")
                continue
            
            # Position sizing for BUY signals using PersonalTradingConfig method
            if signal_type == 'BUY':
                position_info = self.config.get_position_size(
                    signal['price'], 
                    account.net_liquidation, 
                    account.settled_funds
                )
                
                if position_info['type'] == 'none':
                    self.logger.info(f"⚠️ {account.account_type}: Insufficient funds for {symbol}")
                    continue
                
                signal['calculated_position_info'] = position_info
                signal['target_account'] = account.account_id
            
            filtered_signals.append(signal)
        
        return filtered_signals
    
    def execute_trade_automatically_on_account(self, account: AccountInfo, signal: Dict) -> bool:
        """Execute trade automatically on specific account with enhanced retry logic"""
        max_attempts = 3
        base_delay = 10
        
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        price = signal['price']
        
        self.logger.info(f"💰 EXECUTING: {signal_type} {symbol} @ ${price:.2f} on {account.account_type}")
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Switch to this account
                if not self.account_manager.switch_to_account(account):
                    self.logger.error(f"❌ Failed to switch to {account.account_type}")
                    return False
                
                # Calculate position sizing using PersonalTradingConfig
                if signal_type == 'BUY':
                    if 'calculated_position_info' in signal:
                        position_info = signal['calculated_position_info']
                    else:
                        position_info = self.config.get_position_size(
                            price, account.net_liquidation, account.settled_funds
                        )
                    
                    if position_info['type'] == 'none':
                        self.logger.warning(f"Skipping {symbol} on {account.account_type} - {position_info.get('reason', 'Position sizing failed')}")
                        return False
                    
                    if position_info['type'] == 'dollars':
                        # Fractional share order
                        quantity = position_info['amount']  # Dollar amount for fractional
                        self.logger.info(f"Using fractional order: ${quantity} worth of {symbol}")
                    else:
                        # Whole share order
                        quantity = position_info['amount']
                    
                elif signal_type == 'SELL':
                    # Find position to sell
                    position = None
                    for pos in account.positions:
                        if pos['symbol'] == symbol:
                            position = pos
                            break
                    
                    if not position:
                        self.logger.warning(f"No position found for {symbol} on {account.account_type} - skipping sell")
                        return False
                    
                    quantity = position['quantity']
                
                # Execute the order using PersonalTradingConfig order type
                order_type = getattr(self.config, 'FRACTIONAL_ORDER_TYPE', 'LMT')
                self.logger.info(f"Placing {signal_type} order: {quantity} shares of {symbol} on {account.account_type} ({order_type})")
                
                order_result = self.wb.place_order(
                    stock=symbol,
                    price=price,
                    action=signal_type,
                    orderType=order_type,
                    enforce='DAY',
                    quant=quantity,
                    outsideRegularTradingHour=False
                )
                
                # Check order result
                if order_result is None:
                    raise Exception("No order result received")
                
                # Parse different response formats
                success = False
                order_id = None
                error_message = None
                
                if isinstance(order_result, dict):
                    # Check for success indicators
                    if order_result.get('success') == True:
                        success = True
                        order_id = order_result.get('orderId', 'Unknown')
                    elif 'data' in order_result and 'orderId' in order_result['data']:
                        success = True
                        order_id = order_result['data']['orderId']
                    elif 'orderId' in order_result:
                        success = True
                        order_id = order_result['orderId']
                    else:
                        error_message = order_result.get('msg', f'Order failed: {order_result}')
                
                if success:
                    self.logger.info(f"✅ Order executed successfully on {account.account_type} (attempt {attempt})")
                    self.logger.info(f"   Order ID: {order_id}")
                    self.logger.info(f"   Symbol: {symbol}")
                    self.logger.info(f"   Action: {signal_type}")
                    self.logger.info(f"   Quantity: {quantity}")
                    self.logger.info(f"   Price: ${price:.2f}")
                    self.logger.info(f"   Order Type: {order_type}")
                    
                    # Log trade details
                    self.log_trade_execution(signal, quantity, order_result, account)
                    return True
                else:
                    # Order failed - check if retryable
                    if not self._is_retryable_trade_error(order_result, error_message):
                        self.logger.error(f"❌ Non-retryable trade error on {account.account_type}: {error_message}")
                        return False
                    
                    self.logger.warning(f"❌ Trade attempt {attempt} failed on {account.account_type}: {error_message}")
                    
            except Exception as e:
                self.logger.warning(f"❌ Trade execution attempt {attempt} exception on {account.account_type}: {e}")
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    self.logger.error(f"❌ Non-retryable trade exception on {account.account_type}: {e}")
                    return False
            
            # Wait before retry (except on last attempt)
            if attempt < max_attempts:
                delay = base_delay * attempt  # 10, 20 seconds
                self.logger.info(f"⏳ Waiting {delay} seconds before trade retry...")
                import time
                time.sleep(delay)
        
        self.logger.error(f"❌ Failed to execute trade on {account.account_type} after {max_attempts} attempts")
        return False
    
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
    
    def log_trade_execution(self, signal: Dict, quantity: float, order_result: Dict, account: AccountInfo):
        """Log automated trade execution for enhanced multi-account system"""
        try:
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().date().isoformat(),
                'account_id': account.account_id,
                'account_type': account.account_type,
                'symbol': signal['symbol'],
                'action': signal['signal_type'],
                'quantity': quantity,
                'price': signal['price'],
                'automated': True,
                'enhanced_system': True,
                'order_id': order_result.get('orderId', 'N/A'),
                'strategy': signal.get('strategy', 'Unknown'),
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
                
            self.logger.info(f"📝 Enhanced trade logged: {signal['signal_type']} {signal['symbol']} on {account.account_type}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error logging enhanced trade: {e}")
    
    def sync_all_positions_to_db(self):
        """Sync positions from all accounts to database"""
        try:
            sync_date = datetime.now().strftime('%Y-%m-%d')
            total_positions_synced = 0
            
            with self.db as conn:
                # Create enhanced table if not exists
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS enhanced_position_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sync_date TEXT NOT NULL,
                        account_id TEXT NOT NULL,
                        account_type TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        quantity REAL NOT NULL,
                        cost_price REAL NOT NULL,
                        current_price REAL NOT NULL,
                        market_value REAL NOT NULL,
                        unrealized_pnl REAL NOT NULL,
                        pnl_rate REAL NOT NULL,
                        last_open_time TEXT,
                        account_value REAL,
                        settled_funds REAL,
                        is_fractional INTEGER DEFAULT 0,
                        is_buy_and_hold INTEGER DEFAULT 0,
                        enhanced_system INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sync_date, account_id, symbol)
                    )
                ''')
                
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
        """Enhanced automated analysis with full PersonalTradingConfig integration"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🛡️ ENHANCED AUTOMATED MULTI-ACCOUNT TRADING SYSTEM")
            self.logger.info("=" * 80)
            self.logger.info(f"📋 Enhanced Rules: Short Selling {self.config.ALLOW_SHORT_SELLING} | Day Trading {self.config.ALLOW_DAY_TRADING}")
            self.logger.info(f"📅 Analysis Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"⏰ Trading Hours: {self.config.TRADING_START_TIME} - {self.config.TRADING_END_TIME}")
            self.logger.info(f"🎯 Min Confidence: {self.config.MIN_SIGNAL_CONFIDENCE:.1%}")
            self.logger.info(f"💰 Min Position: ${self.config.MIN_POSITION_VALUE}")
            self.logger.info(f"📊 Max Positions: {self.config.MAX_POSITIONS_TOTAL}")
            
            # Pre-flight safety checks using PersonalTradingConfig
            if not self.check_market_hours():
                self.logger.info("✅ Enhanced system ran successfully - market not open")
                return True  # Not an error condition
            
            # Step 1: Authenticate with new modular system
            if not self.authenticate():
                return False
            
            # Step 2: Discover and setup accounts
            self.logger.info("💼 Step 2: Enhanced account discovery and setup...")
            if not self.discover_and_setup_accounts():
                self.logger.error("❌ CRITICAL: Failed to setup trading accounts")
                return False
            
            # Step 3: Enhanced safety checks using PersonalTradingConfig
            self.logger.info("🛡️ Step 3: Running enhanced safety checks...")
            if not self.check_safety_limits_for_accounts():
                self.logger.warning("⚠️ Enhanced safety limits not met - system will not trade today")
                self.logger.info("✅ Enhanced system ran successfully - safety limits prevented trading")
                return True  # Not an error condition
            
            # Log enhanced combined status
            total_value = sum(account.net_liquidation for account in self.trading_accounts)
            total_funds = sum(account.settled_funds for account in self.trading_accounts)
            total_positions = sum(len(account.positions) for account in self.trading_accounts)
            
            # Get fractional capability info
            fractional_info = self.config.get_fractional_capability_info(total_value, total_funds)
            
            self.logger.info("📊 Enhanced Combined Account Status:")
            self.logger.info(f"   💰 Total Account Value: ${total_value:.2f}")
            self.logger.info(f"   💵 Total Settled Funds: ${total_funds:.2f}")
            self.logger.info(f"   📋 Total Positions: {total_positions}")
            self.logger.info(f"   🏦 Trading Accounts: {len(self.trading_accounts)}")
            self.logger.info(f"   🛡️ Today's Trades: {len(self.todays_trades)} executed across all accounts")
            self.logger.info(f"   📊 Fractional Enabled: {fractional_info['fractional_enabled']}")
            self.logger.info(f"   💸 Min Order Amount: ${fractional_info['min_order_amount']}")
            
            # Step 4: Build scan universe using PersonalTradingConfig
            self.logger.info("🔍 Step 4: Building enhanced scan universe...")
            scan_universe = self.get_combined_scan_universe()
            self.logger.info(f"   📈 Scanning {len(scan_universe)} stocks using PersonalTradingConfig preferences")
            
            if len(scan_universe) == 0:
                self.logger.warning("⚠️ No stocks in enhanced scan universe - nothing to analyze")
                return True
            
            # Step 5: Run trading system analysis with retry
            self.logger.info("🤖 Step 5: Running enhanced market analysis...")
            analysis_attempts = 2
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
                        
                        results = self.trading_system.run_daily_analysis()
                        
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
                    else:
                        self.logger.error("❌ CRITICAL: Enhanced market analysis failed after all retries")
                        return False
            
            # Step 6: Process and distribute signals with PersonalTradingConfig rule enforcement
            self.logger.info("📋 Step 6: Processing signals with enhanced rule enforcement...")
            all_signals = results['buy_signals'] + results['sell_signals']
            
            self.logger.info(f"   📊 Strategy Used: {results['strategy_used']}")
            self.logger.info(f"   📈 Market Condition: {results.get('market_condition', {}).get('condition', 'Unknown')}")
            self.logger.info(f"   🎯 Raw Signals: {len(all_signals)}")
            
            if not all_signals:
                self.logger.info("📭 No trading signals generated today")
                # Still sync positions and complete successfully
                self.sync_all_positions_to_db()
                return True
            
            # Enhanced signal processing with PersonalTradingConfig
            executed_trades = 0
            total_rule_violations = 0
            confidence_filtered = 0
            buy_and_hold_protected = 0
            
            for i, signal in enumerate(all_signals, 1):
                self.logger.info(f"\n📊 Signal {i}/{len(all_signals)}: {signal['signal_type']} {signal['symbol']} @ ${signal['price']:.2f}")
                self.logger.info(f"   Confidence: {signal.get('confidence', 0):.1%}")
                
                # Check minimum confidence using PersonalTradingConfig
                if signal.get('confidence', 0) < self.config.MIN_SIGNAL_CONFIDENCE:
                    self.logger.info(f"   ❌ Below minimum confidence threshold ({self.config.MIN_SIGNAL_CONFIDENCE:.1%})")
                    confidence_filtered += 1
                    continue
                
                # Check buy-and-hold protection
                if (signal['symbol'] in self.config.BUY_AND_HOLD_POSITIONS and 
                    signal['signal_type'] == 'SELL'):
                    self.logger.info(f"   🛡️ BUY-AND-HOLD PROTECTION: {signal['symbol']}")
                    buy_and_hold_protected += 1
                    continue
                
                # Find suitable accounts for this signal with enhanced filtering
                suitable_accounts = []
                for account in self.trading_accounts:
                    filtered_signals = self.filter_signals_for_account([signal], account)
                    if filtered_signals:
                        suitable_accounts.append(account)
                    else:
                        total_rule_violations += 1
                
                if not suitable_accounts:
                    self.logger.warning("🚨 No accounts can execute this signal due to enhanced rule violations")
                    continue
                
                # Automatically select best account using PersonalTradingConfig logic
                if len(suitable_accounts) > 1:
                    best_account = max(suitable_accounts, key=lambda a: a.settled_funds)
                    self.logger.info(f"   🎯 Auto-selected: {best_account.account_type} (${best_account.settled_funds:.2f} available)")
                else:
                    best_account = suitable_accounts[0]
                    self.logger.info(f"   🎯 Using: {best_account.account_type}")
                
                # Execute trade on selected account with enhanced logging
                if self.execute_trade_automatically_on_account(best_account, signal):
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
                    self.logger.warning(f"   ❌ Enhanced trade failed for {signal['symbol']}")
            
            # Step 7: Final summary and cleanup
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Sync all positions to enhanced database
            self.sync_all_positions_to_db()
            
            self.logger.info("="*80)
            self.logger.info("✅ ENHANCED AUTOMATED MULTI-ACCOUNT ANALYSIS COMPLETE")
            self.logger.info("="*80)
            self.logger.info(f"📊 Enhanced Execution Summary:")
            self.logger.info(f"   ⏱️ Duration: {duration.total_seconds():.1f} seconds")
            self.logger.info(f"   🏦 Trading Accounts: {len(self.trading_accounts)}")
            self.logger.info(f"   📈 Signals Analyzed: {len(all_signals)}")
            self.logger.info(f"   💰 Trades Executed: {executed_trades}")
            self.logger.info(f"   🚨 Rule Violations Blocked: {total_rule_violations}")
            self.logger.info(f"   🎯 Confidence Filtered: {confidence_filtered}")
            self.logger.info(f"   🛡️ Buy-and-Hold Protected: {buy_and_hold_protected}")
            self.logger.info(f"   📊 Daily Trade Count: {len(self.todays_trades)} across all accounts")
            
            # Final enhanced account status
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
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ CRITICAL ENHANCED SYSTEM ERROR: {e}")
            self.logger.error("📋 Full error details:", exc_info=True)
            return False
        
        finally:
            # Always try to logout for security
            self.login_manager.logout()

def setup_credentials():
    """One-time setup to encrypt and store credentials using new modular system"""
    from trading_system.auth.credentials import setup_credentials_interactive
    return setup_credentials_interactive()

def main():
    """Main entry point for enhanced automated system with modular components"""
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