"""
OAuth Token Manager
Handles token refresh for all stores
"""

import requests
import logging
from datetime import datetime, timedelta
from database.db import get_db
from database.models import Store, ActivityLog

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages OAuth token refresh for stores"""
    
    TOKEN_URL = "https://accounts.salla.sa/oauth2/token"
    
    def refresh_store_token(self, store_id: str) -> bool:
        """
        Refresh OAuth token for a specific store
        
        Args:
            store_id: Salla store ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db() as db:
                store = db.query(Store).filter(Store.store_id == store_id).first()
                
                if not store:
                    logger.error(f"Store {store_id} not found")
                    return False
                
                # Prepare refresh request
                data = {
                    'grant_type': 'refresh_token',
                    'client_id': store.client_id,
                    'client_secret': store.client_secret,
                    'refresh_token': store.refresh_token
                }
                
                logger.info(f"🔄 Refreshing token for store {store_id}")
                
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
                        activity_type='token_refreshed',
                        description='OAuth token refreshed successfully',
                        metadata={'expires_in': expires_in}
                    )
                    db.add(activity)
                    db.commit()
                    
                    logger.info(f"✅ Token refreshed for store {store_id}")
                    return True
                else:
                    logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error refreshing token for store {store_id}: {e}")
            return False
    
    def refresh_all_expired_tokens(self):
        """Refresh tokens for all stores with expired or soon-to-expire tokens"""
        try:
            with get_db() as db:
                # Get stores with tokens expiring in next 24 hours
                threshold = datetime.utcnow() + timedelta(hours=24)
                stores = db.query(Store).filter(
                    Store.is_active == True,
                    Store.token_expires_at < threshold
                ).all()
                
                logger.info(f"Found {len(stores)} stores with expiring tokens")
                
                refreshed = 0
                failed = 0
                
                for store in stores:
                    if self.refresh_store_token(store.store_id):
                        refreshed += 1
                    else:
                        failed += 1
                
                logger.info(f"✅ Refreshed {refreshed} tokens, {failed} failed")
                
                return {"refreshed": refreshed, "failed": failed}
                
        except Exception as e:
            logger.error(f"Error in refresh_all_expired_tokens: {e}")
            return {"refreshed": 0, "failed": 0}
