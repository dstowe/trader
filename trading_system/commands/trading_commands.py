# commands/trading_commands.py
import time
from datetime import datetime
from base_command import Command
from base_command import CommandResult

class AuthenticateCommand(Command):
    """Command to handle authentication"""
    
    def __init__(self, login_manager, session_manager, wb):
        self.login_manager = login_manager
        self.session_manager = session_manager
        self.wb = wb
    
    def can_execute(self) -> bool:
        return self.login_manager is not None
    
    def execute(self) -> CommandResult:
        start_time = time.time()
        
        try:
            # Try existing session first
            if self.session_manager.auto_manage_session(self.wb):
                if self.login_manager.check_login_status():
                    return CommandResult(
                        success=True,
                        data={'method': 'existing_session'},
                        execution_time=time.time() - start_time
                    )
                else:
                    self.session_manager.clear_session()
            
            # Perform fresh login
            if self.login_manager.login_automatically():
                self.session_manager.save_session(self.wb)
                return CommandResult(
                    success=True,
                    data={'method': 'fresh_login'},
                    execution_time=time.time() - start_time
                )
            else:
                return CommandResult(
                    success=False,
                    error_message="Authentication failed after all retries",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                error_message=f"Authentication error: {str(e)}",
                execution_time=time.time() - start_time
            )

class DiscoverAccountsCommand(Command):
    """Command to discover and setup accounts"""
    
    def __init__(self, account_manager, config):
        self.account_manager = account_manager
        self.config = config
    
    def can_execute(self) -> bool:
        return self.account_manager is not None
    
    def execute(self) -> CommandResult:
        start_time = time.time()
        
        try:
            # Discover accounts
            if not self.account_manager.discover_accounts():
                return CommandResult(
                    success=False,
                    error_message="Failed to discover accounts",
                    execution_time=time.time() - start_time
                )
            
            # Get enabled accounts
            trading_accounts = self.account_manager.get_enabled_accounts()
            
            if not trading_accounts:
                return CommandResult(
                    success=False,
                    error_message="No accounts enabled for trading",
                    execution_time=time.time() - start_time
                )
            
            # Generate summary
            summary = self.account_manager.get_account_summary()
            
            return CommandResult(
                success=True,
                data={
                    'trading_accounts': trading_accounts,
                    'summary': summary
                },
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                error_message=f"Account discovery error: {str(e)}",
                execution_time=time.time() - start_time
            )

class ValidateMarketHoursCommand(Command):
    """Command to validate trading hours"""
    
    def __init__(self, config):
        self.config = config
    
    def can_execute(self) -> bool:
        return True
    
    def execute(self) -> CommandResult:
        start_time = time.time()
        
        try:
            if not self.config.is_market_hours():
                current_time = datetime.now().strftime("%H:%M")
                return CommandResult(
                    success=False,
                    error_message=f"Outside trading hours: {current_time}",
                    data={
                        'current_time': current_time,
                        'trading_window': f"{self.config.TRADING_START_TIME} - {self.config.TRADING_END_TIME}"
                    },
                    execution_time=time.time() - start_time
                )
            
            # Check if it's a weekday
            weekday = datetime.now().weekday()
            if weekday >= 5:  # Weekend
                return CommandResult(
                    success=False,
                    error_message="Market closed (weekend)",
                    execution_time=time.time() - start_time
                )
            
            return CommandResult(
                success=True,
                data={'market_open': True},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                error_message=f"Market hours validation error: {str(e)}",
                execution_time=time.time() - start_time
            )

class ValidateSafetyLimitsCommand(Command):
    """Command to validate safety limits"""
    
    def __init__(self, config, trading_accounts, todays_trades):
        self.config = config
        self.trading_accounts = trading_accounts
        self.todays_trades = todays_trades
    
    def can_execute(self) -> bool:
        return len(self.trading_accounts) > 0
    
    def execute(self) -> CommandResult:
        start_time = time.time()
        
        try:
            safety_issues = []
            
            total_trades_today = len(self.todays_trades)
            total_accounts = len(self.trading_accounts)
            max_total_trades = self.config.MAX_POSITIONS_TOTAL * total_accounts
            
            # Check total daily trade limit
            if total_trades_today >= max_total_trades:
                safety_issues.append(
                    f"Total daily trade limit reached: {total_trades_today}/{max_total_trades}"
                )
            
            # Check each account individually
            for account in self.trading_accounts:
                account_trades = [
                    t for t in self.todays_trades 
                    if t.get('account_id') == account.account_id
                ]
                
                if len(account_trades) >= self.config.MAX_POSITIONS_TOTAL:
                    safety_issues.append(
                        f"{account.account_type}: Daily trade limit reached"
                    )
                
                if account.net_liquidation < self.config.MIN_POSITION_VALUE:
                    safety_issues.append(
                        f"{account.account_type}: Account value too low"
                    )
            
            if safety_issues:
                return CommandResult(
                    success=False,
                    error_message="Safety limit violations detected",
                    data={'violations': safety_issues},
                    execution_time=time.time() - start_time
                )
            
            return CommandResult(
                success=True,
                data={'all_checks_passed': True},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                error_message=f"Safety validation error: {str(e)}",
                execution_time=time.time() - start_time
            )