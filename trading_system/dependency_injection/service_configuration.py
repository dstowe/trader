# dependency_injection/service_configuration.py
def configure_services(container: DIContainer, config_path: str = None):
    """Configure all services for dependency injection"""
    
    # Configuration
    container.register(
        PersonalTradingConfig,
        lambda: PersonalTradingConfig(),
        singleton=True
    )
    
    # Database
    container.register(
        DatabaseConnection,
        lambda config: DatabaseConnection(config.DATABASE_PATH),
        dependencies=[PersonalTradingConfig]
    )
    
    # Repositories
    container.register(
        SignalRepository,
        lambda db: SignalRepository(db),
        dependencies=[DatabaseConnection]
    )
    
    container.register(
        PositionRepository,
        lambda db: PositionRepository(db),
        dependencies=[DatabaseConnection]
    )
    
    # Services
    container.register(
        DataService,
        lambda signal_repo, pos_repo: DataService(signal_repo, pos_repo),
        dependencies=[SignalRepository, PositionRepository]
    )
    
    # Error handling
    container.register(
        ErrorHandler,
        lambda: ErrorHandler(logging.getLogger(__name__)),
        singleton=True
    )
    
    # Strategy factory
    container.register(
        StrategyFactory,
        lambda: StrategyFactory(),
        singleton=True
    )