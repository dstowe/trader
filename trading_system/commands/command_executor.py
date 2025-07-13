# commands/command_executor.py
class CommandExecutor:
    """Executes commands in sequence with proper error handling"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.execution_history = []
    
    def execute_command(self, command: Command) -> CommandResult:
        """Execute a single command with logging"""
        command_name = command.get_description()
        
        if self.logger:
            self.logger.info(f"Executing command: {command_name}")
        
        if not command.can_execute():
            result = CommandResult(
                success=False,
                error_message=f"Command {command_name} cannot be executed"
            )
        else:
            result = command.execute()
        
        # Log result
        if self.logger:
            if result.success:
                self.logger.info(f"✅ {command_name} completed successfully")
            else:
                self.logger.error(f"❌ {command_name} failed: {result.error_message}")
        
        # Store in history
        self.execution_history.append({
            'command': command_name,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def execute_sequence(self, commands: list[Command], stop_on_failure: bool = True) -> Dict:
        """Execute a sequence of commands"""
        results = []
        
        for command in commands:
            result = self.execute_command(command)
            results.append(result)
            
            if not result.success and stop_on_failure:
                break
        
        success_count = sum(1 for r in results if r.success)
        
        return {
            'total_commands': len(commands),
            'successful_commands': success_count,
            'all_successful': success_count == len(commands),
            'results': results
        }

# usage in refactored automated_system.py
class RefactoredAutomatedTradingSystem:
    """Refactored system using command pattern"""
    
    def __init__(self):
        self.config = PersonalTradingConfig()  # This would be the refactored config
        self.command_executor = CommandExecutor(self.logger)
        # ... other initializations
    
    def run_enhanced_automated_analysis(self):
        """Simplified main method using commands"""
        
        # Create command sequence
        commands = [
            ValidateMarketHoursCommand(self.config),
            AuthenticateCommand(self.login_manager, self.session_manager, self.wb),
            DiscoverAccountsCommand(self.account_manager, self.config),
            # ... more commands
        ]
        
        # Execute command sequence
        execution_result = self.command_executor.execute_sequence(commands)
        
        if not execution_result['all_successful']:
            self.logger.error("Command sequence failed")
            return False
        
        # Continue with trading logic...
        return True