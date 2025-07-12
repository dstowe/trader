# session_fix.py
"""
Quick fix script for session management issues
Run this to clear corrupted sessions and apply compatibility patches
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """Setup logging for the fix script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def clear_session_files():
    """Clear all session-related files"""
    logger = logging.getLogger(__name__)
    
    session_files = [
        'webull_session.json',
        'webull_session.json.backup_*'
    ]
    
    cleared = 0
    for file_pattern in session_files:
        if '*' in file_pattern:
            # Handle backup files
            import glob
            for file_path in glob.glob(file_pattern):
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️  Removed: {file_path}")
                    cleared += 1
                except Exception as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        else:
            # Handle specific files
            if os.path.exists(file_pattern):
                try:
                    os.remove(file_pattern)
                    logger.info(f"🗑️  Removed: {file_pattern}")
                    cleared += 1
                except Exception as e:
                    logger.warning(f"Could not remove {file_pattern}: {e}")
    
    return cleared

def patch_webull_instance(wb):
    """Apply compatibility patches to webull instance"""
    logger = logging.getLogger(__name__)
    
    def patched_get_account_id(id=0):
        """Patched version that handles missing 'rzone' field"""
        try:
            headers = wb.build_req_headers()
            response = wb._session.get(wb._urls.account_id(), headers=headers, timeout=wb.timeout)
            result = response.json()
            
            if result.get('success') and len(result.get('data', [])) > 0:
                account_data = result['data'][int(id)]
                
                # Handle zone variable with fallbacks
                zone_value = 'dc_core_r001'  # Default
                for zone_field in ['rzone', 'zone', 'zoneVar', 'zone_var']:
                    if zone_field in account_data:
                        zone_value = str(account_data[zone_field])
                        break
                
                wb.zone_var = zone_value
                wb._account_id = str(account_data['secAccountId'])
                return wb._account_id
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Patched get_account_id error: {e}")
            return None
    
    # Apply the patch
    wb.get_account_id = patched_get_account_id
    logger.info("✅ Applied compatibility patches to webull instance")
    return wb

def test_login_with_patches():
    """Test login with compatibility patches applied"""
    logger = logging.getLogger(__name__)
    
    try:
        from trading_system.webull.webull import webull
        from trading_system.auth import CredentialManager, LoginManager, SessionManager
        
        logger.info("🔧 Testing login with compatibility patches...")
        
        # Initialize components
        wb = webull()
        wb = patch_webull_instance(wb)  # Apply patches first
        
        credential_manager = CredentialManager(logger=logger)
        login_manager = LoginManager(wb, credential_manager, logger)
        session_manager = SessionManager(logger=logger)
        
        # Test fresh login
        if login_manager.login_automatically():
            logger.info("✅ Fresh login successful with patches")
            
            # Test if we can save the session
            if session_manager.save_session(wb):
                logger.info("✅ Session saved successfully")
                
                # Test if we can load the session back
                wb2 = webull()
                wb2 = patch_webull_instance(wb2)
                
                if session_manager.load_session(wb2):
                    logger.info("✅ Session loaded back successfully")
                    return True
                else:
                    logger.warning("⚠️  Could not load session back")
                    return False
            else:
                logger.warning("⚠️  Could not save session")
                return False
        else:
            logger.error("❌ Fresh login failed even with patches")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during patched login test: {e}")
        return False

def main():
    """Main fix script"""
    logger = setup_logging()
    
    print("🔧 Webull Session Fix Script")
    print("=" * 40)
    print("This script will:")
    print("1. Clear corrupted session files")
    print("2. Apply compatibility patches")
    print("3. Test fresh login")
    print()
    
    # Step 1: Clear session files
    logger.info("🗑️  Step 1: Clearing session files...")
    cleared = clear_session_files()
    logger.info(f"Cleared {cleared} session files")
    
    # Step 2: Test login with patches
    logger.info("🔧 Step 2: Testing login with compatibility patches...")
    if test_login_with_patches():
        logger.info("✅ Session fix completed successfully!")
        print("\n🎉 SUCCESS!")
        print("Your session management should now work properly.")
        print("You can run your automated trading system normally.")
    else:
        logger.error("❌ Session fix failed")
        print("\n❌ FAILED!")
        print("Please check:")
        print("1. Your credentials are correct")
        print("2. Your network connection")
        print("3. Webull account is not locked")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)