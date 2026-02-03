#!/usr/bin/env python3
"""
Quick Salla API Test - Direct Method
"""

import requests

# Your credentials
CLIENT_ID = "30d2c6a1-36de-45e0-8fca-53219670db91"
CLIENT_SECRET = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"

print("🔑 Quick Salla API Test")
print("=" * 40)
print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret: {CLIENT_SECRET[:20]}...")
print()

# Test 1: Use Client Secret as Bearer token
print("1. Testing Client Secret as Bearer token...")
headers = {
    'Authorization': f'Bearer {CLIENT_SECRET}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

try:
    response = requests.get('https://api.salla.dev/admin/v2/store/info', headers=headers, timeout=30)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS! Client Secret works as API token!")
        data = response.json()
        store_name = data.get('data', {}).get('name', 'Unknown')
        print(f"   Store: {store_name}")
        
        # Update .env file
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the token
        if 'SALLA_ACCESS_TOKEN=' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('SALLA_ACCESS_TOKEN='):
                    lines[i] = f'SALLA_ACCESS_TOKEN={CLIENT_SECRET}'
                    break
        else:
            lines = content.split('\n')
            lines.append(f'SALLA_ACCESS_TOKEN={CLIENT_SECRET}')
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("   ✅ Token updated in .env file!")
        print("\n🎯 Your price optimizer should now work!")
        print("   Test it with: python test_new_token.py")
        
    elif response.status_code == 401:
        print("   ❌ 401 Unauthorized - Token invalid")
        print(f"   Response: {response.text}")
    else:
        print(f"   ❌ Failed with status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 40)
print("If the test above failed, the issue is definitely with")
print("your Salla app configuration in the Partner Dashboard.")
print("\nYou need to:")
print("1. Make sure your app is 'Private App' type")
print("2. Enable products:read, products:write, store:read permissions")
print("3. Make sure your app is approved/active")
print("4. Install the app on your Salla store")