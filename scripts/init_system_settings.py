#!/usr/bin/env python3
"""
Initialize System Settings in Database
Stores system-wide Salla credentials in database for zero-.env dependency
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db
from database.models import SystemSetting
from dotenv import load_dotenv

load_dotenv()


def init_system_settings():
    """Initialize system settings from environment variables"""
    
    print("🔧 Initializing system settings...")
    
    # Get credentials from environment
    client_id = os.getenv('SALLA_CLIENT_ID')
    client_secret = os.getenv('SALLA_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: SALLA_CLIENT_ID and SALLA_CLIENT_SECRET must be set in .env")
        return False
    
    try:
        with get_db() as db:
            # Store SALLA_CLIENT_ID
            client_id_setting = db.query(SystemSetting).filter(
                SystemSetting.setting_key == 'SALLA_CLIENT_ID'
            ).first()
            
            if client_id_setting:
                client_id_setting.setting_value = client_id
                client_id_setting.updated_at = None  # Will be set by onupdate
                print("✅ Updated SALLA_CLIENT_ID")
            else:
                client_id_setting = SystemSetting(
                    setting_key='SALLA_CLIENT_ID',
                    setting_value=client_id,
                    description='System-wide Salla OAuth Client ID'
                )
                db.add(client_id_setting)
                print("✅ Created SALLA_CLIENT_ID")
            
            # Store SALLA_CLIENT_SECRET
            client_secret_setting = db.query(SystemSetting).filter(
                SystemSetting.setting_key == 'SALLA_CLIENT_SECRET'
            ).first()
            
            if client_secret_setting:
                client_secret_setting.setting_value = client_secret
                client_secret_setting.updated_at = None
                print("✅ Updated SALLA_CLIENT_SECRET")
            else:
                client_secret_setting = SystemSetting(
                    setting_key='SALLA_CLIENT_SECRET',
                    setting_value=client_secret,
                    description='System-wide Salla OAuth Client Secret'
                )
                db.add(client_secret_setting)
                print("✅ Created SALLA_CLIENT_SECRET")
            
            db.commit()
            
            print("\n🎉 System settings initialized successfully!")
            print("✅ Credentials are now stored in database")
            print("✅ No user-specific tokens in .env file")
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing system settings: {e}")
        return False


if __name__ == "__main__":
    success = init_system_settings()
    sys.exit(0 if success else 1)
