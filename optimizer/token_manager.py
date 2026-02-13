"""
OAuth Token Manager - Automated SaaS Edition
Handles proactive token refresh for all stores with error handling
"""

import requests
import logging
import os
from datetime import datetime, timedelta
from database.db import get_db
from database.models import Store, ActivityLog, SystemSetting

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages OAuth token refresh for stores with proactive monitoring"""
    
    TOKEN_URL = "https://accounts.salla.sa/oauth2/token"
    
    def __init__(self):
        """Initialize token manager with system credentials"""
        self.system_client_id = None
        self.system_client_secret = None
        self._load_system_credentials()
    
    def _load_system_credentials(self):
        """Load system-wide Salla credentials from database or environment"""
        try:
            with get_db() as db:
                # Try to get from system_settings table first
                client_id_setting = db.query(SystemSetting).filter(
                    SystemSetting.setting_key == 'SALLA_CLIENT_ID'
                ).first()
                
                client_secret_setting = db.query(SystemSetting).filter(
                    SystemSetting.setting_key == 'SALLA_CLIENT_SECRET'
                ).first()
                
                if client_id_setting and client_secret_setting:
                    self.system_client_id = client_id_setting.setting_value
                    self.system_client_secret = client_secret_setting.setting_value
                    logger.info("✅ Loaded system credentials from database")
                else:
                    # Fallback to environment variables
                    self.system_client_id = os.getenv('SALLA_CLIENT_ID')
                    self.system_client_secret = os.getenv('SALLA_CLIENT_SECRET')
                    logger.info("✅ Loaded system credentials from environment")
                    
        except Exception as e:
            logger.warning(f"Could not load from database, using environment: {e}")
            self.system_client_id = os.getenv('SALLA_CLIENT_ID')
            self.system_client_secret = os.getenv('SALLA_CLIENT_SECRET')

    
    def refresh_store_token(self, store_id: str, proactive: bool = False) -> bool:
        """
        Refresh OAuth token for a specific store
        
        Args:
            store_id: Salla store ID
            proactive: Whether this is a proactive refresh (before expiry)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db() as db:
                store = db.query(Store).filter(Store.store_id == store_id).first()
                
                if not store:
                    logger.error(f"Store {store_id} not found")
                    return False
                
                # Use store-specific credentials if available, otherwise use system credentials
                client_id = store.client_id or self.system_client_id
                client_secret = store.client_secret or self.system_client_secret
                
                if not client_id or not client_secret:
                    logger.error(f"No credentials available for store {store_id}")
                    return False
                
                # Prepare refresh request
                data = {
                    'grant_type': 'refresh_token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'refresh_token': store.refresh_token
                }
                
                refresh_type = "proactive" if proactive else "expired"
                logger.info(f"🔄 Refreshing token for store {store_id} ({refresh_type})")
                
                response = requests.post(self.TOKEN_URL, data=data, timeout=30)
                
                if response.status_code == 200:
                    token_data = response.json()
                    
                    new_access_token = token_data.get('access_token')
                    new_refresh_token = token_data.get('refresh_token', store.refresh_token)
                    expires_in = token_data.get('expires_in', 1209600)  # 14 days default
                    
                    # Update store
                    store.access_token = new_access_token
                    store.refresh_token = new_refresh_token
                    store.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    store.updated_at = datetime.utcnow()
                    
                    db.commit()
                    
                    # Log activity
                    activity = ActivityLog(
                        store_id=store_id,
                        activity_type='system_token_refresh',
                        description=f'System Action: OAuth token refreshed automatically ({refresh_type})',
                        activity_metadata={
                            'expires_in': expires_in,
                            'refresh_type': refresh_type,
                            'new_expiry': store.token_expires_at.isoformat()
                        }
                    )
                    db.add(activity)
                    db.commit()
                    
                    logger.info(f"✅ Token refreshed for store {store_id}")
                    return True
                    
                elif response.status_code == 401:
                    # Unauthorized - likely store uninstalled or revoked access
                    logger.error(f"❌ Token refresh unauthorized for store {store_id} - marking inactive")
                    self._deactivate_store(store, "Token refresh unauthorized - store may have uninstalled app")
                    return False
                    
                elif response.status_code == 400:
                    # Bad request - invalid refresh token
                    logger.error(f"❌ Invalid refresh token for store {store_id}")
                    self._deactivate_store(store, "Invalid refresh token")
                    return False
                    
                else:
                    logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                    return False
                    
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout refreshing token for store {store_id}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error refreshing token for store {store_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error refreshing token for store {store_id}: {e}")
            return False

    
    def _deactivate_store(self, store: Store, reason: str):
        """
        Deactivate a store and log the reason
        
        Args:
            store: Store object
            reason: Reason for deactivation
        """
        try:
            with get_db() as db:
                # Merge the store object into this session
                store = db.merge(store)
                
                store.is_active = False
                store.updated_at = datetime.utcnow()
                
                # Log activity
                activity = ActivityLog(
                    store_id=store.store_id,
                    activity_type='system_store_deactivated',
                    description=f'System Action: Store deactivated - {reason}',
                    activity_metadata={
                        'reason': reason,
                        'deactivated_at': datetime.utcnow().isoformat()
                    }
                )
                db.add(activity)
                db.commit()
                
                logger.warning(f"⚠️ Store {store.store_id} deactivated: {reason}")
                
        except Exception as e:
            logger.error(f"Error deactivating store {store.store_id}: {e}")
    
    def check_token_health(self, store_id: str) -> dict:
        """
        Check token health for a store
        
        Args:
            store_id: Salla store ID
            
        Returns:
            Dictionary with health status
        """
        try:
            with get_db() as db:
                store = db.query(Store).filter(Store.store_id == store_id).first()
                
                if not store:
                    return {'healthy': False, 'reason': 'Store not found'}
                
                if not store.is_active:
                    return {'healthy': False, 'reason': 'Store inactive'}
                
                # Check if token is expired
                if datetime.utcnow() >= store.token_expires_at:
                    return {'healthy': False, 'reason': 'Token expired', 'needs_refresh': True}
                
                # Check if token expires soon (within 24 hours)
                time_until_expiry = store.token_expires_at - datetime.utcnow()
                if time_until_expiry < timedelta(hours=24):
                    return {
                        'healthy': True,
                        'reason': 'Token expires soon',
                        'needs_refresh': True,
                        'hours_until_expiry': time_until_expiry.total_seconds() / 3600
                    }
                
                return {
                    'healthy': True,
                    'reason': 'Token valid',
                    'needs_refresh': False,
                    'hours_until_expiry': time_until_expiry.total_seconds() / 3600
                }
                
        except Exception as e:
            logger.error(f"Error checking token health for store {store_id}: {e}")
            return {'healthy': False, 'reason': f'Error: {str(e)}'}

    
    def refresh_all_expired_tokens(self) -> dict:
        """
        Proactively refresh tokens for all stores with expired or soon-to-expire tokens
        
        Returns:
            Dictionary with refresh statistics
        """
        try:
            with get_db() as db:
                # Get stores with tokens expiring in next 24 hours
                threshold = datetime.utcnow() + timedelta(hours=24)
                stores = db.query(Store).filter(
                    Store.is_active == True,
                    Store.token_expires_at < threshold
                ).all()
                
                logger.info(f"🔍 Found {len(stores)} stores with expiring tokens")
                
                refreshed = 0
                failed = 0
                deactivated = 0
                
                for store in stores:
                    # Check if token is already expired or will expire soon
                    is_proactive = store.token_expires_at > datetime.utcnow()
                    
                    if self.refresh_store_token(store.store_id, proactive=is_proactive):
                        refreshed += 1
                    else:
                        failed += 1
                        # Check if store was deactivated
                        db.refresh(store)
                        if not store.is_active:
                            deactivated += 1
                
                result = {
                    'total_checked': len(stores),
                    'refreshed': refreshed,
                    'failed': failed,
                    'deactivated': deactivated,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ Token refresh complete: {refreshed} refreshed, {failed} failed, {deactivated} deactivated")
                
                # Log system activity
                activity = ActivityLog(
                    store_id='SYSTEM',
                    activity_type='system_token_refresh_batch',
                    description=f'System Action: Batch token refresh completed',
                    activity_metadata=result
                )
                db.add(activity)
                db.commit()
                
                return result
                
        except Exception as e:
            logger.error(f"❌ Error in refresh_all_expired_tokens: {e}")
            return {
                'total_checked': 0,
                'refreshed': 0,
                'failed': 0,
                'deactivated': 0,
                'error': str(e)
            }
    
    def get_token_status_summary(self) -> dict:
        """
        Get summary of token status across all stores
        
        Returns:
            Dictionary with token status summary
        """
        try:
            with get_db() as db:
                total_stores = db.query(Store).count()
                active_stores = db.query(Store).filter(Store.is_active == True).count()
                
                # Tokens expiring in next 24 hours
                threshold_24h = datetime.utcnow() + timedelta(hours=24)
                expiring_soon = db.query(Store).filter(
                    Store.is_active == True,
                    Store.token_expires_at < threshold_24h
                ).count()
                
                # Already expired tokens
                expired = db.query(Store).filter(
                    Store.is_active == True,
                    Store.token_expires_at < datetime.utcnow()
                ).count()
                
                return {
                    'total_stores': total_stores,
                    'active_stores': active_stores,
                    'inactive_stores': total_stores - active_stores,
                    'tokens_expiring_soon': expiring_soon,
                    'tokens_expired': expired,
                    'healthy_tokens': active_stores - expiring_soon
                }
                
        except Exception as e:
            logger.error(f"Error getting token status summary: {e}")
            return {}
