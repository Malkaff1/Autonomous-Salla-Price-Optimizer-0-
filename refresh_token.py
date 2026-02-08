#!/usr/bin/env python3
"""
Quick Salla Token Refresh with Correct Scopes
"""

import requests
import webbrowser
import time
from urllib.parse import urlencode
import os
from dotenv import load_dotenv, set_key

load_dotenv()

def refresh_salla_token():
    """Refresh Salla token with correct scopes."""
    
    print("🔄 Salla Token Refresh")
    print("=" * 40)
    
    # Use existing credentials from .env
    client_id = os.getenv("SALLA_CLIENT_ID", "30d2c6a1-3cde-45e0-8fca-5319670daf91")
    client_secret = os.getenv("SALLA_CLIENT_SECRET", "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c")
    
    print(f"✅ Using Client ID: {client_id}")
    print(f"✅ Using Client Secret: {client_secret[:20]}...")
    
    # Correct scopes that your app has permission for
    callback_url = "http://localhost:8000/callback"
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': 'offline_access',  # Use minimal scope that works
        'state': 'oauth_refresh_123'
    }
    
    auth_url = f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"
    
    print("\n🌐 Opening authorization URL...")
    print(f"URL: {auth_url}")
    print()
    
    # Open browser
    webbrowser.open(auth_url)
    time.sleep(2)
    
    print("📋 After authorization, you'll be redirected to:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE&state=oauth_refresh_123")
    print()
    print("⚠️  If you see 'This site can't be reached', that's normal!")
    print("Just copy the authorization code from the URL bar.")
    print()
    
    # Get authorization code
    auth_code = input("Enter the authorization code from the URL: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided!")
        return None
    
    print(f"✅ Authorization code received: {auth_code[:20]}...")
    
    # Exchange code for token
    print("\n🔄 Exchanging code for access token...")
    
    token_url = "https://accounts.salla.sa/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': callback_url
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        
        print(f"Token request status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        token_info = response.json()
        print(f"Token response keys: {list(token_info.keys())}")
        
        if 'access_token' not in token_info:
            print(f"❌ No access token in response: {token_info}")
            return None
        
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token', '')
        expires_in = token_info.get('expires_in', 3600)
        
        print(f"\n🎉 SUCCESS! New access token obtained!")
        print(f"Access Token: {access_token}")
        print(f"Expires In: {expires_in} seconds ({expires_in//3600} hours)")
        
        # Test the token
        print(f"\n🧪 Testing the new access token...")
        
        test_response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        print(f"Test request status: {test_response.status_code}")
        
        if test_response.status_code == 200:
            store_data = test_response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ Token works! Connected to store: {store_name}")
            
            # Update .env file
            try:
                set_key('.env', 'SALLA_ACCESS_TOKEN', access_token)
                if refresh_token:
                    set_key('.env', 'SALLA_REFRESH_TOKEN', refresh_token)
                set_key('.env', 'SALLA_CLIENT_ID', client_id)
                set_key('.env', 'SALLA_CLIENT_SECRET', client_secret)
                
                print(f"✅ .env file updated with working token!")
                return access_token
                
            except Exception as e:
                print(f"⚠️  Could not update .env: {e}")
                print(f"Please manually add: SALLA_ACCESS_TOKEN={access_token}")
                return access_token
        else:
            print(f"❌ Token test failed: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Salla Token Refresh with Correct Scopes")
    print("This uses the scopes your app actually has permission for.")
    print()
    
    token = refresh_salla_token()
    
    if token:
        print(f"\n🎯 Success! Your dashboard should now work.")
        print(f"Next steps:")
        print(f"1. Test dashboard: streamlit run dashboard_fixed.py")
        print(f"2. Run optimizer: python main.py")
    else:
        print(f"\n❌ Token refresh failed.")
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Make sure your Salla app has these permissions:")
        print(f"   - settings.read")
        print(f"   - products.read_write") 
        print(f"   - offline_access")
        print(f"2. Check that your app is installed in your store")
        print(f"3. Verify redirect URL: http://localhost:8000/callback")