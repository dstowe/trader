# check_webull_day_trading_data.py - TEMPORARY SCRIPT TO CHECK DAY TRADING DATA
"""
Temporary script to check what day trading information Webull provides
This script can be deleted after we determine what data is available
"""

import sys
import os
import json
import logging
from datetime import datetime
from pprint import pprint

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system.webull.webull import webull
from trading_system.auth import CredentialManager, LoginManager, SessionManager
from trading_system.accounts import AccountManager
from personal_config import PersonalTradingConfig

def setup_logging():
    """Setup simple logging for this test script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def check_day_trading_data():
    """Check what day trading data Webull provides"""
    logger = setup_logging()
    config = PersonalTradingConfig()
    
    print("🔍 CHECKING WEBULL DAY TRADING DATA")
    print("=" * 50)
    
    try:
        # Initialize Webull and auth components
        wb = webull()
        credential_manager = CredentialManager(logger=logger)
        login_manager = LoginManager(wb, credential_manager, logger)
        session_manager = SessionManager(logger=logger)
        
        # Try to authenticate
        print("1. Attempting to authenticate...")
        
        if session_manager.auto_manage_session(wb):
            if login_manager.check_login_status():
                print("✅ Using existing session")
            else:
                session_manager.clear_session()
                if not login_manager.login_automatically():
                    print("❌ Authentication failed")
                    return
        elif not login_manager.login_automatically():
            print("❌ Authentication failed")
            return
            
        print("✅ Authentication successful")
        
        # Initialize account manager
        account_manager = AccountManager(wb, config, logger)
        
        print("\n2. Discovering accounts...")
        if not account_manager.discover_accounts():
            print("❌ Failed to discover accounts")
            return
            
        print("✅ Accounts discovered")
        
        # Check each account for day trading data
        print("\n3. Checking day trading data for each account...")
        print("=" * 50)
        
        for account_id, account in account_manager.accounts.items():
            print(f"\n📊 ACCOUNT: {account.account_type} (ID: {account_id})")
            print("-" * 40)
            
            # Switch to this account
            if not account_manager.switch_to_account(account):
                print(f"❌ Failed to switch to account {account_id}")
                continue
            
            # Get full account data
            print("Fetching full account data...")
            account_data = wb.get_account()
            
            if not account_data:
                print("❌ No account data returned")
                continue
            
            print("✅ Account data retrieved")
            
            # Look for day trading related fields
            day_trading_fields = {}
            
            # Check top-level fields
            for key, value in account_data.items():
                if any(keyword in key.lower() for keyword in ['day', 'trade', 'pdt', 'pattern']):
                    day_trading_fields[f"top_level_{key}"] = value
            
            # Check accountMembers for day trading fields
            if 'accountMembers' in account_data:
                print(f"Checking {len(account_data['accountMembers'])} account members...")
                
                for member in account_data['accountMembers']:
                    key = member.get('key', '')
                    value = member.get('value', '')
                    
                    if any(keyword in key.lower() for keyword in ['day', 'trade', 'pdt', 'pattern', 'left', 'remain', 'count']):
                        day_trading_fields[f"member_{key}"] = value
            
            # Check for nested objects that might contain day trading info
            for key, value in account_data.items():
                if isinstance(value, dict):
                    for nested_key, nested_value in value.items():
                        if any(keyword in nested_key.lower() for keyword in ['day', 'trade', 'pdt', 'pattern']):
                            day_trading_fields[f"{key}_{nested_key}"] = nested_value
            
            # Display findings
            if day_trading_fields:
                print(f"🎯 FOUND DAY TRADING RELATED FIELDS:")
                for field_name, field_value in day_trading_fields.items():
                    print(f"   {field_name}: {field_value}")
            else:
                print("⚠️ No obvious day trading fields found")
            
            # Also check for trading permissions/restrictions
            print(f"\n📋 Account Details:")
            print(f"   Account Type: {account.account_type}")
            print(f"   Account Value: ${account.net_liquidation:,.2f}")
            print(f"   Settled Funds: ${account.settled_funds:,.2f}")
            print(f"   Status: {account.status}")
            
            # Save raw account data to file for detailed inspection
            filename = f"account_data_{account.account_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(account_data, f, indent=2, default=str)
                print(f"💾 Raw account data saved to: {filename}")
            except Exception as e:
                print(f"⚠️ Could not save account data: {e}")
        
        # Try to get trading activities/history for day trade detection
        print(f"\n4. Checking recent trading activities...")
        print("=" * 50)
        
        try:
            # Get recent order history
            print("Fetching order history...")
            orders = wb.get_history_orders(status='All', count=20)
            
            if orders and 'data' in orders:
                print(f"✅ Found {len(orders['data'])} recent orders")
                
                # Look for day trading indicators in orders
                day_trade_indicators = {}
                
                for order in orders['data'][:5]:  # Check first 5 orders
                    for key, value in order.items():
                        if any(keyword in key.lower() for keyword in ['day', 'trade', 'pdt', 'pattern']):
                            day_trade_indicators[key] = value
                
                if day_trade_indicators:
                    print("🎯 Day trading indicators in orders:")
                    for key, value in day_trade_indicators.items():
                        print(f"   {key}: {value}")
                else:
                    print("⚠️ No day trading indicators found in order data")
                    
                # Save sample order data
                sample_filename = f"sample_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(sample_filename, 'w') as f:
                        json.dump(orders['data'][:3], f, indent=2, default=str)
                    print(f"💾 Sample order data saved to: {sample_filename}")
                except Exception as e:
                    print(f"⚠️ Could not save order data: {e}")
            else:
                print("❌ No order history data returned")
                
        except Exception as e:
            print(f"❌ Error fetching order history: {e}")
        
        # Try to get account activities
        try:
            print("\nFetching account activities...")
            activities = wb.get_activities(index=1, size=20)
            
            if activities and 'data' in activities:
                print(f"✅ Found {len(activities['data'])} recent activities")
                
                # Look for day trading indicators in activities
                for activity in activities['data'][:3]:  # Check first 3 activities
                    activity_type = activity.get('type', '')
                    if 'trade' in activity_type.lower():
                        print(f"Trade activity found: {activity.get('description', 'No description')}")
                        
                        # Check for day trading fields
                        for key, value in activity.items():
                            if any(keyword in key.lower() for keyword in ['day', 'trade', 'pdt', 'pattern']):
                                print(f"   Day trading field: {key} = {value}")
                
                # Save sample activity data
                activity_filename = f"sample_activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(activity_filename, 'w') as f:
                        json.dump(activities['data'][:3], f, indent=2, default=str)
                    print(f"💾 Sample activity data saved to: {activity_filename}")
                except Exception as e:
                    print(f"⚠️ Could not save activity data: {e}")
            else:
                print("❌ No activity data returned")
                
        except Exception as e:
            print(f"❌ Error fetching activities: {e}")
        
        print(f"\n5. Summary and Next Steps")
        print("=" * 50)
        print("✅ Check complete! Review the generated files for:")
        print("   • Day trading fields in account data")
        print("   • Day trade counters or limits")
        print("   • PDT status indicators")
        print("   • Day trades remaining/used counts")
        print("\n🔍 Look for fields like:")
        print("   • dayTradesRemaining, dayTradesLeft")
        print("   • dayTradeCount, dayTradesUsed") 
        print("   • pdtStatus, patternDayTrader")
        print("   • dayTradingBuyingPower")
        print("   • Any fields with 'day', 'trade', 'pdt' keywords")
        
        print(f"\n📁 Files generated:")
        generated_files = [f for f in os.listdir('.') if f.startswith(('account_data_', 'sample_orders_', 'sample_activities_')) and f.endswith('.json')]
        for file in generated_files:
            print(f"   • {file}")
        
        print(f"\n🗑️  Remember to delete this script and generated files when done!")
        
    except Exception as e:
        logger.error(f"❌ Error in day trading data check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Webull Day Trading Data Check...")
    print("This will authenticate and check what day trading data is available.")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
        check_day_trading_data()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")