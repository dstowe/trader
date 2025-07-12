# auth/session_manager.py
import json
import logging
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

class SessionManager:
    """Manages trading session persistence and token management with automatic cleanup"""
    
    def __init__(self, session_file="webull_session.json", logger=None):
        self.session_file = session_file
        self.logger = logger or logging.getLogger(__name__)
        self.session_data = {}
        
        # Session expiration thresholds
        self.EXPIRATION_WARNING_MINUTES = 15  # Remove sessions expiring within 15 minutes
        self.EXPIRATION_CRITICAL_MINUTES = 5   # Critical threshold for immediate action
        
    def save_session(self, wb) -> bool:
        """Save current session data"""
        try:
            session_data = {
                'access_token': getattr(wb, '_access_token', ''),
                'refresh_token': getattr(wb, '_refresh_token', ''),
                'token_expire': getattr(wb, '_token_expire', ''),
                'uuid': getattr(wb, '_uuid', ''),
                'account_id': getattr(wb, '_account_id', ''),
                'trade_token': getattr(wb, '_trade_token', ''),
                'zone_var': getattr(wb, 'zone_var', ''),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            self.session_data = session_data
            self.logger.info(f"Session saved to {self.session_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self, wb) -> bool:
        """Load session data into webull instance with robust validation and API patches"""
        try:
            if not os.path.exists(self.session_file):
                self.logger.info("No session file found")
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            self.session_data = session_data
            
            # Check if session is still valid (basic validation)
            if not self._is_session_valid(session_data):
                self.logger.info("Session expired or invalid based on timestamps")
                return False
            
            # Apply session data to webull instance
            wb._access_token = session_data.get('access_token', '')
            wb._refresh_token = session_data.get('refresh_token', '')
            wb._token_expire = session_data.get('token_expire', '')
            wb._uuid = session_data.get('uuid', '')
            wb._account_id = session_data.get('account_id', '')
            wb._trade_token = session_data.get('trade_token', '')
            wb.zone_var = session_data.get('zone_var', 'dc_core_r001')
            
            self.logger.info("Session data loaded into webull instance")
            
            # Apply compatibility patches
            try:
                from .webull_api_patch import apply_webull_patches
                wb = apply_webull_patches(wb)
                self.logger.debug("Applied webull compatibility patches")
            except ImportError:
                self.logger.debug("Webull patches not available - using built-in compatibility")
            except Exception as e:
                self.logger.debug(f"Could not apply webull patches: {e}")
            
            # Test if session actually works with the API
            if self._test_session_with_api(wb):
                self.logger.info("✅ Session validated with API successfully")
                return True
            else:
                self.logger.warning("❌ Session failed API validation")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return False
    
    def _test_session_with_api(self, wb) -> bool:
        """Test if the loaded session actually works with Webull API"""
        try:
            # Try a simple API call that requires authentication
            self.logger.debug("Testing session with API call...")
            
            # First try a basic account details call that's less prone to structure changes
            try:
                account_data = wb.get_account()
                if account_data and isinstance(account_data, dict):
                    self.logger.debug("Session validated via get_account() call")
                    return True
            except Exception as e:
                self.logger.debug(f"get_account() failed: {e}")
            
            # Try get_account_id with better error handling for the 'rzone' issue
            try:
                # Build headers to test authentication without relying on get_account_id's parsing
                headers = wb.build_req_headers()
                response = wb._session.get(wb._urls.account_id(), headers=headers, timeout=wb.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and result.get('data'):
                        self.logger.debug("Session validated via account_id API call")
                        return True
                    else:
                        self.logger.debug(f"API returned unsuccessful response: {result}")
                        return False
                elif response.status_code == 401:
                    self.logger.debug("API returned 401 - session invalid")
                    return False
                else:
                    self.logger.debug(f"API returned status {response.status_code}")
                    return False
                    
            except Exception as e:
                self.logger.debug(f"Direct API test failed: {e}")
                return False
            
        except Exception as e:
            self.logger.debug(f"Session API test failed: {e}")
            return False
    
    def _is_session_valid(self, session_data: Dict) -> bool:
        """Check if session data is still valid"""
        try:
            # Check if required fields exist
            required_fields = ['access_token', 'refresh_token', 'token_expire']
            for field in required_fields:
                if not session_data.get(field):
                    self.logger.debug(f"Missing required field: {field}")
                    return False
            
            # Check token expiration
            token_expire = session_data.get('token_expire', '')
            if token_expire:
                try:
                    expire_time = datetime.fromisoformat(token_expire.replace('+0000', '+00:00'))
                    current_time = datetime.now(expire_time.tzinfo)
                    
                    # Use critical threshold for validity check
                    if expire_time <= current_time + timedelta(minutes=self.EXPIRATION_CRITICAL_MINUTES):
                        self.logger.debug("Token is expired or expires very soon")
                        return False
                        
                except ValueError as e:
                    self.logger.debug(f"Could not parse token expiration: {e}")
                    return False
            
            # Check session age
            saved_at = session_data.get('saved_at', '')
            if saved_at:
                try:
                    saved_time = datetime.fromisoformat(saved_at)
                    age = datetime.now() - saved_time
                    
                    # Sessions older than 24 hours are considered stale
                    if age > timedelta(hours=24):
                        self.logger.debug("Session is too old")
                        return False
                        
                except ValueError as e:
                    self.logger.debug(f"Could not parse saved time: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating session: {e}")
            return False
    
    def _should_remove_expiring_session(self, session_data: Dict) -> bool:
        """Check if session should be removed due to upcoming expiration"""
        try:
            token_expire = session_data.get('token_expire', '')
            if not token_expire:
                return True  # Remove sessions without expiration info
            
            try:
                expire_time = datetime.fromisoformat(token_expire.replace('+0000', '+00:00'))
                current_time = datetime.now(expire_time.tzinfo)
                
                # Remove if expires within warning threshold
                time_until_expire = expire_time - current_time
                warning_threshold = timedelta(minutes=self.EXPIRATION_WARNING_MINUTES)
                
                if time_until_expire <= warning_threshold:
                    minutes_left = int(time_until_expire.total_seconds() / 60)
                    self.logger.info(f"Session expires in {minutes_left} minutes - removing proactively")
                    return True
                
            except ValueError as e:
                self.logger.debug(f"Could not parse expiration time: {e}")
                return True  # Remove sessions with invalid expiration
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking session expiration: {e}")
            return True  # Remove sessions that can't be checked
    
    def remove_expiring_session(self) -> bool:
        """Remove session file if it's expiring soon"""
        try:
            if not os.path.exists(self.session_file):
                return True  # Already removed
            
            # Load session data to check expiration
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not read session file for expiration check: {e}")
                # Remove corrupted session file
                return self.clear_session()
            
            # Check if session should be removed
            if self._should_remove_expiring_session(session_data):
                self.logger.info("Removing expiring session proactively")
                return self.clear_session()
            
            return False  # Session not removed
            
        except Exception as e:
            self.logger.error(f"Error checking/removing expiring session: {e}")
            return False
    
    def clear_session(self) -> bool:
        """Clear stored session data"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                self.logger.info("Session file deleted")
            
            self.session_data = {}
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing session: {e}")
            return False
    
    def refresh_session(self, wb) -> bool:
        """Refresh the session using refresh token with robust error handling"""
        try:
            self.logger.info("Attempting to refresh session...")
            
            # Check if we have a refresh token
            if not hasattr(wb, '_refresh_token') or not wb._refresh_token:
                self.logger.warning("No refresh token available for session refresh")
                return False
            
            # Try to refresh login with better error handling
            try:
                result = wb.refresh_login()
                
                # Check if we got a valid response
                if not result:
                    self.logger.warning("❌ Refresh login returned empty result")
                    return False
                
                # Check if refresh was successful
                if isinstance(result, dict) and 'accessToken' in result and result['accessToken']:
                    self.logger.info("✅ Session refreshed successfully")
                    
                    # Save the refreshed session
                    self.save_session(wb)
                    return True
                else:
                    # Log the actual response for debugging
                    self.logger.warning(f"❌ Failed to refresh session - invalid response: {result}")
                    return False
                    
            except requests.exceptions.HTTPError as e:
                if hasattr(e, 'response') and e.response.status_code == 403:
                    self.logger.warning("❌ Refresh token expired or invalid (HTTP 403)")
                else:
                    self.logger.warning(f"❌ HTTP error during session refresh: {e}")
                return False
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"❌ Network error during session refresh: {e}")
                return False
            except ValueError as e:
                # This catches JSON parsing errors
                self.logger.warning(f"❌ Invalid JSON response during session refresh (likely expired token): {e}")
                return False
            except Exception as e:
                self.logger.warning(f"❌ Unexpected error during session refresh: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in refresh_session method: {e}")
            return False
    
    def diagnose_session_issues(self, wb) -> Dict:
        """
        Diagnose session-related issues for debugging
        
        Returns:
            Dict with diagnostic information
        """
        diagnosis = {
            'session_file_exists': False,
            'session_data_valid': False,
            'session_data_complete': False,
            'session_expired': False,
            'api_test_passed': False,
            'refresh_token_available': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Check if session file exists
            if os.path.exists(self.session_file):
                diagnosis['session_file_exists'] = True
                
                try:
                    with open(self.session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    diagnosis['session_data_valid'] = True
                    
                    # Check if session data is complete
                    required_fields = ['access_token', 'refresh_token', 'token_expire', 'uuid']
                    missing_fields = [field for field in required_fields if not session_data.get(field)]
                    
                    if not missing_fields:
                        diagnosis['session_data_complete'] = True
                    else:
                        diagnosis['issues'].append(f"Missing session fields: {missing_fields}")
                    
                    # Check if session is expired
                    if self._is_session_valid(session_data):
                        diagnosis['session_expired'] = False
                    else:
                        diagnosis['session_expired'] = True
                        diagnosis['issues'].append("Session has expired based on timestamps")
                    
                    # Check if refresh token is available
                    if session_data.get('refresh_token'):
                        diagnosis['refresh_token_available'] = True
                    else:
                        diagnosis['issues'].append("No refresh token available")
                    
                    # Test API connectivity if we have basic session data
                    if diagnosis['session_data_complete'] and not diagnosis['session_expired']:
                        # Temporarily apply session data
                        original_access_token = getattr(wb, '_access_token', '')
                        original_refresh_token = getattr(wb, '_refresh_token', '')
                        original_uuid = getattr(wb, '_uuid', '')
                        original_account_id = getattr(wb, '_account_id', '')
                        original_zone_var = getattr(wb, 'zone_var', '')
                        
                        try:
                            wb._access_token = session_data.get('access_token', '')
                            wb._refresh_token = session_data.get('refresh_token', '')
                            wb._uuid = session_data.get('uuid', '')
                            wb._account_id = session_data.get('account_id', '')
                            wb.zone_var = session_data.get('zone_var', 'dc_core_r001')
                            
                            if self._test_session_with_api(wb):
                                diagnosis['api_test_passed'] = True
                            else:
                                diagnosis['issues'].append("Session failed API validation - likely expired or invalid")
                        
                        finally:
                            # Restore original values
                            wb._access_token = original_access_token
                            wb._refresh_token = original_refresh_token
                            wb._uuid = original_uuid
                            wb._account_id = original_account_id
                            wb.zone_var = original_zone_var
                
                except json.JSONDecodeError:
                    diagnosis['issues'].append("Session file contains invalid JSON")
                except Exception as e:
                    diagnosis['issues'].append(f"Error reading session file: {e}")
            else:
                diagnosis['issues'].append("No session file found")
            
            # Generate recommendations
            if not diagnosis['session_file_exists']:
                diagnosis['recommendations'].append("Fresh login required - no session file")
            elif not diagnosis['session_data_valid']:
                diagnosis['recommendations'].append("Clear corrupted session file and perform fresh login")
            elif not diagnosis['session_data_complete']:
                diagnosis['recommendations'].append("Session data incomplete - fresh login recommended")
            elif diagnosis['session_expired']:
                if diagnosis['refresh_token_available']:
                    diagnosis['recommendations'].append("Try session refresh, fallback to fresh login")
                else:
                    diagnosis['recommendations'].append("Session expired and no refresh token - fresh login required")
            elif not diagnosis['api_test_passed']:
                diagnosis['recommendations'].append("Session data looks valid but API test failed - try refresh or fresh login")
            else:
                diagnosis['recommendations'].append("Session appears healthy")
            
        except Exception as e:
            diagnosis['issues'].append(f"Error during diagnosis: {e}")
            diagnosis['recommendations'].append("Clear session and perform fresh login due to diagnosis errors")
        
        return diagnosis
    
    def get_session_info(self) -> Dict:
        """Get information about current session with enhanced diagnostics"""
        if not self.session_data:
            return {'exists': False}
        
        info = {
            'exists': True,
            'access_token_exists': bool(self.session_data.get('access_token')),
            'refresh_token_exists': bool(self.session_data.get('refresh_token')),
            'trade_token_exists': bool(self.session_data.get('trade_token')),
            'account_id': self.session_data.get('account_id'),
            'saved_at': self.session_data.get('saved_at'),
            'token_expire': self.session_data.get('token_expire')
        }
        
        # Calculate time until expiration
        token_expire = self.session_data.get('token_expire', '')
        if token_expire:
            try:
                expire_time = datetime.fromisoformat(token_expire.replace('+0000', '+00:00'))
                current_time = datetime.now(expire_time.tzinfo)
                time_until_expire = expire_time - current_time
                
                info['expires_in_minutes'] = int(time_until_expire.total_seconds() / 60)
                info['is_expired'] = time_until_expire.total_seconds() <= 0
                info['expires_soon'] = time_until_expire <= timedelta(minutes=self.EXPIRATION_WARNING_MINUTES)
                
            except ValueError:
                info['expires_in_minutes'] = None
                info['is_expired'] = None
                info['expires_soon'] = None
        
        return info
    
    def auto_manage_session(self, wb, force_refresh=False) -> bool:
        """
        Automatically manage session with proactive cleanup and better error handling
        
        Args:
            wb: Webull instance
            force_refresh: Force session refresh even if valid
            
        Returns:
            bool: True if valid session is available, False if new login required
        """
        try:
            # First, check and remove sessions that are expiring soon
            session_removed = self.remove_expiring_session()
            
            if session_removed:
                self.logger.info("Expiring session was removed - fresh login required")
                return False
            
            # Try to load existing session if not forcing refresh
            if not force_refresh:
                session_loaded = self.load_session(wb)
                if session_loaded:
                    # Check if session expires soon and try to refresh
                    session_info = self.get_session_info()
                    if session_info.get('expires_soon', False):
                        self.logger.info("Session expires soon - attempting refresh")
                        if self.refresh_session(wb):
                            self.logger.info("Session refreshed proactively due to upcoming expiration")
                            return True
                        else:
                            self.logger.warning("Failed to refresh expiring session - will need fresh login")
                            self.clear_session()
                            return False
                    else:
                        self.logger.info("Loaded existing valid session")
                        return True
                else:
                    # Session loading failed, check if we should try refresh
                    self.logger.info("Session loading failed")
                    
                    # Only try refresh if we have session data with a refresh token
                    if (self.session_data and 
                        self.session_data.get('refresh_token') and 
                        self.session_data.get('access_token')):
                        
                        self.logger.info("Have session data with refresh token - attempting refresh...")
                        
                        # Apply session data first for refresh attempt
                        wb._access_token = self.session_data.get('access_token', '')
                        wb._refresh_token = self.session_data.get('refresh_token', '')
                        wb._token_expire = self.session_data.get('token_expire', '')
                        wb._uuid = self.session_data.get('uuid', '')
                        
                        if self.refresh_session(wb):
                            self.logger.info("Successfully refreshed session after loading failure")
                            return True
                        else:
                            self.logger.warning("Refresh also failed - clearing session")
                            self.clear_session()
                    else:
                        self.logger.info("No valid session data for refresh attempt")
            
            # If we get here, no valid session is available
            self.logger.info("No valid session available - new login required")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in auto session management: {e}")
            # Clear potentially corrupted session data
            self.session_data = {}
            self.clear_session()
            return False
    
    def backup_session(self, backup_suffix=None) -> bool:
        """Create a backup of current session"""
        try:
            if not os.path.exists(self.session_file):
                self.logger.info("No session file to backup")
                return False
            
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_file = f"{self.session_file}.backup_{backup_suffix}"
            
            with open(self.session_file, 'r') as source:
                with open(backup_file, 'w') as backup:
                    backup.write(source.read())
            
            self.logger.info(f"Session backed up to {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up session: {e}")
            return False
    
    def cleanup_old_backups(self, max_age_days=7) -> int:
        """Clean up old session backup files"""
        try:
            cleaned = 0
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            # Look for backup files
            directory = os.path.dirname(self.session_file) or '.'
            filename_base = os.path.basename(self.session_file)
            
            for file in os.listdir(directory):
                if file.startswith(f"{filename_base}.backup_"):
                    file_path = os.path.join(directory, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        cleaned += 1
                        self.logger.debug(f"Cleaned up old backup: {file}")
            
            if cleaned > 0:
                self.logger.info(f"Cleaned up {cleaned} old session backups")
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
            return 0