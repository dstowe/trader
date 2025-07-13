# config/stock_lists.py
class StockLists:
    """Stock lists optimized for 2025 market conditions with enhanced strategies"""
    
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
    
    # ========================================================================
    # PERSONAL TRADING CONFIG STOCK LISTS (MOVED FROM personal_config.py)
    # ========================================================================
    
    # International ETFs (for International Strategy)
    INTERNATIONAL_ETFS = [
        # Broad International
        'VEA', 'EFA', 'VXUS', 'IEFA',
        # Currency Hedged
        'HEFA', 'HEDJ',
        # Regional
        'VGK', 'EWJ', 'EEMA', 'VWO',
        # Specific Countries
        'EWG', 'EWU', 'EWY', 'INDA'
    ]
    
    # Sector ETFs (for Sector Rotation Strategy)
    SECTOR_ETFS = [
        'XLK',   # Technology
        'XLF',   # Financials
        'XLE',   # Energy
        'XLV',   # Healthcare
        'XLI',   # Industrials
        'XLP',   # Consumer Staples
        'XLU',   # Utilities
        'XLY',   # Consumer Discretionary
        'XLB',   # Materials
        'XLRE',  # Real Estate
        'XLC'    # Communication Services
    ]
    
    # REIT Universe (for Value-Rate Strategy)
    REIT_UNIVERSE = [
        # Industrial/Logistics REITs
        'PLD', 'EXR',
        # Healthcare REITs
        'WELL', 'VTR',
        # Retail REITs
        'FRT', 'REG', 'SPG',
        # Infrastructure REITs
        'CCI', 'AMT', 'EQIX', 'DLR',
        # Office REITs
        'BXP', 'VNO',
        # Residential REITs
        'EQR', 'AVB', 'MAA',
        # REIT ETFs
        'XLRE', 'IYR', 'SCHH'
    ]
    
    # Financial Universe (for Value-Rate Strategy)
    FINANCIAL_UNIVERSE = [
        # Large Banks
        'JPM', 'BAC', 'WFC', 'C',
        # Regional Banks
        'USB', 'TFC', 'PNC',
        # Investment Banks
        'GS', 'MS',
        # Insurance
        'BRK-B', 'AIG',
        # Financial ETFs
        'XLF', 'KBE'
    ]
    
    # Policy-Sensitive Stocks (for Policy Momentum Strategy)
    POLICY_SENSITIVE_STOCKS = [
        # Rate-sensitive financials
        'JPM', 'BAC', 'USB', 'XLF',
        # Growth stocks (policy sensitive)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
        # Market-sensitive ETFs
        'SPY', 'QQQ', 'IWM'
    ]
    
    # High-Volume Stocks for Microstructure Breakouts
    MICROSTRUCTURE_UNIVERSE = [
        # Major ETFs (tight spreads)
        'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
        # Large Cap Tech (tight spreads)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
        # High volume names
        'AMD', 'INTC', 'NFLX', 'CRM', 'ORCL'
    ]
    
    # Personal Watchlist (Blue chip favorites to always include)
    PERSONAL_WATCHLIST = [
        # Blue chip favorites
        'AAPL', 'MSFT', 'JNJ', 'PG', 'KO',
        # Value plays
        'USB', 'TGT', 'CVS', 'XOM', 'CVX',
        # ETFs
        'SPY', 'QQQ', 'VTV', 'SCHD'
    ]
    
    # ========================================================================
    # EXISTING STRATEGY STOCK LISTS
    # ========================================================================
    
    # Sector Rotation Strategy - All major sector ETFs
    SECTOR_ROTATION = [
        'XLK',   # Technology
        'XLF',   # Financials
        'XLE',   # Energy
        'XLV',   # Healthcare
        'XLI',   # Industrials
        'XLP',   # Consumer Staples
        'XLU',   # Utilities
        'XLY',   # Consumer Discretionary
        'XLB',   # Materials
        'XLRE',  # Real Estate
        'XLC',   # Communication Services
    ]
    
    # International Strategy - Global exposure ETFs and ADRs
    INTERNATIONAL_OUTPERFORMANCE = [
        # Broad International Developed
        'VEA',   # Vanguard FTSE Developed Markets - 0.05% expense ratio
        'EFA',   # iShares MSCI EAFE - Core international
        'VXUS',  # Vanguard Total International Stock
        'IEFA',  # iShares Core MSCI EAFE
        
        # Currency Hedged Options
        'HEFA',  # iShares Currency Hedged MSCI EAFE
        'HEDJ',  # WisdomTree Europe Hedged Equity
        
        # Regional ETFs
        'VGK',   # Vanguard FTSE Europe
        'EWJ',   # iShares MSCI Japan
        'EEMA',  # iShares MSCI Emerging Markets Asia
        'VWO',   # Vanguard FTSE Emerging Markets
        
        # Country-Specific
        'EWG',   # Germany ETF
        'EWU',   # United Kingdom ETF
        'EWY',   # South Korea ETF
        'INDA',  # India ETF
        'FXI',   # China Large-Cap ETF
        'EWT',   # Taiwan ETF
        
        # International ADRs
        'ASML',  # ASML Holding - Dutch semiconductor
        'NVO',   # Novo Nordisk - Danish pharma
        'UL',    # Unilever - Consumer goods        
        'TSM',   # Taiwan Semiconductor
        'BABA',  # Alibaba - Chinese e-commerce
        'JD',    # JD.com - Chinese e-commerce
    ]
    
    # Value-Rate Strategy - REITs and Financials
    VALUE_RATE_UNIVERSE = [
        # REIT Sectors
        # Industrial REITs
        'PLD', 'EXR',
        
        # Healthcare REITs
        'WELL', 'VTR',
        
        # Retail REITs  
        'FRT', 'REG', 'SPG',
        
        # Infrastructure REITs
        'CCI', 'AMT', 'EQIX', 'DLR',
        
        # Office REITs
        'BXP', 'VNO',
        
        # Residential REITs
        'EQR', 'AVB', 'MAA',
        
        # REIT ETFs
        'XLRE', 'IYR', 'SCHH',
        
        # Financial Stocks
        # Money Center Banks
        'JPM', 'BAC', 'WFC', 'C',
        
        # Regional Banks (high rate sensitivity)
        'USB', 'TFC', 'PNC',
        
        # Investment Banks
        'GS', 'MS',
        
        # Insurance
        'BRK-B', 'AIG',
        
        # Financial ETFs
        'XLF', 'KBE',  # KBE = SPDR S&P Bank ETF
    ]
    
    # Microstructure Strategy - High liquidity, tight spreads
    MICROSTRUCTURE_BREAKOUT = [
        # Major ETFs with tightest spreads
        'SPY', 'QQQ', 'IWM', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU',
        'VTI', 'VTV', 'VUG', 'IWD', 'IWF',
        
        # Mega Cap Stocks - Best spreads
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
        'BRK-B', 'JNJ', 'JPM', 'V', 'MA', 'UNH', 'HD',
        
        # High Volume Growth Stocks
        'AMD', 'NFLX', 'CRM', 'ADBE', 'PYPL', 'ROKU', 'XYZ', 'ZM',
        
        # Cryptocurrency ETFs (high volatility for breakouts)
        'COIN', 'MSTR',
    ]
    
    # Policy Momentum Strategy - Fed-sensitive stocks
    POLICY_MOMENTUM = [
        # Rate-Sensitive Sectors
        'XLF', 'XLRE', 'XLU',  # Financials, REITs, Utilities
        
        # Banks (most Fed-sensitive)
        'JPM', 'BAC', 'WFC', 'USB', 'TFC', 'PNC',
        
        # REITs (rate-sensitive)
        'O', 'PLD', 'CCI', 'AMT', 'SPG', 'EQR',
        
        # Utilities (rate-sensitive)
        'DUK', 'SO', 'D', 'NEE', 'ES',
        
        # Growth stocks (affected by discount rates)
        'TSLA', 'NVDA', 'AMD', 'CRM', 'NFLX', 'ROKU',
        
        # Volatility products
        'VXX', 'UVXY', 'SVXY',  # VIX-related ETFs
        'SQQQ', 'TQQQ',         # Leveraged Nasdaq ETFs
        
        # Treasury ETFs (direct Fed policy impact)
        'TLT', 'IEF', 'SHY',
        
        # Dollar-sensitive
        'GLD', 'SLV', 'UUP', 'FXE',  # Gold, Silver, Dollar ETFs
    ]
    
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
        
        # International Gaps
        'VEA', 'EFA', 'VGK', 'EWJ', 'VWO',
    ]
    
    # Bullish Momentum Dip Strategy - High-quality momentum stocks
    BULLISH_MOMENTUM_UNIVERSE = [
        # Mega Cap Tech - Classic momentum leaders
        'AAPL',  # Apple - Premium momentum with institutional support
        'MSFT',  # Microsoft - Consistent momentum trends
        'GOOGL', # Alphabet - Search/AI momentum
        'AMZN',  # Amazon - E-commerce/cloud momentum  
        'NVDA',  # Nvidia - AI chip momentum leader
        'META',  # Meta - Social media recovery momentum
        'TSLA',  # Tesla - EV/tech momentum (high beta)
        
        # High-Growth Tech
        'CRM',   # Salesforce - Enterprise software momentum
        'ADBE',  # Adobe - Creative software momentum
        'NFLX',  # Netflix - Streaming momentum
        'ORCL',  # Oracle - Cloud transition momentum
        'INTC',  # Intel - Semiconductor recovery momentum
        'AMD',   # AMD - CPU/GPU momentum
        'PYPL',  # PayPal - Digital payments momentum
        'SNOW',  # Snowflake - Cloud data momentum
        'PLTR',  # Palantir - Big data analytics momentum
        'ZM',    # Zoom - Video communications momentum
        
        # Growth ETFs for momentum plays
        'QQQ',   # Nasdaq 100 - Tech momentum ETF
        'ARKK',  # ARK Innovation - Disruptive growth momentum
        'ARKW',  # ARK Next Generation Internet
        'ARKQ',  # ARK Autonomous & Robotics
        'VGT',   # Vanguard Information Technology
        'XLK',   # Technology Select Sector SPDR
        'IGV',   # iShares Expanded Tech-Software
        'SKYY',  # First Trust Cloud Computing ETF
        
        # Communication & Media Momentum
        'DIS',   # Disney - Entertainment momentum
        'CMCSA', # Comcast - Media/broadband momentum  
        'ROKU',  # Roku - Streaming platform momentum
        'SPOT',  # Spotify - Music streaming momentum
        'UBER',  # Uber - Ride-sharing/delivery momentum
        'ABNB',  # Airbnb - Travel recovery momentum
        
        # Healthcare Innovation Momentum
        'JNJ',   # Johnson & Johnson - Healthcare momentum
        'UNH',   # UnitedHealth - Healthcare services momentum
        'PFE',   # Pfizer - Pharmaceutical momentum
        'MRNA',  # Moderna - Biotech momentum
        'BNTX',  # BioNTech - mRNA technology momentum
        'REGN',  # Regeneron - Biotech innovation
        'GILD',  # Gilead - Antiviral momentum
        
        # Financial Momentum (rate beneficiaries)
        'JPM',   # JPMorgan Chase - Banking momentum
        'BAC',   # Bank of America - Financial momentum
        'GS',    # Goldman Sachs - Investment banking momentum
        'MS',    # Morgan Stanley - Wealth management momentum
        'V',     # Visa - Payment processing momentum
        'MA',    # Mastercard - Digital payments momentum
        'PYPL',  # PayPal - Digital wallet momentum
        
        # Consumer Momentum Plays
        'AMZN',  # Amazon - E-commerce momentum
        'HD',    # Home Depot - Home improvement momentum
        'NKE',   # Nike - Athletic apparel momentum
        'SBUX',  # Starbucks - Premium coffee momentum
        'MCD',   # McDonald's - QSR momentum
        'TGT',   # Target - Retail momentum
        'COST',  # Costco - Warehouse club momentum
        
        # Industrial Momentum
        'CAT',   # Caterpillar - Infrastructure momentum
        'BA',    # Boeing - Aerospace recovery momentum
        'DE',    # Deere - Agricultural equipment momentum
        'HON',   # Honeywell - Industrial technology momentum
        'GE',    # General Electric - Industrial turnaround momentum
        'RTX',   # Raytheon - Defense momentum
        'LMT',   # Lockheed Martin - Defense contractor momentum
        
        # Energy Momentum (commodity plays)
        'XOM',   # Exxon Mobil - Energy momentum
        'CVX',   # Chevron - Integrated oil momentum
        'COP',   # ConocoPhillips - Shale momentum
        'EOG',   # EOG Resources - Energy independence momentum
        'SLB',   # Schlumberger - Oilfield services momentum
        'XLE',   # Energy Select Sector SPDR ETF
        
        # Semiconductor Momentum
        'NVDA',  # Nvidia - AI/GPU leader
        'AMD',   # AMD - CPU/GPU competition
        'INTC',  # Intel - Foundry recovery
        'QCOM',  # Qualcomm - Mobile chips
        'AVGO',  # Broadcom - Diversified semiconductors
        'MU',    # Micron - Memory semiconductors
        'TSM',   # Taiwan Semiconductor - Foundry leader
        'AMAT',  # Applied Materials - Semiconductor equipment
        'SOXX',  # iShares Semiconductor ETF
        
        # Cloud/Software Momentum
        'CRM',   # Salesforce - CRM leader
        'SNOW',  # Snowflake - Cloud data platform
        'PLTR',  # Palantir - Big data analytics
        'ZM',    # Zoom - Video communications
        'DOCN',  # DigitalOcean - Cloud infrastructure
        'NET',   # Cloudflare - Edge computing
        'DDOG',  # Datadog - Cloud monitoring
        'OKTA',  # Okta - Identity management
        
        # EV/Clean Energy Momentum
        'TSLA',  # Tesla - EV leader
        'RIVN',  # Rivian - EV trucks
        'LCID',  # Lucid Motors - Luxury EVs
        'NIO',   # NIO - Chinese EV
        'XPEV',  # XPeng - Chinese EV
        'LI',    # Li Auto - Chinese EV
        'ICLN',  # iShares Global Clean Energy ETF
        'PBW',   # Invesco WilderHill Clean Energy ETF
        
        # Broad Market Momentum ETFs
        'SPY',   # S&P 500 - Overall market momentum
        'QQQ',   # Nasdaq 100 - Tech momentum
        'IWM',   # Russell 2000 - Small cap momentum
        'VTI',   # Total Stock Market - Broad momentum
        'VUG',   # Vanguard Growth ETF - Growth momentum
        'MTUM',  # iShares MSCI USA Momentum Factor ETF
        'QUAL',  # iShares MSCI USA Quality Factor ETF
        'USMV',  # iShares MSCI USA Min Vol Factor ETF
    ]
    
    # ========================================================================
    # STRATEGY ALLOCATION FRAMEWORKS
    # ========================================================================
    
    # Conservative Portfolio (Lower risk, steady income)
    CONSERVATIVE_STRATEGY_UNIVERSE = [
        # Core positions (60%)
        'SPY', 'VTV', 'VEA',  # Broad market exposure
        
        # Income focus (25%)
        'O', 'PLD', 'CCI', 'USB', 'TFC', 'DUK', 'SO',
        
        # International (15%)
        'VEA', 'VGK', 'EWJ',
    ]
    
    # Aggressive Growth Portfolio (Higher risk, growth focused)
    AGGRESSIVE_STRATEGY_UNIVERSE = [
        # Growth core (40%)
        'QQQ', 'NVDA', 'TSLA', 'AMD', 'CRM',
        
        # Sector rotation (30%)
        'XLK', 'XLF', 'XLE', 'XLV', 'XLI',
        
        # International growth (15%)
        'VWO', 'EEMA', 'EWY', 'INDA',
        
        # Momentum/Breakout (15%)
        'SPY', 'QQQ', 'IWM',
    ]
    
    # Balanced Portfolio (Moderate risk, diversified)
    BALANCED_STRATEGY_UNIVERSE = [
        # Core holdings (50%)
        'SPY', 'QQQ', 'VTV', 'VEA',
        
        # Value/Income (25%)
        'USB', 'PLD', 'O', 'XLF', 'XLRE',
        
        # Growth/Momentum (15%)
        'NVDA', 'CRM', 'XLK',
        
        # International (10%)
        'VEA', 'VGK', 'VWO',
    ]
    
    # ========================================================================
    # BACKWARD COMPATIBILITY
    # ========================================================================
    
    # Legacy aliases maintained for existing code
    GAP_TRADING_STOCKS = GAP_TRADING
    GAP_TRADING_UNIVERSE = BOLLINGER_MEAN_REVERSION + GAP_TRADING
    
    # Maintain existing structure
    DIVIDEND_ARISTOCRATS_VALUE = [
        'PG', 'KO', 'JNJ', 'XOM', 'CVX', 'CAT', 'MCD', 'TGT', 'LOW',
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
    
    # ETF lists
    ETFS = ['SPY', 'QQQ', 'IWM', 'VTV', 'IWD', 'XLF', 'XLE', 'XLV', 'XLI', 'XLU', 
            'XLP', 'XLRE', 'VEA', 'EFA', 'VGK', 'EWJ', 'VWO']
    
    # Market cap classifications
    MEGA_CAP = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
    LARGE_CAP = ['JPM', 'BAC', 'XOM', 'CVX', 'JNJ', 'PG', 'UNH', 'DHR', 'CAT', 'NUE']
    MID_CAP = ['ROKU', 'PTON', 'ZM', 'PLTR', 'SNOW', 'CVS', 'CHRD']

    # ========================================================================
    # UTILITY METHODS AND MAPPINGS
    # ========================================================================
    
    @classmethod
    def get_stocks_for_strategy(cls, strategy_name: str) -> list:
        """Return appropriate stock list for given strategy"""
        
        strategy_mapping = {
            'BollingerMeanReversion': cls.BOLLINGER_MEAN_REVERSION,
            'SectorRotation': cls.SECTOR_ROTATION,
            'International': cls.INTERNATIONAL_OUTPERFORMANCE,
            'ValueRate': cls.VALUE_RATE_UNIVERSE,
            'MicrostructureBreakout': cls.MICROSTRUCTURE_BREAKOUT,
            'PolicyMomentum': cls.POLICY_MOMENTUM,
            'GapTrading': cls.GAP_TRADING,
            'BullishMomentumDip': cls.BULLISH_MOMENTUM_UNIVERSE,
            'Conservative': cls.CONSERVATIVE_STRATEGY_UNIVERSE,
            'Aggressive': cls.AGGRESSIVE_STRATEGY_UNIVERSE,
            'Balanced': cls.BALANCED_STRATEGY_UNIVERSE,
        }
        
        return strategy_mapping.get(strategy_name, cls.BOLLINGER_MEAN_REVERSION)
    
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
            'SectorRotation': {
                'stocks': len(cls.SECTOR_ROTATION),
                'description': 'Volatility-adjusted sector momentum rotation',
                'market_condition': 'FREQUENT_SECTOR_ROTATION',
                'volatility_target': 'VIX-scaled position sizing'
            },
            'International': {
                'stocks': len(cls.INTERNATIONAL_OUTPERFORMANCE),
                'description': 'Capitalize on MSCI EAFE +11.21% outperformance',
                'market_condition': 'INTERNATIONAL_ROTATION',
                'volatility_target': 'Currency-adjusted exposure'
            },
            'ValueRate': {
                'stocks': len(cls.VALUE_RATE_UNIVERSE),
                'description': 'REITs 9% undervalued + financials in rate environment',
                'market_condition': 'RATE_ENVIRONMENT_VALUE',
                'volatility_target': 'Rate-sensitive positioning'
            },
            'MicrostructureBreakout': {
                'stocks': len(cls.MICROSTRUCTURE_BREAKOUT),
                'description': 'Exploit 21-45% tighter spreads for precise entries',
                'market_condition': 'IMPROVED_LIQUIDITY',
                'volatility_target': 'Spread-optimized execution'
            },
            'PolicyMomentum': {
                'stocks': len(cls.POLICY_MOMENTUM),
                'description': 'Fed-driven volatility and policy uncertainty plays',
                'market_condition': 'POLICY_UNCERTAINTY',
                'volatility_target': 'Event-driven volatility'
            }
        }