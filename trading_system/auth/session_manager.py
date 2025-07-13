# auth/session_manager.py
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class SessionManager:
    """Manages trading session persistence and token management"""
    
    def __init__(self, session_file="webull_session.json", logger=None):
        self.session_file = session_file
        self.logger = logger or logging.getLogger(__name__)
        self.session_data = {}
    
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
        """Load session data into webull instance"""
        try:
            if not os.path.exists(self.session_file):
                self.logger.info("No session file found")
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            self.session_data = session_data
            self.logger.debug(f"Loaded session data with keys: {list(session_data.keys())}")
            
            # Check if session is still valid
            if not self._is_session_valid(session_data):
                self.logger.info("Session expired or invalid")
                self.logger.info("Clearing invalid session file")
                self.clear_session()
                return False
            
            # Apply session data to webull instance
            wb._access_token = session_data.get('access_token', '')
            wb._refresh_token = session_data.get('refresh_token', '')
            wb._token_expire = session_data.get('token_expire', '')
            wb._uuid = session_data.get('uuid', '')
            wb._account_id = session_data.get('account_id', '')
            wb._trade_token = session_data.get('trade_token', '')
            wb.zone_var = session_data.get('zone_var', 'dc_core_r1')
            
            self.logger.info("Session loaded successfully")
            self.logger.debug(f"Set zone_var to: {wb.zone_var}")
            self.logger.debug(f"Set account_id to: {wb._account_id}")
            
            # IMPORTANT: Re-initialize account context to ensure proper API access
            # This is crucial for account discovery to work correctly
            try:
                self.logger.debug("Attempting to re-initialize account context...")
                account_id = wb.get_account_id()
                if account_id:
                    self.logger.info(f"Account context re-initialized: {account_id}")
                    return True
                else:
                    self.logger.warning("Failed to re-initialize account context - session may be expired")
                    self.logger.info("Clearing invalid session file")
                    self.clear_session()
                    return False
            except KeyError as e:
                self.logger.warning(f"API response missing expected field {e} - session likely expired")
                self.logger.info("Clearing invalid session file")
                self.clear_session()
                return False
            except Exception as e:
                self.logger.warning(f"Failed to re-initialize account context: {e} - session may be invalid")
                self.logger.info("Clearing invalid session file")
                self.clear_session()
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
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
                    # Parse the expiration time
                    expire_time = datetime.fromisoformat(token_expire.replace('+0000', '+00:00'))
                    current_time = datetime.now(expire_time.tzinfo)
                    
                    # Add 5 minute buffer
                    if expire_time <= current_time + timedelta(minutes=5):
                        self.logger.debug("Token is expired or expires soon")
                        return False
                        
                except ValueError as e:
                    self.logger.debug(f"Could not parse token expiration: {e}")
                    return False
            
            # Check session age - be more conservative
            saved_at = session_data.get('saved_at', '')
            if saved_at:
                try:
                    saved_time = datetime.fromisoformat(saved_at)
                    age = datetime.now() - saved_time
                    
                    # Sessions older than 12 hours are considered stale (reduced from 24)
                    if age > timedelta(hours=12):
                        self.logger.debug(f"Session is too old: {age.total_seconds()/3600:.1f} hours")
                        return False
                        
                except ValueError as e:
                    self.logger.debug(f"Could not parse saved time: {e}")
                    return False
            
            # Additional basic validation
            access_token = session_data.get('access_token', '')
            if not access_token or len(access_token) < 10:
                self.logger.debug("Access token appears invalid")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating session: {e}")
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
        """Refresh the session using refresh token - DISABLED DUE TO ERRORS"""
        try:
            self.logger.info("Session refresh requested but disabled due to errors")
            self.logger.info("Will attempt fresh login instead")
            
            # Instead of refreshing, we'll just return False so the system
            # falls back to fresh login
            return False
            
            # ORIGINAL CODE COMMENTED OUT:
            # self.logger.info("Attempting to refresh session...")
            # 
            # # Try to refresh login
            # result = wb.refresh_login()
            # 
            # if 'accessToken' in result and result['accessToken']:
            #     self.logger.info("✅ Session refreshed successfully")
            #     
            #     # Save the refreshed session
            #     self.save_session(wb)
            #     return True
            # else:
            #     self.logger.warning("❌ Failed to refresh session")
            #     return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in refresh session: {e}")
            return False
    
    def get_session_info(self) -> Dict:
        """Get information about current session"""
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
                
            except ValueError:
                info['expires_in_minutes'] = None
                info['is_expired'] = None
        
        return info
    
    def auto_manage_session(self, wb, force_refresh=False) -> bool:
        """Automatically manage session - load if valid, skip refresh due to errors"""
        try:
            # Try to load existing session first
            if not force_refresh and self.load_session(wb):
                self.logger.info("Loaded existing valid session")
                return True
            
            # Skip refresh functionality due to errors
            self.logger.info("Session refresh disabled - will require fresh login")
            self.logger.info("No valid session found - new login required")
            return False
            
            # ORIGINAL REFRESH CODE COMMENTED OUT:
            # # If no valid session, try to refresh if we have a refresh token
            # if self.session_data and self.session_data.get('refresh_token'):
            #     self.logger.info("Attempting to refresh session...")
            #     if self.refresh_session(wb):
            #         self.logger.info("Refreshed expired session")
            #         return True
            #     else:
            #         self.logger.warning("Session refresh failed")
            # 
            # # If refresh fails or no refresh token, need new login
            # self.logger.info("No valid session found - new login required")
            # return False
            
        except Exception as e:
            self.logger.error(f"Error in auto session management: {e}")
            # Clear potentially corrupted session data
            self.session_data = {}
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