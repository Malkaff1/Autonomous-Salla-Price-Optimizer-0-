#!/usr/bin/env python3
"""
Fixed Salla Token Refresh - Uses only the scopes your app has permission for
"""

import requests
import webbrowser
import time
from urllib.parse import urlencode
import os
from dotenv import load_dotenv, set_key

load_dotenv()

def fix_salla_token():
    """Get a new Salla token using only permitted scopes."""
    
    print("🔧 Salla Token Fix")
    print("=" * 40)
    print("This script uses ONLY the scopes your app has permission for.")
    print()
    
    # App credentials
    client_id = "30d2c6a1-3cde-45e0-8fca-5319670daf91"
    client_secret = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"
    callback_url = "http://localhost:8000/callback"
    
    print(f"✅ Client ID: {client_id}")
    
    # Use offline_access scope as per Salla documentation
    # This generates both access token and refresh token
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': 'offline_access',  # Required for refresh token
        'state': 'fix_token_123'
    }
    
    auth_url = f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"
    
    print("🌐 Opening authorization URL...")
    print(f"URL: {auth_url}")
    print()
    
    # Open browser
    webbrowser.open(auth_url)
    time.sleep(3)
    
    print("📋 After authorization, you'll be redirected to:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE")
    print()
    print("⚠️  If you see 'This site can't be reached', that's normal!")
    print("Just copy the authorization code from the URL.")
    print()
    
    # Get authorization code
    auth_code = input("📝 Enter the authorization code from the URL: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided!")
        return None
    
    print(f"✅ Code received: {auth_code[:15]}...")
    
    # Exchange code for token
    print("\n🔄 Getting access token...")
    
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
        
        print(f"Token response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        token_info = response.json()
        
        if 'access_token' not in token_info:
            print(f"❌ No access token: {token_info}")
            return None
        
        access_token = token_info['access_token']
        expires_in = token_info.get('expires_in', 3600)
        
        print(f"\n🎉 SUCCESS!")
        print(f"Access Token: {access_token}")
        print(f"Expires: {expires_in//3600} hours")
        
        # Test the token
        print(f"\n🧪 Testing token...")
        
        test_response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        if test_response.status_code == 200:
            store_data = test_response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ Token works! Store: {store_name}")
            
            # Update .env
            set_key('.env', 'SALLA_ACCESS_TOKEN', access_token)
            print(f"✅ .env updated!")
            return access_token
            
        else:
            print(f"❌ Token test failed: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Salla Token Fix")
    print("This fixes the OAuth scope error by using minimal permissions.")
    print()
    
    token = fix_salla_token()
    
    if token:
        print(f"\n🎯 Success! Next steps:")
        print(f"1. Test: python test_current_token.py")
        print(f"2. Dashboard: streamlit run dashboard_fixed.py")
        print(f"3. Optimizer: python main.py")
    else:
        print(f"\n❌ Failed. Check:")
        print(f"1. App is installed in your store")
        print(f"2. Redirect URL is: http://localhost:8000/callback")
        print(f"3. App has basic permissions")