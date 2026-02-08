#!/usr/bin/env python3
"""
Simple Salla OAuth2 - Following Official Documentation
Based on: https://github.com/SallaApp/Salla-OAuth2-Client
"""

import requests
import webbrowser
from urllib.parse import urlencode
import os
from dotenv import load_dotenv, set_key

load_dotenv()

# Your app credentials
CLIENT_ID = "30d2c6a1-3cde-45e0-8fca-5319670daf91"
CLIENT_SECRET = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"
REDIRECT_URI = "http://localhost:8000/callback"

def get_authorization_url():
    """Step 1: Get authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'offline_access',  # Important: generates refresh token
        'state': 'random_state_123'
    }
    
    return f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"

def exchange_code_for_token(authorization_code):
    """Step 2: Exchange authorization code for access token"""
    
    token_url = "https://accounts.salla.sa/oauth2/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_merchant_info(access_token):
    """Step 3: Get merchant information"""
    
    try:
        response = requests.get(
            'https://accounts.salla.sa/oauth2/user/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get merchant info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main OAuth flow"""
    
    print("🔐 Salla OAuth2 - Simple Flow")
    print("=" * 50)
    print("Following official Salla documentation")
    print()
    
    # Step 1: Get authorization URL
    auth_url = get_authorization_url()
    
    print("📋 Step 1: Authorization")
    print(f"Opening: {auth_url}")
    print()
    
    webbrowser.open(auth_url)
    
    print("⏳ Please authorize the app in your browser...")
    print()
    print("After authorization, you'll be redirected to:")
    print("http://localhost:8000/callback?code=XXXXX")
    print()
    print("⚠️  If you see 'This site can't be reached', that's OK!")
    print("Just copy the 'code' parameter from the URL.")
    print()
    
    # Step 2: Get authorization code from user
    auth_code = input("📝 Paste the authorization code here: ").strip()
    
    if not auth_code:
        print("❌ No code provided!")
        return
    
    print(f"\n✅ Code received: {auth_code[:15]}...")
    
    # Step 3: Exchange code for token
    print("\n🔄 Step 2: Exchanging code for access token...")
    
    token_data = exchange_code_for_token(auth_code)
    
    if not token_data:
        print("❌ Failed to get token!")
        return
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in', 0)
    
    print(f"\n🎉 SUCCESS!")
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    print(f"Expires in: {expires_in} seconds ({expires_in//86400} days)")
    
    # Step 4: Get merchant info
    print(f"\n🔍 Step 3: Getting merchant information...")
    
    merchant_info = get_merchant_info(access_token)
    
    if merchant_info:
        print(f"\n✅ Merchant Info:")
        print(f"User ID: {merchant_info.get('id')}")
        print(f"Name: {merchant_info.get('name')}")
        print(f"Email: {merchant_info.get('email')}")
        
        merchant = merchant_info.get('merchant', {})
        print(f"\nStore Info:")
        print(f"Store ID: {merchant.get('id')}")
        print(f"Store Name: {merchant.get('name')}")
        print(f"Domain: {merchant.get('domain')}")
        print(f"Plan: {merchant.get('plan')}")
        print(f"Status: {merchant.get('status')}")
    
    # Step 5: Save to .env
    print(f"\n💾 Saving tokens to .env...")
    
    try:
        set_key('.env', 'SALLA_ACCESS_TOKEN', access_token)
        set_key('.env', 'SALLA_REFRESH_TOKEN', refresh_token)
        set_key('.env', 'SALLA_CLIENT_ID', CLIENT_ID)
        set_key('.env', 'SALLA_CLIENT_SECRET', CLIENT_SECRET)
        
        print(f"✅ Tokens saved to .env!")
        
    except Exception as e:
        print(f"⚠️  Could not update .env: {e}")
        print(f"\nPlease manually add to .env:")
        print(f"SALLA_ACCESS_TOKEN={access_token}")
        print(f"SALLA_REFRESH_TOKEN={refresh_token}")
    
    # Step 6: Test the token
    print(f"\n🧪 Testing token with Salla API...")
    
    try:
        response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        if response.status_code == 200:
            store_data = response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ API Test Successful!")
            print(f"Connected to store: {store_name}")
        else:
            print(f"⚠️  API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  API test error: {e}")
    
    print(f"\n🎯 All Done!")
    print(f"\nNext steps:")
    print(f"1. Run dashboard: streamlit run dashboard.py")
    print(f"2. Run optimizer: python main.py")

if __name__ == "__main__":
    main()
