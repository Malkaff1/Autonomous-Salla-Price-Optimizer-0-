#!/usr/bin/env python3
"""
Salla OAuth2 Scope Testing - Try Different Permission Formats
"""

import requests
import webbrowser
import time
from urllib.parse import urlencode

def test_different_scopes():
    """Test different scope formats that Salla might accept."""
    
    print("🔍 Salla OAuth2 Scope Testing")
    print("=" * 50)
    print("We'll try different permission formats to find what works.")
    print()
    
    # Get credentials
    client_id = input("Enter your Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return
    
    client_secret = input("Enter your Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return
    
    print(f"\n✅ Using credentials:")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:20]}...")
    print()
    
    # Different scope formats to try
    scope_variations = [
        # Standard format
        "products:read products:write store:read",
        
        # Alternative formats
        "product:read product:write store:read",
        "products.read products.write store.read",
        "product.read product.write store.read",
        
        # Minimal scopes
        "store:read",
        "products:read",
        "product:read",
        
        # Common e-commerce scopes
        "read_products write_products read_store",
        "products orders customers",
        
        # Try without products scope
        "store:read orders:read",
        
        # Empty scope (basic access)
        "",
        
        # All possible variations
        "admin:read admin:write",
        "merchant:read merchant:write",
        "api:read api:write"
    ]
    
    callback_url = "http://localhost:8000/callback"
    
    for i, scope in enumerate(scope_variations, 1):
        print(f"\n🧪 Test {i}: Trying scope: '{scope}'")
        
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': callback_url,
            'scope': scope,
            'state': f'test_{i}'
        }
        
        auth_url = f"https://accounts.salla.sa/oauth2/auth?{urlencode(params)}"
        
        print(f"URL: {auth_url}")
        print(f"Opening browser...")
        
        webbrowser.open(auth_url)
        
        print(f"Check your browser. If authorization works, you'll see a different URL.")
        print(f"If you see the same 'invalid_scope' error, we'll try the next one.")
        
        choice = input(f"Did this scope work? (y/n/skip): ").strip().lower()
        
        if choice == 'y':
            print(f"🎉 SUCCESS! Working scope found: '{scope}'")
            
            # Get the authorization code
            auth_code = input("Enter the authorization code from the URL: ").strip()
            
            if auth_code:
                # Try to exchange for token
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
                    
                    if response.status_code == 200:
                        token_info = response.json()
                        if 'access_token' in token_info:
                            access_token = token_info['access_token']
                            print(f"🎉 ACCESS TOKEN OBTAINED!")
                            print(f"Token: {access_token}")
                            
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
                                
                                print(f"✅ Token saved to .env file!")
                                print(f"✅ Working scope: '{scope}'")
                                return True
                                
                            except Exception as e:
                                print(f"⚠️  Could not update .env: {e}")
                                print(f"Manual token: {access_token}")
                                return True
                        
                    else:
                        print(f"❌ Token exchange failed: {response.status_code}")
                        print(f"Response: {response.text}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            return True
            
        elif choice == 'skip':
            print("Skipping remaining tests...")
            break
        else:
            print("Trying next scope...")
            time.sleep(2)
    
    print(f"\n❌ None of the scope variations worked.")
    print(f"This suggests there might be an issue with:")
    print(f"1. Your app configuration in Salla Partner Dashboard")
    print(f"2. Your app might not be approved/active")
    print(f"3. Your store might not have installed the app")
    
    return False

if __name__ == "__main__":
    print("🔍 Salla OAuth2 Scope Tester")
    print("This will try different permission formats to find what works.")
    print()
    
    success = test_different_scopes()
    
    if success:
        print(f"\n🎯 Success! You can now test your connection:")
        print(f"python test_new_token.py")
    else:
        print(f"\n🔧 Next steps:")
        print(f"1. Double-check your app in Salla Partner Dashboard")
        print(f"2. Make sure your app is approved and active")
        print(f"3. Verify your store has installed the app")
        print(f"4. Try creating a completely new app")