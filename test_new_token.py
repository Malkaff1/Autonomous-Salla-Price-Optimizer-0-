#!/usr/bin/env python3
"""
Test the new Salla API token directly
"""

import requests
import json

def test_new_salla_token():
    """Test the new Salla token directly."""
    
    # Use the new token directly
    token = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"
    
    print("🧪 Testing New Salla API Token")
    print("=" * 50)
    print(f"Token: {token[:20]}...{token[-10:]}")
    print(f"Length: {len(token)} characters")
    
    # Test different endpoints
    test_endpoints = [
        {
            "name": "Store Info",
            "url": "https://api.salla.dev/admin/v2/store/info",
            "method": "GET"
        },
        {
            "name": "Products List",
            "url": "https://api.salla.dev/admin/v2/products",
            "method": "GET",
            "params": {"per_page": 1}
        },
        {
            "name": "Categories List", 
            "url": "https://api.salla.dev/admin/v2/categories",
            "method": "GET",
            "params": {"per_page": 1}
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'SallaBot/1.0'
    }
    
    success_count = 0
    
    for i, endpoint in enumerate(test_endpoints, 1):
        print(f"\n{i}. Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            response = requests.get(
                endpoint['url'],
                headers=headers,
                params=endpoint.get('params', {}),
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                
                # Show some data details
                if 'data' in data:
                    if isinstance(data['data'], list):
                        print(f"   📊 Found {len(data['data'])} items")
                    elif isinstance(data['data'], dict):
                        if 'name' in data['data']:
                            print(f"   🏪 Store: {data['data']['name']}")
                        if 'id' in data['data']:
                            print(f"   🆔 ID: {data['data']['id']}")
                
                success_count += 1
                
            elif response.status_code == 401:
                error_data = response.json() if response.content else {}
                print(f"   ❌ 401 Unauthorized: {error_data.get('error', {}).get('message', 'Unknown error')}")
                
            elif response.status_code == 403:
                print("   ❌ 403 Forbidden - Token lacks required permissions")
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text[:100]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{len(test_endpoints)} endpoints successful")
    
    if success_count > 0:
        print("🎉 Token is working! At least some endpoints are accessible.")
        return True
    else:
        print("❌ Token failed all tests. This might not be a valid access token.")
        print("\n💡 Possible Issues:")
        print("1. This might be a Client Secret, not an Access Token")
        print("2. Token might be expired or invalid")
        print("3. App might not be properly configured")
        print("4. Store might not have installed the app")
        return False

if __name__ == "__main__":
    test_new_salla_token()