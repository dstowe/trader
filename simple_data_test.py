# simple_data_test.py
"""
Simple standalone test to verify data fetching and analysis components
Run this first to identify any basic issues
"""

import sys
import os

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_yfinance():
    """Test yfinance data fetching"""
    print("🔍 Testing yfinance data fetching...")
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
        
        # Test basic data fetch
        ticker = yf.Ticker("SPY")
        data = ticker.history(period="1mo")
        
        if data.empty:
            print("❌ No data returned from yfinance")
            return False
        
        print(f"✅ Data fetched: {len(data)} rows")
        print(f"   Columns: {list(data.columns)}")
        print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        
        return True
        
    except ImportError:
        print("❌ yfinance not installed. Run: pip install yfinance")
        return False
    except Exception as e:
        print(f"❌ yfinance test failed: {e}")
        return False

def test_technical_indicators():
    """Test technical indicators calculation"""
    print("\n🔍 Testing technical indicators...")
    
    try:
        import yfinance as yf
        import pandas as pd
        import numpy as np
        
        # Get sample data
        ticker = yf.Ticker("SPY")
        data = ticker.history(period="2mo")
        
        if data.empty:
            print("❌ No sample data available")
            return False
        
        # Test Bollinger Bands calculation
        close_prices = data['Close']
        sma_20 = close_prices.rolling(20).mean()
        std_20 = close_prices.rolling(20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        
        print(f"✅ Bollinger Bands calculated")
        print(f"   Latest Upper: ${bb_upper.iloc[-1]:.2f}")
        print(f"   Latest SMA: ${sma_20.iloc[-1]:.2f}")
        print(f"   Latest Lower: ${bb_lower.iloc[-1]:.2f}")
        
        # Test RSI calculation
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        print(f"✅ RSI calculated")
        print(f"   Latest RSI: {rsi.iloc[-1]:.1f}")
        
        # Test gap detection
        prev_close = data['Close'].shift(1)
        current_open = data['Open']
        gap_percent = (current_open - prev_close) / prev_close
        
        print(f"✅ Gap detection calculated")
        print(f"   Latest gap: {gap_percent.iloc[-1]:.3%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Technical indicators test failed: {e}")
        return False

def test_data_fetcher():
    """Test the DataFetcher class"""
    print("\n🔍 Testing DataFetcher class...")
    
    try:
        from trading_system.data.webull_client import DataFetcher
        
        fetcher = DataFetcher()
        print("✅ DataFetcher imported successfully")
        
        # Test fetching data
        symbols = ['SPY', 'QQQ']
        for symbol in symbols:
            print(f"   Testing {symbol}...")
            data = fetcher.fetch_stock_data(symbol, period="1mo")
            
            if data.empty:
                print(f"   ❌ {symbol}: No data")
            else:
                print(f"   ✅ {symbol}: {len(data)} rows")
        
        return True
        
    except ImportError as e:
        print(f"❌ DataFetcher import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ DataFetcher test failed: {e}")
        return False

def test_trading_system():
    """Test TradingSystem creation"""
    print("\n🔍 Testing TradingSystem...")
    
    try:
        from personal_config import PersonalTradingConfig
        from trading_system import TradingSystem
        
        config = PersonalTradingConfig()
        print("✅ PersonalTradingConfig created")
        
        trading_system = TradingSystem(config)
        print("✅ TradingSystem created")
        print(f"   Available strategies: {len(trading_system.strategies)}")
        
        if trading_system.strategies:
            strategy_names = list(trading_system.strategies.keys())
            print(f"   Strategy list: {strategy_names[:3]}...")  # Show first 3
        else:
            print("   ❌ No strategies loaded")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ TradingSystem test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test the complete data analysis pipeline"""
    print("\n🔍 Testing full analysis pipeline...")
    
    try:
        from personal_config import PersonalTradingConfig
        from trading_system import TradingSystem
        
        config = PersonalTradingConfig()
        trading_system = TradingSystem(config)
        
        # Run analysis with small stock list
        test_stocks = ['SPY', 'QQQ', 'AAPL']
        print(f"   Running analysis on: {test_stocks}")
        
        results = trading_system.run_daily_analysis(
            strategy_override='BollingerMeanReversion',
            stock_list_override=test_stocks
        )
        
        if 'error' in results:
            print(f"❌ Analysis failed: {results['error']}")
            return False
        
        print("✅ Full pipeline test passed")
        print(f"   Strategy: {results.get('strategy_used')}")
        print(f"   Stocks analyzed: {results.get('stocks_analyzed')}")
        print(f"   Total signals: {results.get('total_signals')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Simple Data Fetching Test Suite")
    print("=" * 50)
    
    tests = [
        ("YFinance", test_yfinance),
        ("Technical Indicators", test_technical_indicators),
        ("DataFetcher Class", test_data_fetcher),
        ("TradingSystem", test_trading_system),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your data fetching system is working.")
        print("You can now run the full automated system.")
    else:
        print("\n🚨 Some tests failed. Common solutions:")
        
        if not results.get("YFinance", False):
            print("• Install yfinance: pip install yfinance")
            print("• Check internet connection")
        
        if not results.get("DataFetcher Class", False):
            print("• Check trading_system module structure")
            print("• Verify all imports are working")
        
        if not results.get("TradingSystem", False):
            print("• Check strategy imports")
            print("• Verify personal_config.py is correct")
        
        print("\nRun this test again after fixing issues.")

if __name__ == "__main__":
    main()