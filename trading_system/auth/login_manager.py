# auth/login_manager.py
import time
import logging
import requests
from typing import Tuple, Dict
from .credentials import CredentialManager

class LoginManager:
    """Handles login operations with retry logic, error handling, and enhanced session management"""
    
    def __init__(self, wb, credential_manager: CredentialManager = None, logger=None):
        self.wb = wb
        self.credential_manager = credential_manager or CredentialManager()
        self.logger = logger or logging.getLogger(__name__)
        self.is_logged_in = False
        
        # Login retry settings
        self.max_login_attempts = 3
        self.base_login_delay = 30  # seconds
        self.max_trade_token_attempts = 3
        self.base_trade_token_delay = 10  # seconds
    
    def login_automatically(self) -> bool:
        """Automated login using stored credentials with retry logic and enhanced session management"""
        for attempt in range(1, self.max_login_attempts + 1):
            try:
                self.logger.info(f"Starting automated login attempt {attempt}/{self.max_login_attempts}...")
                
                # Load credentials
                credentials = self.credential_manager.load_credentials()
                
                # Validate credentials
                if not self.credential_manager.validate_credentials(credentials):
                    self.logger.error("❌ Invalid credentials found")
                    return False
                
                # Set DID if provided
                if credentials.get('did'):
                    self.wb._set_did(credentials['did'])
                    self.logger.info("DID set from stored credentials")
                
                # Login to Webull
                self.logger.info("Attempting Webull login...")
                login_result = self.wb.login(
                    username=credentials['username'],
                    password=credentials['password']
                )
                
                # Check login result
                if 'accessToken' in login_result:
                    self.logger.info("✅ Webull login successful")
                    self.is_logged_in = True
                    
                    # Try to get trade token with retries
                    if self._get_trade_token_with_retry(credentials['trading_pin']):
                        self.logger.info("✅ Complete login process successful")
                        return True
                    else:
                        self.logger.error("❌ Failed to get trade token after retries")
                        # Continue to retry loop for complete login failure
                        
                else:
                    # Analyze login failure
                    error_msg = login_result.get('msg', 'Unknown error')
                    error_code = login_result.get('code', 'unknown')
                    
                    self.logger.warning(f"❌ Login attempt {attempt} failed: {error_msg} (Code: {error_code})")
                    
                    # Check if this is a retryable error
                    if not self._is_retryable_login_error(login_result):
                        self.logger.error(f"❌ Non-retryable login error: {error_msg}")
                        return False
                
            except Exception as e:
                self.logger.warning(f"❌ Login attempt {attempt} exception: {e}")
                
                # Check if this is a retryable exception
                if not self._is_retryable_exception(e):
                    self.logger.error(f"❌ Non-retryable exception during login: {e}")
                    return False
            
            # If we get here, we need to retry
            if attempt < self.max_login_attempts:
                # Calculate delay with exponential backoff
                delay = self.base_login_delay * (2 ** (attempt - 1))  # 30, 60, 120 seconds
                delay = min(delay, 300)  # Cap at 5 minutes
                
                self.logger.info(f"⏳ Waiting {delay} seconds before retry {attempt + 1}...")
                time.sleep(delay)
            else:
                self.logger.error(f"❌ All {self.max_login_attempts} login attempts failed")
        
        return False
    
    def login_with_session_management(self, session_manager) -> bool:
        """
        Enhanced login with automatic session management and detailed diagnostics
        
        Args:
            session_manager: SessionManager instance
            
        Returns:
            bool: True if successfully logged in, False otherwise
        """
        try:
            self.logger.info("🔐 Starting enhanced authentication with session management")
            
            # Step 1: Diagnose any existing session issues
            self.logger.info("🔍 Diagnosing session health...")
            diagnosis = session_manager.diagnose_session_issues(self.wb)
            
            if diagnosis['issues']:
                self.logger.info("⚠️  Session issues detected:")
                for issue in diagnosis['issues']:
                    self.logger.info(f"   • {issue}")
            
            # Step 2: Try to use existing session with automatic cleanup
            self.logger.info("🔍 Attempting to use existing session...")
            if session_manager.auto_manage_session(self.wb):
                self.logger.info("✅ Using existing/refreshed session")
                
                # Verify login status with a simple test
                if self.check_login_status():
                    self.is_logged_in = True
                    
                    # Get session info for logging
                    session_info = session_manager.get_session_info()
                    if session_info.get('expires_in_minutes'):
                        self.logger.info(f"📅 Session expires in {session_info['expires_in_minutes']} minutes")
                    
                    return True
                else:
                    self.logger.warning("⚠️  Session loaded but login verification failed")
                    # Clear potentially bad session and try fresh login
                    session_manager.clear_session()
            else:
                self.logger.info("🔄 Session management determined fresh login is needed")
            
            # Step 3: If no valid session, perform fresh login
            self.logger.info("🔄 Performing fresh login...")
            if self.login_automatically():
                self.logger.info("✅ Fresh login successful")
                self.is_logged_in = True
                
                # Save the new session
                if session_manager.save_session(self.wb):
                    self.logger.info("💾 New session saved successfully")
                else:
                    self.logger.warning("⚠️  Could not save new session")
                
                # Clean up old backups
                cleaned = session_manager.cleanup_old_backups()
                if cleaned > 0:
                    self.logger.info(f"🧹 Cleaned up {cleaned} old session backups")
                
                return True
            else:
                self.logger.error("❌ CRITICAL: Fresh login failed after all retries")
                
                # Final diagnosis for troubleshooting
                self.logger.error("🔍 Final session diagnosis:")
                final_diagnosis = session_manager.diagnose_session_issues(self.wb)
                for recommendation in final_diagnosis['recommendations']:
                    self.logger.error(f"   📋 {recommendation}")
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error during enhanced authentication: {e}")
            return False
    
    def _get_trade_token_with_retry(self, trading_pin: str) -> bool:
        """Get trade token with retry logic"""
        for attempt in range(1, self.max_trade_token_attempts + 1):
            try:
                self.logger.info(f"Getting trade token (attempt {attempt}/{self.max_trade_token_attempts})...")
                
                if self.wb.get_trade_token(trading_pin):
                    self.logger.info("✅ Trade token obtained successfully")
                    return True
                else:
                    self.logger.warning(f"❌ Trade token attempt {attempt} failed")
                    
            except Exception as e:
                self.logger.warning(f"❌ Trade token attempt {attempt} exception: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_trade_token_attempts:
                delay = self.base_trade_token_delay * attempt  # 10, 20 seconds
                self.logger.info(f"⏳ Waiting {delay} seconds before trade token retry...")
                time.sleep(delay)
        
        self.logger.error(f"❌ Failed to get trade token after {self.max_trade_token_attempts} attempts")
        return False
    
    def _is_retryable_login_error(self, login_result: Dict) -> bool:
        """Determine if a login error is retryable"""
        error_code = login_result.get('code', '').lower()
        error_msg = login_result.get('msg', '').lower()
        
        # Non-retryable errors (permanent failures)
        non_retryable_codes = [
            'phone.illegal',
            'user.passwd.error',
            'account.freeze',
            'account.lock',
            'user.not.exist'
        ]
        
        non_retryable_messages = [
            'invalid username',
            'invalid password', 
            'account suspended',
            'account locked',
            'user not found'
        ]
        
        # Check for non-retryable conditions
        for code in non_retryable_codes:
            if code in error_code:
                return False
        
        for msg in non_retryable_messages:
            if msg in error_msg:
                return False
        
        # Default to retryable for unknown errors
        return True
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Determine if an exception is retryable"""
        # Network-related exceptions are retryable
        retryable_exceptions = [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            ConnectionError,
            TimeoutError,
            OSError  # Can include network issues
        ]
        
        for exc_type in retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default to retryable for unknown exceptions
        return True
    
    def login_with_credentials(self, username: str, password: str, trading_pin: str, 
                             device_name: str = '', mfa: str = '', 
                             question_id: str = '', question_answer: str = '') -> bool:
        """Login with explicit credentials (for setup or testing)"""
        try:
            self.logger.info("Attempting login with provided credentials...")
            
            login_result = self.wb.login(
                username=username,
                password=password,
                device_name=device_name,
                mfa=mfa,
                question_id=question_id,
                question_answer=question_answer
            )
            
            if 'accessToken' in login_result:
                self.logger.info("✅ Login successful")
                self.is_logged_in = True
                
                # Get trade token
                if self.wb.get_trade_token(trading_pin):
                    self.logger.info("✅ Trade token obtained")
                    return True
                else:
                    self.logger.error("❌ Failed to get trade token")
                    return False
            else:
                self.logger.error(f"❌ Login failed: {login_result.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Exception during login: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout from Webull"""
        try:
            if self.is_logged_in:
                response_code = self.wb.logout()
                if response_code == 200:
                    self.logger.info("🔐 Logged out successfully")
                    self.is_logged_in = False
                    return True
                else:
                    self.logger.warning(f"⚠️ Logout returned code: {response_code}")
                    return False
            else:
                self.logger.info("Already logged out")
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ Logout warning: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """Check if currently logged in with robust error handling for API changes"""
        try:
            # Try to make a simple API call to check login status
            # Use a more basic API call that's less likely to fail
            self.logger.debug("Checking login status with API call...")
            
            # Try getting account details first - this is often more reliable
            try:
                account_data = self.wb.get_account()
                if account_data and isinstance(account_data, dict):
                    self.is_logged_in = True
                    self.logger.debug("Login verified via get_account() call")
                    return True
            except Exception as e:
                self.logger.debug(f"get_account() failed: {e}")
            
            # Fallback: try direct API call to avoid get_account_id's parsing issues
            try:
                headers = self.wb.build_req_headers()
                response = self.wb._session.get(self.wb._urls.account_id(), headers=headers, timeout=self.wb.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and result.get('data'):
                        self.is_logged_in = True
                        self.logger.debug("Login verified via direct account_id API call")
                        
                        # Try to extract and set account details if possible
                        try:
                            account_data = result['data'][0] if result['data'] else {}
                            if 'secAccountId' in account_data:
                                self.wb._account_id = str(account_data['secAccountId'])
                                # Handle zone variable with fallback
                                self.wb.zone_var = str(account_data.get('rzone', account_data.get('zone', 'dc_core_r001')))
                                self.logger.debug(f"Account context set: {self.wb._account_id}")
                        except Exception as e:
                            self.logger.debug(f"Could not extract account details: {e}")
                        
                        return True
                    else:
                        self.logger.debug(f"API returned unsuccessful response: {result}")
                        self.is_logged_in = False
                        return False
                elif response.status_code == 401:
                    self.logger.debug("API returned 401 - session invalid")
                    self.is_logged_in = False
                    return False
                else:
                    self.logger.debug(f"API returned status {response.status_code}")
                    self.is_logged_in = False
                    return False
                    
            except Exception as e:
                self.logger.debug(f"Direct API call failed: {e}")
                self.is_logged_in = False
                return False
                
        except Exception as e:
            self.logger.debug(f"Login status check failed: {e}")
            self.is_logged_in = False
            return False
    
    def refresh_login(self) -> bool:
        """Refresh the login session if possible"""
        try:
            self.logger.info("Attempting to refresh login session...")
            result = self.wb.refresh_login()
            
            if 'accessToken' in result and result['accessToken']:
                self.logger.info("✅ Login session refreshed successfully")
                self.is_logged_in = True
                return True
            else:
                self.logger.warning("❌ Failed to refresh login session")
                self.is_logged_in = False
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error refreshing login: {e}")
            self.is_logged_in = False
            return False
    
    def get_login_info(self) -> Dict:
        """Get information about current login status"""
        return {
            'is_logged_in': self.is_logged_in,
            'access_token_exists': bool(getattr(self.wb, '_access_token', None)),
            'trade_token_exists': bool(getattr(self.wb, '_trade_token', None)),
            'account_id': getattr(self.wb, '_account_id', None),
            'uuid': getattr(self.wb, '_uuid', None)
        }
    
    def validate_session_health(self, session_manager) -> Dict:
        """
        Validate the health of the current session
        
        Args:
            session_manager: SessionManager instance
            
        Returns:
            Dict with session health information
        """
        try:
            health_info = {
                'session_valid': False,
                'login_verified': False,
                'account_accessible': False,
                'expires_soon': False,
                'needs_refresh': False,
                'session_info': {}
            }
            
            # Check session file and data
            session_info = session_manager.get_session_info()
            health_info['session_info'] = session_info
            
            if session_info.get('exists', False):
                health_info['session_valid'] = True
                health_info['expires_soon'] = session_info.get('expires_soon', False)
                
                # Check if login is verified
                if self.check_login_status():
                    health_info['login_verified'] = True
                    health_info['account_accessible'] = True
                
                # Determine if refresh is needed
                expires_in = session_info.get('expires_in_minutes', 0)
                if expires_in and expires_in < 30:  # Less than 30 minutes
                    health_info['needs_refresh'] = True
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"Error validating session health: {e}")
            return {
                'session_valid': False,
                'login_verified': False,
                'account_accessible': False,
                'expires_soon': True,
                'needs_refresh': True,
                'error': str(e)
            }