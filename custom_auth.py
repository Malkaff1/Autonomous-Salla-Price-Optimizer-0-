#!/usr/bin/env python3
"""
Custom Salla OAuth2 Authorization - Enter Your Own Credentials
"""

import requests
import webbrowser
import time
from urllib.parse import urlencode

def get_salla_token_custom():
    """Get Salla access token using your own credentials."""
    
    print("🔐 Custom Salla OAuth2 Authorization")
    print("=" * 50)
    print("You need to get your credentials from Salla Partner Dashboard:")
    print("1. Go to: https://salla.dev")
    print("2. Login → My Apps → Your App → View Details")
    print("3. Copy both Client ID and Client Secret")
    print()
    
    # Get credentials from user
    client_id = input("Enter your Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return None
    
    client_secret = input("Enter your Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return None
    
    print(f"\n✅ Using credentials:")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:20]}...")
    print()
    
    # Step 1: Build authorization URL
    callback_url = "http://localhost:8000/callback"
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': 'products:read products:write store:read',
        'state': 'oauth_state_123'
    }
    
    auth_url = f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"
    
    print("🌐 Step 1: Authorization URL Generated")
    print(f"URL: {auth_url}")
    print()
    
    # Step 2: Manual authorization
    print("📋 Step 2: Manual Authorization")
    print("1. Opening browser automatically...")
    print("2. Authorize your app on the Salla page")
    print("3. Copy the 'code' parameter from the callback URL")
    print()
    
    # Open browser automatically
    print("🌐 Opening browser...")
    webbrowser.open(auth_url)
    time.sleep(3)
    print()
    
    # Get authorization code from user
    print("After authorization, you'll be redirected to:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE&state=oauth_state_123")
    print()
    print("If you see 'This site can't be reached', that's normal!")
    print("Just copy the authorization code from the URL bar.")
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
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': callback_url
    }
    
    try:
        print("Making token request...")
        response = requests.post(token_url, data=token_data, timeout=30)
        
        print(f"Token request status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to parse error
            try:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                print(f"Error details: {error_msg}")
            except:
                pass
            
            return None
        
        token_info = response.json()
        print(f"Token response: {token_info}")
        
        if 'access_token' not in token_info:
            print(f"❌ No access token in response: {token_info}")
            return None
        
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token', '')
        expires_in = token_info.get('expires_in', 3600)
        
        print(f"\n🎉 SUCCESS! Access token obtained!")
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
                
                # Add refresh token and client credentials for future use
                updated_lines.append(f'SALLA_REFRESH_TOKEN={refresh_token}\n')
                updated_lines.append(f'SALLA_CLIENT_ID={client_id}\n')
                updated_lines.append(f'SALLA_CLIENT_SECRET={client_secret}\n')
                
                with open('.env', 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
                print(f"✅ .env file updated with working token and credentials!")
                return access_token
                
            except Exception as e:
                print(f"⚠️  Could not update .env: {e}")
                print(f"Please manually add: SALLA_ACCESS_TOKEN={access_token}")
                return access_token
        else:
            print(f"❌ Token test failed: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            
            # Still save the token even if test fails
            print(f"💾 Saving token anyway - it might work for your specific use case")
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
                
                print(f"✅ Token saved to .env file")
                return access_token
                
            except Exception as e:
                print(f"⚠️  Could not update .env: {e}")
                return access_token
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Custom Salla OAuth2 Authorization")
    print("This script uses YOUR credentials from Salla Partner Dashboard.")
    print()
    
    token = get_salla_token_custom()
    
    if token:
        print(f"\n🎯 Success! Your price optimizer is now ready.")
        print(f"Next steps:")
        print(f"1. Test connection: python test_new_token.py")
        print(f"2. Run optimizer: python run_optimizer.py")
    else:
        print(f"\n❌ Authorization failed.")
        print(f"\n🔧 Troubleshooting Steps:")
        print(f"1. Go to https://salla.dev and login")
        print(f"2. Create a new app if you haven't already")
        print(f"3. Make sure your app has these permissions:")
        print(f"   - products:read")
        print(f"   - products:write") 
        print(f"   - store:read")
        print(f"4. Set redirect URL to: http://localhost:8000/callback")
        print(f"5. Make sure your store has installed the app")