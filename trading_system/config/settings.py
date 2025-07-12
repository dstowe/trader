# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    # Database
    DATABASE_PATH = "trading_data.db"
        
    # Trading parameters
    ACCOUNT_SIZE = float(os.getenv('ACCOUNT_SIZE', 10000))
    MAX_POSITION_SIZE = 0.10  # 10% of account per position
    STOP_LOSS_PERCENT = 0.05  # 5% stop loss
    
    # Bollinger Band parameters
    BB_PERIOD = 20
    BB_STD_DEV = 2
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    # Data refresh intervals
    DATA_REFRESH_MINUTES = 15
    
    # Risk management
    MAX_DAILY_LOSS = 0.03  # 3% max daily loss
    MAX_POSITIONS = 5
    
    # Gap Trading Parameters
    GAP_MIN_SIZE = 0.01          # 1% minimum gap to consider
    GAP_LARGE_SIZE = 0.03        # 3% large gap threshold
    GAP_EXTREME_SIZE = 0.05      # 5% extreme gap threshold
    GAP_VOLUME_MULTIPLIER = 1.5  # Volume vs average required
    GAP_TIMEOUT_MINUTES = 60     # Max time in gap trade (minutes)
    GAP_MAX_RISK = 0.03          # 3% max risk per gap trade
    GAP_STOP_MULTIPLIER = 1.5    # Stop loss multiplier for gap trades
    
    # Gap Environment Detection
    GAP_ENVIRONMENT_THRESHOLD = 0.30  # 30% of stocks must gap for "high gap day"
    EARNINGS_SEASON_VIX_THRESHOLD = 22  # VIX level indicating earnings volatility
    
    # Strategy Selection
    STRATEGY_MODE = 'AUTO'  # Options: 'AUTO', 'FORCE_BB', 'FORCE_GAP', 'TEST_GAP'
