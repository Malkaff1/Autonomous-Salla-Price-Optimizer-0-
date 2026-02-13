#!/usr/bin/env python3
"""
Fetch store information from Salla API and update database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from database.db import get_db
from database.models import Store, ActivityLog
from datetime import datetime

def fetch_and_update_store():
    """Fetch store info from Salla API and update database"""
    
    print("🔍 Fetching store information from Salla API...")
    
    with get_db() as db:
        # Get the store with None ID
        store = db.query(Store).filter(Store.store_id == 'None').first()
        
        if not store:
            print("❌ No store found with ID 'None'")
            return False
        
        if not store.access_token:
            print("❌ No access token found")
            return False
        
        print(f"✅ Found store with access token")
        
        try:
            # Fetch merchant/store information from Salla
            headers = {
                'Authorization': f'Bearer {store.access_token}',
                'Accept': 'application/json'
            }
            
            print("📡 Calling Salla API...")
            response = requests.get(
                'https://accounts.salla.sa/oauth2/user/info',
                headers=headers,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                return False
            
            response_data = response.json()
            print(f"✅ Received response: {response_data}")
            
            # Extract user data (may be nested under 'data' key)
            user_data = response_data.get('data', response_data)
            
            # Extract merchant information
            merchant = user_data.get('merchant', {})
            store_id = str(merchant.get('id', ''))
            store_name = merchant.get('name', 'Unknown Store')
            store_domain = merchant.get('domain', '')
            owner_email = user_data.get('email', '')
            owner_name = user_data.get('name', '')
            
            print(f"\n📦 Store Information:")
            print(f"  Store ID: {store_id}")
            print(f"  Store Name: {store_name}")
            print(f"  Domain: {store_domain}")
            print(f"  Owner: {owner_name}")
            print(f"  Email: {owner_email}")
            
            if not store_id:
                print("❌ Could not extract store ID from API response")
                return False
            
            # Update store record
            store.store_id = store_id
            store.store_name = store_name
            store.store_domain = store_domain
            store.owner_email = owner_email
            store.owner_name = owner_name
            store.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Log activity
            activity = ActivityLog(
                store_id=store_id,
                activity_type='store_info_updated',
                description='Store information fetched and updated',
                metadata={
                    'store_name': store_name,
                    'domain': store_domain
                }
            )
            db.add(activity)
            db.commit()
            
            print(f"\n✅ Store information updated successfully!")
            print(f"   Store ID: {store_id}")
            print(f"   Store Name: {store_name}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fetch_and_update_store()
    sys.exit(0 if success else 1)
