import sys
import traceback

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        from personal_config import PersonalTradingConfig
        print("✅ PersonalTradingConfig: OK")
    except Exception as e:
        print(f"❌ PersonalTradingConfig: {e}")
        return False
    
    try:
        sys.path.append('trading_system')
        from trading_system import TradingSystem
        print("✅ TradingSystem: OK")
    except Exception as e:
        print(f"❌ TradingSystem: {e}")
        print("Full traceback:", traceback.format_exc())
    
    return True

if __name__ == "__main__":
    test_imports()