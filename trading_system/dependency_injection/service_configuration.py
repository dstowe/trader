from container import DIContainer
from personal_config import PersonalTradingConfig
from trading_system.repositories.base_repository import DatabaseConnection
from trading_system.repositories.signal_repository import SignalRepository
from trading_system.repositories.position_repository import PositionRepository
from trading_system.services.data_service import DataService
from trading_system.errors.error_handler import ErrorHandler
import logging
from strategies.strategy_factory import StrategyFactory

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