# refactored_main.py
class RefactoredTradingSystem:
    """Fully refactored trading system with proper architecture"""
    
    def __init__(self, container: DIContainer):
        self.container = container
        self.config = container.get(PersonalTradingConfig)
        self.data_service = container.get(DataService)
        self.error_handler = container.get(ErrorHandler)
        self.strategy_factory = container.get(StrategyFactory)
        
        # Register error callbacks
        self._setup_error_handling()
    
    def _setup_error_handling(self):
        """Setup error handling callbacks"""
        self.error_handler.register_error_callback(
            AuthenticationError,
            self._handle_auth_error
        )
        self.error_handler.register_error_callback(
            TradingRuleViolation,
            self._handle_rule_violation
        )
    
    def _handle_auth_error(self, error: AuthenticationError, context: dict) -> bool:
        """Handle authentication errors"""
        # Could trigger re-authentication, notifications, etc.
        return True
    
    def _handle_rule_violation(self, error: TradingRuleViolation, context: dict) -> bool:
        """Handle trading rule violations"""
        # Could log to compliance system, send alerts, etc.
        return True
    
    @with_error_handling(error_handler=None, reraise=True)  # Would inject error_handler
    def run_daily_analysis(self) -> Dict:
        """Simplified main analysis method"""
        try:
            # Validate preconditions
            self._validate_preconditions()
            
            # Execute trading pipeline
            result = self._execute_trading_pipeline()
            
            return result
            
        except TradingSystemError as e:
            # Specific trading system errors
            self.error_handler.handle_error(e, {'method': 'run_daily_analysis'})
            raise
        except Exception as e:
            # Unexpected errors
            trading_error = TradingSystemError(
                f"Unexpected error in daily analysis: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
            self.error_handler.handle_error(trading_error)
            raise trading_error
    
    def _validate_preconditions(self):
        """Validate system preconditions"""
        if not self.config.is_market_hours():
            raise TradingSystemError(
                "Market is closed",
                error_code="MARKET_CLOSED",
                context={'current_time': datetime.now().strftime("%H:%M")}
            )
    
    def _execute_trading_pipeline(self) -> Dict:
        """Execute the main trading pipeline"""
        # This would use the command pattern from previous example
        # Combined with proper error handling and dependency injection
        pass

# usage
def main():
    """Main entry point with dependency injection"""
    container = DIContainer()
    configure_services(container)
    
    trading_system = RefactoredTradingSystem(container)
    
    try:
        result = trading_system.run_daily_analysis()
        print("Analysis completed successfully")
        return result
    except TradingSystemError as e:
        print(f"Trading system error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    main()