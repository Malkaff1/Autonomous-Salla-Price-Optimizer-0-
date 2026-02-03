#!/usr/bin/env python3
"""
Simple Salla OAuth2 Authorization
"""

import requests
import webbrowser
import time
from urllib.parse import urlencode

# Your Salla App Credentials
CLIENT_ID = "30d2c6a1-3cde-45e0-8fca-5319670daf91"
CLIENT_SECRET = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"

def get_salla_token():
    """Get Salla access token using OAuth2 flow."""
    
    print("🔐 Salla OAuth2 Authorization")
    print("=" * 50)
    print(f"Client ID: {CLIENT_ID}")
    print(f"Client Secret: {CLIENT_SECRET[:20]}...")
    print()
    
    # Step 1: Build authorization URL
    callback_url = "http://localhost:8000/callback"
    
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': callback_url,
        'scope': 'products:read products:write store:read',
        'state': 'oauth_state_123'
    }
    
    auth_url = f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"
    
    print("🌐 Step 1: Authorization URL Generated")
    print(f"URL: {auth_url}")
    print()
    
    # Step 2: Manual authorization
    print("📋 Step 2: Manual Authorization Required")
    print("1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Authorize your app")
    print("4. Copy the 'code' parameter from the callback URL")
    print()
    
    # Open browser automatically
    print("🌐 Opening browser...")
    webbrowser.open(auth_url)
    print()
    
    # Get authorization code from user
    print("After authorization, you'll be redirected to:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE&state=oauth_state_123")
    print()
    
    auth_code = input("Enter the authorization code from the URL: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided!")
        return None
    
    print(f"✅ Authorization code received: {auth_code[:20]}...")
    
    # Step 3: Exchange code for token
    print("\n🔄 Step 3: Exchanging code for access token...")
    
    token_url = "https://accounts.salla.sa/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': callback_url
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        
        print(f"Token request status: {response.status_code}")
        print(f"Token response: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        token_info = response.json()
        
        if 'access_token' not in token_info:
            print(f"❌ No access token in response: {token_info}")
            return None
        
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token', '')
        expires_in = token_info.get('expires_in', 3600)
        
        print(f"🎉 SUCCESS! Access token obtained!")
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        print(f"Expires In: {expires_in} seconds ({expires_in//3600} hours)")
        
        # Step 4: Test the token
        print(f"\n🧪 Step 4: Testing the access token...")
        
        test_response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        print(f"Test request status: {test_response.status_code}")
        print(f"Test response: {test_response.text[:200]}...")
        
        if test_response.status_code == 200:
            store_data = test_response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ Token works! Connected to store: {store_name}")
            
            # Update .env file
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                updated_lines = []
                token_updated = False
                
                for line in lines:
                    if line.startswith('SALLA_ACCESS_TOKEN='):
                        updated_lines.append(f'SALLA_ACCESS_TOKEN={access_token}\n')
                        token_updated = True
                    else:
                        updated_lines.append(line)
                
                if not token_updated:
                    updated_lines.append(f'SALLA_ACCESS_TOKEN={access_token}\n')
                
                with open('.env', 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
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
    print("🚀 Simple Salla OAuth2 Authorization")
    print("This script will help you get a working access token.")
    print()
    
    token = get_salla_token()
    
    if token:
        print(f"\n🎯 Success! Your price optimizer is now ready.")
        print(f"Next steps:")
        print(f"1. Test connection: python test_new_token.py")
        print(f"2. Run optimizer: python run_optimizer.py")
    else:
        print(f"\n❌ Authorization failed. Please check:")
        print(f"1. Your Client ID and Client Secret are correct")
        print(f"2. Your app is properly configured in Salla Partner Dashboard")
        print(f"3. Your app has the required permissions")
        print(f"4. Your store has installed the app")