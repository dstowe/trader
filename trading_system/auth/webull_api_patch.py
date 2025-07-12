# auth/webull_api_patch.py
"""
Patch for Webull API compatibility issues
Apply this patch to handle API response structure changes
"""

def patch_webull_get_account_id(wb):
    """
    Patch the get_account_id method to handle missing 'rzone' field
    
    Args:
        wb: webull instance to patch
    """
    
    def patched_get_account_id(id=0):
        """
        Patched version of get_account_id that handles missing 'rzone' field
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            headers = wb.build_req_headers()
            response = wb._session.get(wb._urls.account_id(), headers=headers, timeout=wb.timeout)
            result = response.json()
            
            if result.get('success') and len(result.get('data', [])) > 0:
                account_data = result['data'][int(id)]
                
                # Handle zone variable with multiple fallbacks
                zone_options = ['rzone', 'zone', 'zoneVar', 'zone_var']
                zone_value = 'dc_core_r001'  # Default fallback
                
                for zone_field in zone_options:
                    if zone_field in account_data:
                        zone_value = str(account_data[zone_field])
                        break
                
                wb.zone_var = zone_value
                wb._account_id = str(account_data['secAccountId'])
                
                logger.debug(f"Account ID: {wb._account_id}, Zone: {wb.zone_var}")
                return wb._account_id
            else:
                logger.warning(f"get_account_id failed: {result}")
                return None
                
        except KeyError as e:
            logger.warning(f"KeyError in get_account_id (field missing): {e}")
            # Try to extract what we can
            try:
                if result.get('success') and len(result.get('data', [])) > 0:
                    account_data = result['data'][int(id)]
                    if 'secAccountId' in account_data:
                        wb._account_id = str(account_data['secAccountId'])
                        wb.zone_var = 'dc_core_r001'  # Safe default
                        logger.info(f"Partial success - Account ID: {wb._account_id} (using default zone)")
                        return wb._account_id
            except:
                pass
            return None
        except Exception as e:
            logger.error(f"Error in get_account_id: {e}")
            return None
    
    # Replace the method
    wb.get_account_id = patched_get_account_id
    return wb

def apply_webull_patches(wb):
    """
    Apply all available patches to webull instance
    
    Args:
        wb: webull instance to patch
        
    Returns:
        wb: patched webull instance
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Apply get_account_id patch
        wb = patch_webull_get_account_id(wb)
        logger.info("✅ Applied get_account_id compatibility patch")
        
        # Add any future patches here
        
        return wb
        
    except Exception as e:
        logger.warning(f"⚠️  Could not apply webull patches: {e}")
        return wb

# Utility function to test if patches are needed
def test_webull_compatibility(wb):
    """
    Test if webull instance needs compatibility patches
    
    Args:
        wb: webull instance to test
        
    Returns:
        dict: Test results and recommendations
    """
    import logging
    logger = logging.getLogger(__name__)
    
    results = {
        'get_account_id_works': False,
        'needs_patches': True,
        'api_accessible': False,
        'issues': [],
        'recommendations': []
    }
    
    try:
        # Test basic API access
        headers = wb.build_req_headers()
        response = wb._session.get(wb._urls.account_id(), headers=headers, timeout=wb.timeout)
        
        if response.status_code == 200:
            results['api_accessible'] = True
            
            # Test get_account_id method
            try:
                account_id = wb.get_account_id()
                if account_id:
                    results['get_account_id_works'] = True
                    results['needs_patches'] = False
                    results['recommendations'].append("No patches needed - API working normally")
                else:
                    results['issues'].append("get_account_id returned None")
                    results['recommendations'].append("Apply get_account_id patch")
            except KeyError as e:
                results['issues'].append(f"KeyError in get_account_id: {e}")
                results['recommendations'].append("Apply get_account_id compatibility patch")
            except Exception as e:
                results['issues'].append(f"Exception in get_account_id: {e}")
                results['recommendations'].append("Apply get_account_id compatibility patch")
        else:
            results['issues'].append(f"API not accessible (HTTP {response.status_code})")
            results['recommendations'].append("Check authentication before applying patches")
            
    except Exception as e:
        results['issues'].append(f"Could not test API: {e}")
        results['recommendations'].append("Check network connectivity and authentication")
    
    return results