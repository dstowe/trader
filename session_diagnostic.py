# session_diagnostic.py
"""
Session Diagnostic Tool for debugging authentication issues
Run this when experiencing session problems
"""

import logging
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_system.webull.webull import webull
from trading_system.auth import SessionManager, CredentialManager, LoginManager

def setup_logging():
    """Setup detailed logging for diagnostics"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_session_diagnostics():
    """Run comprehensive session diagnostics"""
    logger = setup_logging()
    logger.info("🔍 Starting Session Diagnostics")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        wb = webull()
        session_manager = SessionManager(logger=logger)
        credential_manager = CredentialManager(logger=logger)
        login_manager = LoginManager(wb, credential_manager, logger)
        
        # Check if credentials exist
        logger.info("📋 CREDENTIAL CHECK")
        logger.info("-" * 30)
        if credential_manager.credentials_exist():
            logger.info("✅ Encrypted credentials found")
            cred_info = credential_manager.get_credential_info()
            logger.info(f"   Username: {cred_info.get('username', 'Unknown')}")
            logger.info(f"   Created: {cred_info.get('created_date', 'Unknown')}")
            logger.info(f"   Has DID: {cred_info.get('has_did', False)}")
        else:
            logger.error("❌ No encrypted credentials found")
            logger.error("   Run setup first: python automated_system.py --setup")
            return False
        
        # Run session diagnosis
        logger.info("\n🔍 SESSION DIAGNOSIS")
        logger.info("-" * 30)
        diagnosis = session_manager.diagnose_session_issues(wb)
        
        logger.info(f"Session file exists: {'✅' if diagnosis['session_file_exists'] else '❌'}")
        logger.info(f"Session data valid: {'✅' if diagnosis['session_data_valid'] else '❌'}")
        logger.info(f"Session data complete: {'✅' if diagnosis['session_data_complete'] else '❌'}")
        logger.info(f"Session not expired: {'✅' if not diagnosis['session_expired'] else '❌'}")
        logger.info(f"API test passed: {'✅' if diagnosis['api_test_passed'] else '❌'}")
        logger.info(f"Refresh token available: {'✅' if diagnosis['refresh_token_available'] else '❌'}")
        
        if diagnosis['issues']:
            logger.info("\n⚠️  ISSUES DETECTED:")
            for issue in diagnosis['issues']:
                logger.info(f"   • {issue}")
        
        if diagnosis['recommendations']:
            logger.info("\n📋 RECOMMENDATIONS:")
            for rec in diagnosis['recommendations']:
                logger.info(f"   • {rec}")
        
        # Test session management
        logger.info("\n🔄 TESTING SESSION MANAGEMENT")
        logger.info("-" * 30)
        
        if session_manager.auto_manage_session(wb):
            logger.info("✅ Session management successful")
            
            # Test login verification
            if login_manager.check_login_status():
                logger.info("✅ Login status verification successful")
            else:
                logger.warning("⚠️  Login status verification failed")
        else:
            logger.warning("⚠️  Session management failed - fresh login needed")
        
        # Get final session info
        logger.info("\n📊 FINAL SESSION STATUS")
        logger.info("-" * 30)
        session_info = session_manager.get_session_info()
        
        if session_info.get('exists', False):
            logger.info("✅ Session exists")
            logger.info(f"   Access token: {'✅' if session_info.get('access_token_exists') else '❌'}")
            logger.info(f"   Refresh token: {'✅' if session_info.get('refresh_token_exists') else '❌'}")
            logger.info(f"   Trade token: {'✅' if session_info.get('trade_token_exists') else '❌'}")
            logger.info(f"   Account ID: {session_info.get('account_id', 'None')}")
            
            expires_in = session_info.get('expires_in_minutes')
            if expires_in is not None:
                if expires_in > 0:
                    logger.info(f"   Expires in: {expires_in} minutes")
                else:
                    logger.warning(f"   ⚠️  Expired {abs(expires_in)} minutes ago")
            
            if session_info.get('expires_soon', False):
                logger.warning("   ⚠️  Session expires soon")
        else:
            logger.info("❌ No session exists")
        
        # Test fresh login if requested
        test_login = input("\n🔄 Test fresh login? (y/n): ").lower().strip()
        if test_login in ['y', 'yes']:
            logger.info("\n🔄 TESTING FRESH LOGIN")
            logger.info("-" * 30)
            
            # Clear existing session first
            session_manager.clear_session()
            
            if login_manager.login_automatically():
                logger.info("✅ Fresh login successful")
                
                # Save new session
                if session_manager.save_session(wb):
                    logger.info("✅ New session saved")
                else:
                    logger.warning("⚠️  Failed to save new session")
            else:
                logger.error("❌ Fresh login failed")
        
        logger.info("\n" + "=" * 60)
        logger.info("🏁 Session diagnostics complete")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during diagnostics: {e}")
        logger.error("Full error details:", exc_info=True)
        return False

def main():
    """Main diagnostic entry point"""
    print("🔍 Webull Session Diagnostic Tool")
    print("=" * 40)
    print("This tool helps diagnose session and authentication issues.")
    print("Run this when experiencing login problems.\n")
    
    success = run_session_diagnostics()
    
    if success:
        print("\n✅ Diagnostics completed successfully")
    else:
        print("\n❌ Diagnostics failed - check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()