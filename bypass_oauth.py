#!/usr/bin/env python3
"""
Bypass OAuth - Use Direct API Key Method
Some Salla integrations work with direct API keys instead of OAuth tokens.
"""

import requests
import json

def test_direct_api_access():
    """Test if we can access Salla API with direct credentials."""
    
    print("🔑 Direct Salla API Access Test")
    print("=" * 50)
    print("Let's try accessing Salla API with different authentication methods.")
    print()
    
    # Get credentials
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    print(f"\n🧪 Testing different authentication methods...")
    
    # Method 1: Try using Client Secret as API Key
    print(f"\n1. Testing Client Secret as API Key...")
    headers1 = {
        'Authorization': f'Bearer {client_secret}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response1 = requests.get('https://api.salla.dev/admin/v2/store/info', headers=headers1, timeout=30)
        print(f"   Status: {response1.status_code}")
        if response1.status_code == 200:
            print("   ✅ SUCCESS! Client Secret works as API key!")
            store_data = response1.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"   Store: {store_name}")
            
            # Update .env file
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                updated_lines = []
                token_updated = False
                
                for line in lines:
                    if line.startswith('SALLA_ACCESS_TOKEN='):
                        updated_lines.append(f'SALLA_ACCESS_TOKEN={client_secret}\n')
                        token_updated = True
                    else:
                        updated_lines.append(line)
                
                if not token_updated:
                    updated_lines.append(f'SALLA_ACCESS_TOKEN={client_secret}\n')
                
                with open('.env', 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                
                print(f"   ✅ Token saved to .env file!")
                return True
                
            except Exception as e:
                print(f"   ⚠️  Could not update .env: {e}")
                return True
        else:
            print(f"   ❌ Failed: {response1.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 2: Try Basic Auth
    print(f"\n2. Testing Basic Authentication...")
    try:
        response2 = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            auth=(client_id, client_secret),
            headers={'Accept': 'application/json'},
            timeout=30
        )
        print(f"   Status: {response2.status_code}")
        if response2.status_code == 200:
            print("   ✅ SUCCESS! Basic auth works!")
            return True
        else:
            print(f"   ❌ Failed: {response2.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 3: Try API Key in header
    print(f"\n3. Testing API Key in X-API-KEY header...")
    headers3 = {
        'X-API-KEY': client_secret,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response3 = requests.get('https://api.salla.dev/admin/v2/store/info', headers=headers3, timeout=30)
        print(f"   Status: {response3.status_code}")
        if response3.status_code == 200:
            print("   ✅ SUCCESS! X-API-KEY works!")
            return True
        else:
            print(f"   ❌ Failed: {response3.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 4: Try different endpoints
    print(f"\n4. Testing public endpoints...")
    try:
        response4 = requests.get('https://api.salla.dev/admin/v2/categories', headers=headers1, timeout=30)
        print(f"   Categories endpoint status: {response4.status_code}")
        if response4.status_code == 200:
            print("   ✅ Categories endpoint works!")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n❌ All authentication methods failed.")
    print(f"\n💡 This confirms the issue is with your Salla app configuration.")
    print(f"The app exists but doesn't have proper API access permissions.")
    
    return False

def show_salla_app_fix_guide():
    """Show detailed guide to fix Salla app configuration."""
    
    print(f"\n🔧 How to Fix Your Salla App Configuration")
    print(f"=" * 60)
    
    print(f"\n1. 🌐 Go to Salla Partner Dashboard:")
    print(f"   https://salla.dev")
    
    print(f"\n2. 📱 Check Your App Status:")
    print(f"   - Login → My Apps → Find your app")
    print(f"   - Status should be 'Active' or 'Approved'")
    print(f"   - If it says 'Draft' or 'Pending', submit for approval")
    
    print(f"\n3. 🔑 Verify App Type:")
    print(f"   - App Type should be 'Private App' or 'Internal App'")
    print(f"   - NOT 'Public App' (public apps have limited permissions)")
    
    print(f"\n4. ✅ Check Permissions/Scopes:")
    print(f"   Look for 'Permissions', 'Scopes', or 'API Access' section")
    print(f"   Enable these permissions:")
    print(f"   - ✅ products:read")
    print(f"   - ✅ products:write") 
    print(f"   - ✅ store:read")
    
    print(f"\n5. 🏪 Install App on Your Store:")
    print(f"   - Go to your Salla store admin panel")
    print(f"   - Apps → App Store → My Apps")
    print(f"   - Find your app and click 'Install'")
    print(f"   - Grant all requested permissions")
    
    print(f"\n6. 🔄 Alternative: Create New App")
    print(f"   If the above doesn't work, create a completely new app:")
    print(f"   - Use 'Private App' type from the start")
    print(f"   - Enable all required permissions during creation")
    print(f"   - Install it on your store immediately")
    
    print(f"\n7. 📞 Contact Salla Support:")
    print(f"   If nothing works, contact Salla developer support:")
    print(f"   - Email: developers@salla.sa")
    print(f"   - Tell them your app can't access products:read scope")

if __name__ == "__main__":
    print("🔑 Salla API Direct Access Tester")
    print("Let's try different ways to access your Salla store.")
    print()
    
    success = test_direct_api_access()
    
    if success:
        print(f"\n🎉 SUCCESS! Your API access is working!")
        print(f"You can now test your price optimizer:")
        print(f"python test_new_token.py")
    else:
        show_salla_app_fix_guide()