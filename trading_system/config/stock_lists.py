# config/stock_lists.py
class StockLists:
    """Stock lists optimized for 2025 market conditions with enhanced Bollinger Band mean reversion focus"""
    
    # ========================================================================
    # ENHANCED BOLLINGER BAND MEAN REVERSION UNIVERSE
    # ========================================================================
    
    # Significantly expanded based on optimal volatility research (ATR <1.5%, beta 1.2-1.8, vol 20-40%)
    BOLLINGER_MEAN_REVERSION = [
        # Core ETFs - High liquidity, optimal volatility for BB signals
        'SPY',   # S&P 500 ETF - Ultimate liquidity
        'QQQ',   # Nasdaq ETF - Tech rotation opportunities
        'IWM',   # Russell 2000 ETF - Small cap mean reversion
        'VTV',   # Vanguard Value ETF - Systematic value exposure
        'IWD',   # iShares Russell 1000 Value - Large cap value
        
        # Mega Cap Tech - Mean reversion during sector rotation
        'AAPL',  # Apple - Premium multiple, dividend aristocrat
        'MSFT',  # Microsoft - Defensive tech, AI leader
        'GOOGL', # Google - Undervalued AI/cloud play
        'AMZN',  # Amazon - E-commerce normalization
        'TSLA',  # Tesla - High volatility, EV cycle
        'NVDA',  # Nvidia - AI chip leader, cyclical
        'META',  # Meta - Social media recovery
        
        # Financial Sector - Benefiting from rate environment
        'JPM',   # JPMorgan Chase - Money center leader
        'BAC',   # Bank of America - Consumer banking
        'USB',   # U.S. Bancorp - 4.2% dividend, regional leader
        'TFC',   # Truist Financial - Strategic restructuring
        'PNC',   # PNC Financial - Diversified regional
        'WFC',   # Wells Fargo - Turnaround story
        'BK',    # BNY Mellon - Fee-based wealth management
        'NTRS',  # Northern Trust - Premium wealth services
        'GS',    # Goldman Sachs - Investment banking cycle
        'MS',    # Morgan Stanley - Wealth management focus
        'C',     # Citigroup - International exposure
        
        # Energy Sector - Value rotation leader, optimal BB patterns
        'XOM',   # Exxon Mobil - Integrated oil leader
        'CVX',   # Chevron - 75%+ FCF return to shareholders
        'EOG',   # EOG Resources - 100%+ FCF returns, shale leader
        'COP',   # ConocoPhillips - Variable dividend policy
        'SLB',   # Schlumberger - Oilfield services recovery
        'EPD',   # Enterprise Products Partners - 8.2% yield, 26yr growth
        'KMI',   # Kinder Morgan - Natural gas infrastructure
        'ET',    # Energy Transfer - Fee-based midstream
        'CHRD',  # Chord Energy - 6.8% dividend, E&P value
        
        # Healthcare - Defensive value with mean reversion characteristics
        'JNJ',   # Johnson & Johnson - Healthcare conglomerate
        'UNH',   # UnitedHealth Group - Healthcare services leader
        'DHR',   # Danaher - Medtech/diagnostics, AI catalysts
        'CVS',   # CVS Health - Healthcare transformation
        'PFE',   # Pfizer - Pharmaceutical value play
        'ABBV',  # AbbVie - Biotech dividend aristocrat
        'MRK',   # Merck - Pharmaceutical innovation
        'BMY',   # Bristol Myers Squibb - Oncology focus
        
        # Consumer Staples - Defensive with reliable BB patterns
        'PG',    # Procter & Gamble - 67yr dividend growth
        'KO',    # Coca-Cola - Dividend king, global brands
        'PEP',   # PepsiCo - Diversified consumer staples
        'CPB',   # Campbell Soup - AI integration, $63 fair value
        'CHD',   # Church & Dwight - 28yr dividend growth
        'CL',    # Colgate-Palmolive - Global consumer products
        'KMB',   # Kimberly-Clark - Essential products
        
        # Industrial Cyclicals - Classic BB behavior tied to cycles
        'CAT',   # Caterpillar - Infrastructure spending cycle
        'DE',    # Deere & Company - Agricultural equipment
        'BA',    # Boeing - Aerospace recovery
        'HON',   # Honeywell - Diversified industrials
        'MMM',   # 3M - Industrial conglomerate turnaround
        'GE',    # General Electric - Industrial focus transformation
        'RTX',   # Raytheon - Defense and aerospace
        'LMT',   # Lockheed Martin - Defense contractor
        
        # Materials & Steel - Cyclical mean reversion leaders
        'NUE',   # Nucor - 52yr dividend growth, steel leader
        'STLD',  # Steel Dynamics - Mini-mill efficiency
        'X',     # United States Steel - Traditional steel
        'FCX',   # Freeport-McMoRan - Copper mining cycle
        'NEM',   # Newmont - Gold mining defensive
        
        # Consumer Discretionary - Retail value opportunities
        'TGT',   # Target - 10.3x P/E, 4.8% yield, dividend king
        'HD',    # Home Depot - Home improvement leader
        'LOW',   # Lowe's - Home improvement #2
        'MCD',   # McDonald's - QSR defensive dividend
        'SBUX',  # Starbucks - Premium coffee, China recovery
        'NKE',   # Nike - Athletic apparel cycle
        
        # REITs - 9% below fair value sector-wide
        'O',     # Realty Income - Monthly dividends, 30yr growth
        'PLD',   # Prologis - Industrial REIT, e-commerce
        'CCI',   # Crown Castle - 6.2% yield, wireless infrastructure
        'AMT',   # American Tower - Cell tower infrastructure
        'SPG',   # Simon Property - Premium mall REIT
        'PSA',   # Public Storage - Self-storage leader
        
        # Utilities - Minimal volatility, reliable BB boundaries
        'DUK',   # Duke Energy - 4.1% yield, rate base growth
        'SO',    # Southern Company - Regulated utility
        'D',     # Dominion Energy - Utility transformation
        'EVRG',  # Evergy - Regional utility, strong regulatory
        'ES',    # Eversource Energy - Northeast utility
        'NEE',   # NextEra Energy - Renewable energy leader
        
        # Communication Services - Media/Telecom value
        'VZ',    # Verizon - 6.9% dividend yield telecom
        'T',     # AT&T - Telecom turnaround story
        'CMCSA', # Comcast - Cable/broadband leader
        'DIS',   # Disney - Entertainment recovery
        
        # Technology Value - Former growth at value prices
        'ORCL',  # Oracle - Cloud transition
        'IBM',   # IBM - Hybrid cloud focus
        'INTC',  # Intel - Semiconductor turnaround
        'CRM',   # Salesforce - Cloud software leader
        
        # Sector ETFs - Systematic sector rotation
        'XLF',   # Financial sector - Rate beneficiary
        'XLE',   # Energy sector - Value rotation leader
        'XLV',   # Healthcare sector - Defensive positioning
        'XLI',   # Industrial sector - Infrastructure cycle
        'XLU',   # Utilities sector - Defensive income
        'XLP',   # Consumer staples - Recession defense
        'XLRE',  # Real estate sector - REIT exposure
    ]
    
    # Value-focused subsets for specialized strategies
    DIVIDEND_ARISTOCRATS_VALUE = [
        'PG', 'KO', 'JNJ', 'XOM', 'CVX', 'CAT', 'MCD', 'WMT', 'TGT', 'LOW',
        'HD', 'MMM', 'GE', 'IBM', 'VZ', 'T', 'SO', 'D', 'NEE'
    ]
    
    DEEP_VALUE_OPPORTUNITIES = [
        'CVS', 'TGT', 'INTC', 'F', 'CPB', 'T', 'CHRD', 'X', 'C', 'WFC',
        'IBM', 'BMY', 'BA', 'MMM', 'XOM'
    ]
    
    ENERGY_VALUE_PLAYS = [
        'XOM', 'CVX', 'EOG', 'COP', 'SLB', 'EPD', 'KMI', 'ET', 'CHRD', 'XLE'
    ]
    
    FINANCIAL_ROTATION_LEADERS = [
        'JPM', 'BAC', 'USB', 'TFC', 'PNC', 'WFC', 'BK', 'NTRS', 'GS', 'MS', 'C', 'XLF'
    ]
    
    HEALTHCARE_DEFENSIVE_VALUE = [
        'JNJ', 'UNH', 'DHR', 'CVS', 'PFE', 'ABBV', 'MRK', 'BMY', 'XLV'
    ]
    
    REIT_INCOME_FOCUS = [
        'O', 'PLD', 'CCI', 'AMT', 'SPG', 'PSA', 'XLRE'
    ]
    
    # ========================================================================
    # VOLATILITY-OPTIMIZED LISTS
    # ========================================================================
    
    # Optimal volatility for BB signals (ATR 1.0-1.5%, beta 1.2-1.8)
    OPTIMAL_VOLATILITY_BB = [
        'SPY', 'VTV', 'IWD', 'USB', 'TFC', 'PNC', 'EPD', 'KMI', 'UNH', 'DHR',
        'PG', 'CPB', 'CHD', 'CAT', 'NUE', 'TGT', 'O', 'PLD', 'DUK', 'EVRG'
    ]
    
    # Higher volatility for aggressive BB strategies (ATR 1.5-2.5%)
    HIGHER_VOLATILITY_BB = [
        'QQQ', 'IWM', 'TSLA', 'NVDA', 'META', 'XOM', 'CVX', 'EOG', 'COP',
        'CHRD', 'CVS', 'BA', 'X', 'FCX', 'INTC', 'CRM'
    ]
    
    # Low volatility for conservative strategies (ATR <1.0%)
    LOW_VOLATILITY_BB = [
        'JNJ', 'KO', 'PEP', 'PG', 'CL', 'DUK', 'SO', 'D', 'VZ', 'T'
    ]
    
    # ========================================================================
    # INTERNATIONAL VALUE OPPORTUNITIES
    # ========================================================================
    
    # European value ETFs and ADRs
    INTERNATIONAL_VALUE = [
        'EFA',   # MSCI EAFE - Developed markets
        'VEA',   # Vanguard FTSE Developed Markets
        'IEFA',  # iShares Core MSCI EAFE
        'VGK',   # Vanguard FTSE Europe
        'EWG',   # Germany ETF
        'EWU',   # United Kingdom ETF
        'ASML',  # ASML Holding - Semiconductor equipment
        'NVO',   # Novo Nordisk - Danish pharma
        'UL',    # Unilever - Consumer goods
        'NESN',  # Nestle - Swiss consumer staples
    ]
    
    # ========================================================================
    # INCOME AND COVERED CALL STRATEGIES
    # ========================================================================
    
    # Enhanced covered call candidates with 3%+ dividends
    COVERED_CALL_ENHANCED = [
        # High dividend ETFs
        'SCHD',  # Schwab US Dividend Equity - Quality focus
        'VYM',   # Vanguard High Dividend Yield
        'DVY',   # iShares Select Dividend
        'HDV',   # iShares High Dividend
        'JEPI',  # JPMorgan Equity Premium Income - 7.9% yield
        'JEPQ',  # JPMorgan Nasdaq Equity Premium Income - 9.3% yield
        
        # High dividend value stocks
        'EPD', 'KMI', 'ET', 'O', 'CCI',  # Infrastructure/REITs
        'VZ', 'T', 'XOM', 'CVX',         # Telecom/Energy
        'USB', 'TFC', 'PNC',             # Regional banks
        'DUK', 'SO', 'D', 'EVRG',        # Utilities
        'PG', 'KO', 'PEP', 'JNJ',        # Dividend aristocrats
    ]
    
    # ========================================================================
    # EXISTING STRATEGY LISTS (MAINTAINED FOR COMPATIBILITY)
    # ========================================================================
    
    # Expanded gap trading with new volatility-optimized additions
    GAP_TRADING = [
        # High Volume ETFs
        'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
        'VTV', 'IWD', 'JEPI', 'JEPQ',  # Value/income ETFs
        'ARKK', 'GLD', 'TLT', 'HYG',   # Specialty ETFs
        
        # Mega Cap Tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
        'NFLX', 'ORCL', 'CRM', 'ADBE',
        
        # High Beta Growth/Value
        'AMD', 'SNOW', 'PLTR', 'ROKU', 'ZM', 'PTON', 'ABNB', 'UBER',
        'CVS', 'BA', 'X', 'FCX', 'CHRD',  # Value volatility
        
        # Financial Gaps
        'JPM', 'BAC', 'GS', 'MS', 'C', 'WFC', 'USB', 'TFC',
        
        # Energy Gaps
        'XOM', 'CVX', 'EOG', 'COP', 'SLB', 'EPD', 'KMI',
        
        # Healthcare Gaps
        'JNJ', 'UNH', 'DHR', 'CVS', 'PFE', 'MRNA', 'BNTX',
        
        # Communication/Media
        'DIS', 'CMCSA', 'T', 'VZ', 'NFLX',
    ]
    
    # Momentum stocks updated for 2025 conditions
    MOMENTUM_STOCKS = [
        'AMD', 'NFLX', 'CRM', 'ADBE', 'PYPL',  # Original momentum
        'NVDA', 'META', 'GOOGL', 'AMZN',       # Tech leaders
        'UNH', 'DHR', 'CAT', 'NUE',            # Value momentum
        'EPD', 'KMI', 'O', 'PLD',              # Income momentum
        'SHOP', 'SQ', 'TWLO', 'OKTA', 'DDOG',  # Growth momentum
    ]
    
    # Iron condor candidates (high IV, range-bound potential)
    IRON_CONDOR_CANDIDATES = [
        # High IV ETFs
        'IWM', 'QQQ', 'XLF', 'XLE', 'ARKK',
        
        # High IV individual stocks
        'TSLA', 'AMD', 'NVDA', 'NFLX', 'META',
        'ROKU', 'PTON', 'ZM', 'PLTR', 'SNOW',
        'MRNA', 'BNTX', 'CVS', 'BA', 'X',
    ]
    
    # ========================================================================
    # COMPOSITE AND STRATEGY LISTS
    # ========================================================================
    
    # Core 50 universe - highest quality, most liquid
    CORE_UNIVERSE = [
        # Must-have ETFs
        'SPY', 'QQQ', 'IWM', 'VTV', 'IWD',
        
        # Mega cap tech
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
        
        # Financial leaders
        'JPM', 'BAC', 'USB', 'TFC', 'GS',
        
        # Energy value leaders
        'XOM', 'CVX', 'EOG', 'EPD', 'KMI',
        
        # Healthcare/Consumer defensive
        'JNJ', 'UNH', 'PG', 'KO', 'TGT',
        
        # Industrial/Materials cyclicals
        'CAT', 'NUE', 'DHR',
        
        # REITs/Utilities income
        'O', 'PLD', 'DUK', 'VZ',
        
        # Sector ETFs
        'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
        
        # High beta opportunities
        'CVS', 'BA', 'CHRD', 'CRM'
    ]
    
    # Comprehensive universe for multi-strategy scanning
    ALL_STRATEGIES = list(set(
        BOLLINGER_MEAN_REVERSION + 
        GAP_TRADING + 
        MOMENTUM_STOCKS + 
        COVERED_CALL_ENHANCED +
        IRON_CONDOR_CANDIDATES +
        INTERNATIONAL_VALUE
    ))
    
    # ========================================================================
    # VOLATILITY AND RISK PARAMETERS
    # ========================================================================
    
    # Optimal conditions for BB mean reversion
    VOLATILITY_PARAMETERS = {
        'OPTIMAL_VIX_RANGE': (15, 25),
        'MAX_ATR_PERCENT': 1.5,      # ATR as % of stock price
        'OPTIMAL_BETA_RANGE': (1.2, 1.8),
        'MIN_DAILY_VOLUME': 1_000_000,
        'MIN_MARKET_CAP': 5_000_000_000,  # $5B minimum
        'OPTIMAL_VOLATILITY_RANGE': (20, 40),  # Annualized %
        'MAX_HOLDING_PERIOD_DAYS': 6,
        'VOLUME_CONFIRMATION_MULTIPLIER': 1.5,
    }
    
    # ========================================================================
    # BACKWARD COMPATIBILITY
    # ========================================================================
    
    # Legacy aliases maintained for existing code
    GAP_TRADING_STOCKS = GAP_TRADING
    GAP_TRADING_UNIVERSE = BOLLINGER_MEAN_REVERSION + GAP_TRADING  # Critical for existing code
    
    # ETF lists
    ETFS = ['SPY', 'QQQ', 'IWM', 'VTV', 'IWD', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU', 
            'XLP', 'XLRE', 'JEPI', 'JEPQ', 'SCHD', 'VYM', 'DVY', 'HDV']
    
    # Market cap classifications
    MEGA_CAP = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
    LARGE_CAP = ['JPM', 'BAC', 'XOM', 'CVX', 'JNJ', 'PG', 'UNH', 'DHR', 'CAT', 'NUE']
    MID_CAP = ['ROKU', 'PTON', 'ZM', 'PLTR', 'SNOW', 'CVS', 'CHRD']
    SMALL_CAP = []  # Not defined in new structure
    
    # Original sector classifications (simplified)
    SECTORS = {
        'TECHNOLOGY': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'ORCL', 'AMD', 'CRM'],
        'FINANCIALS': ['JPM', 'BAC', 'GS', 'MS', 'C', 'WFC', 'XLF'],
        'ENERGY': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'XLE'],
        'HEALTHCARE': ['JNJ', 'PFE', 'MRNA', 'BNTX', 'GILD', 'BIIB', 'XLV'],
        'CONSUMER': ['PG', 'KO', 'PEP', 'DIS'],
        'INDUSTRIALS': ['XLI'],
        'COMMUNICATION': ['META', 'GOOGL', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ']
    }
    
    # Market cap classifications (maintained)
    MARKET_CAPS = {
        'MEGA_CAP': MEGA_CAP,
        'LARGE_CAP': LARGE_CAP,
        'MID_CAP': MID_CAP,
        'ETFS': ETFS
    }
    
    # ========================================================================
    # ENHANCED STRATEGY MAPPING
    # ========================================================================
    
    @classmethod
    def get_stocks_for_strategy(cls, strategy_name: str) -> list:
        """Return appropriate stock list for given strategy with 2025 enhancements"""
        
        strategy_mapping = {
            'BollingerMeanReversion': cls.BOLLINGER_MEAN_REVERSION,
            'BollingerOptimalVolatility': cls.OPTIMAL_VOLATILITY_BB,
            'BollingerHighVolatility': cls.HIGHER_VOLATILITY_BB,
            'BollingerLowVolatility': cls.LOW_VOLATILITY_BB,
            'GapTrading': cls.GAP_TRADING,
            'Momentum': cls.MOMENTUM_STOCKS,
            'CoveredCall': cls.COVERED_CALL_ENHANCED,
            'IronCondor': cls.IRON_CONDOR_CANDIDATES,
            'DividendAristocrats': cls.DIVIDEND_ARISTOCRATS_VALUE,
            'DeepValue': cls.DEEP_VALUE_OPPORTUNITIES,
            'EnergyValue': cls.ENERGY_VALUE_PLAYS,
            'FinancialRotation': cls.FINANCIAL_ROTATION_LEADERS,
            'HealthcareDefensive': cls.HEALTHCARE_DEFENSIVE_VALUE,
            'REITIncome': cls.REIT_INCOME_FOCUS,
            'InternationalValue': cls.INTERNATIONAL_VALUE,
            'Core': cls.CORE_UNIVERSE,
            'All': cls.ALL_STRATEGIES
        }
        
        return strategy_mapping.get(strategy_name, cls.CORE_UNIVERSE)
    
    @classmethod
    def get_strategy_info(cls) -> dict:
        """Return comprehensive information about all available strategies"""
        
        return {
            'BollingerMeanReversion': {
                'stocks': len(cls.BOLLINGER_MEAN_REVERSION),
                'description': 'Enhanced value-focused mean reversion with optimal volatility',
                'market_condition': 'VALUE_ROTATION_2025',
                'volatility_target': 'ATR 1.0-2.0%'
            },
            'BollingerOptimalVolatility': {
                'stocks': len(cls.OPTIMAL_VOLATILITY_BB),
                'description': 'Optimal volatility range for BB signals (ATR <1.5%)',
                'market_condition': 'RANGE_BOUND',
                'volatility_target': 'ATR 1.0-1.5%'
            },
            'EnergyValue': {
                'stocks': len(cls.ENERGY_VALUE_PLAYS),
                'description': 'Energy sector value rotation leaders',
                'market_condition': 'SECTOR_ROTATION',
                'volatility_target': 'High volatility, strong fundamentals'
            },
            'FinancialRotation': {
                'stocks': len(cls.FINANCIAL_ROTATION_LEADERS),
                'description': 'Financial sector benefiting from rate environment',
                'market_condition': 'RATE_ENVIRONMENT',
                'volatility_target': 'Medium volatility, rate sensitivity'
            },
            'DividendAristocrats': {
                'stocks': len(cls.DIVIDEND_ARISTOCRATS_VALUE),
                'description': 'Quality dividend growers trading at value',
                'market_condition': 'INCOME_FOCUS',
                'volatility_target': 'Low-medium volatility'
            },
            'REITIncome': {
                'stocks': len(cls.REIT_INCOME_FOCUS),
                'description': 'Real estate value with 9% sector discount',
                'market_condition': 'INCOME_ROTATION',
                'volatility_target': 'Low volatility, rate sensitive'
            }
        }
    
    # ========================================================================
    # ENHANCED SECTOR AND MARKET CAP CLASSIFICATIONS
    # ========================================================================
    
    SECTORS_ENHANCED = {
        'TECHNOLOGY': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 
                      'NFLX', 'ORCL', 'CRM', 'ADBE', 'AMD', 'INTC', 'IBM'],
        'FINANCIALS': ['JPM', 'BAC', 'USB', 'TFC', 'PNC', 'WFC', 'BK', 'NTRS', 
                      'GS', 'MS', 'C', 'XLF'],
        'ENERGY': ['XOM', 'CVX', 'EOG', 'COP', 'SLB', 'EPD', 'KMI', 'ET', 'CHRD', 'XLE'],
        'HEALTHCARE': ['JNJ', 'UNH', 'DHR', 'CVS', 'PFE', 'ABBV', 'MRK', 'BMY', 'XLV'],
        'CONSUMER_STAPLES': ['PG', 'KO', 'PEP', 'CPB', 'CHD', 'CL', 'KMB', 'XLP'],
        'INDUSTRIALS': ['CAT', 'DE', 'BA', 'HON', 'MMM', 'GE', 'RTX', 'LMT', 'XLI'],
        'MATERIALS': ['NUE', 'STLD', 'X', 'FCX', 'NEM'],
        'CONSUMER_DISCRETIONARY': ['TGT', 'HD', 'LOW', 'MCD', 'SBUX', 'NKE'],
        'REAL_ESTATE': ['O', 'PLD', 'CCI', 'AMT', 'SPG', 'PSA', 'XLRE'],
        'UTILITIES': ['DUK', 'SO', 'D', 'EVRG', 'ES', 'NEE', 'XLU'],
        'COMMUNICATION': ['VZ', 'T', 'CMCSA', 'DIS'],
    }
    
    @classmethod
    def get_sector_rotation_opportunities(cls) -> dict:
        """Get current sector rotation opportunities based on 2025 trends"""
        return {
            'LEADING_SECTORS': ['ENERGY', 'FINANCIALS', 'HEALTHCARE'],
            'LAGGING_SECTORS': ['TECHNOLOGY', 'COMMUNICATION'],
            'DEFENSIVE_ROTATION': ['UTILITIES', 'CONSUMER_STAPLES', 'REAL_ESTATE'],
            'CYCLICAL_OPPORTUNITIES': ['INDUSTRIALS', 'MATERIALS', 'CONSUMER_DISCRETIONARY']
        }
    
    # ========================================================================
    # UTILITY METHODS (MAINTAINED FOR BACKWARD COMPATIBILITY)
    # ========================================================================
    
    @classmethod
    def get_sector_stocks(cls, sector: str) -> list:
        """Get all stocks in a specific sector (legacy method)"""
        return cls.SECTORS.get(sector.upper(), [])
    
    @classmethod
    def get_market_cap_stocks(cls, market_cap: str) -> list:
        """Get all stocks in a specific market cap category"""
        return cls.MARKET_CAPS.get(market_cap.upper(), [])
    
    @classmethod
    def is_etf(cls, symbol: str) -> bool:
        """Check if a symbol is an ETF"""
        return symbol in cls.ETFS
    
    @classmethod
    def get_overlap(cls, strategy1: str, strategy2: str) -> list:
        """Find overlapping stocks between two strategies"""
        list1 = cls.get_stocks_for_strategy(strategy1)
        list2 = cls.get_stocks_for_strategy(strategy2)
        return list(set(list1) & set(list2))
    
    # ========================================================================
    # NEW ENHANCED UTILITY METHODS
    # ========================================================================
    
    @classmethod
    def validate_bb_criteria(cls, symbol: str, atr_percent: float, beta: float, 
                           daily_volume: int, market_cap: int) -> bool:
        """Validate if stock meets optimal BB mean reversion criteria"""
        params = cls.VOLATILITY_PARAMETERS
        
        return (
            atr_percent <= params['MAX_ATR_PERCENT'] and
            params['OPTIMAL_BETA_RANGE'][0] <= beta <= params['OPTIMAL_BETA_RANGE'][1] and
            daily_volume >= params['MIN_DAILY_VOLUME'] and
            market_cap >= params['MIN_MARKET_CAP']
        )
    
    @classmethod
    def get_optimal_position_size(cls, atr_percent: float, base_position: float = 0.02) -> float:
        """Calculate optimal position size based on ATR volatility"""
        if atr_percent <= 1.0:
            return base_position * 1.2  # Increase for low volatility
        elif atr_percent <= 1.5:
            return base_position  # Normal sizing
        elif atr_percent <= 2.5:
            return base_position * 0.75  # Reduce for higher volatility
        else:
            return base_position * 0.5  # Significantly reduce for high volatility