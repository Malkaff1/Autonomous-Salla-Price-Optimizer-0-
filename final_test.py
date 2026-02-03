#!/usr/bin/env python3
"""
Final Salla API Test - Comprehensive Debugging
"""

import requests
import json
from dotenv import load_dotenv
import os

def comprehensive_salla_test():
    """Comprehensive test of Salla API with detailed debugging."""
    
    load_dotenv()
    
    print("🔍 Comprehensive Salla API Test")
    print("=" * 50)
    
    # Get token from .env
    token = os.getenv('SALLA_ACCESS_TOKEN')
    print(f"Token from .env: {token[:20]}...{token[-10:] if token else 'None'}")
    print(f"Token length: {len(token) if token else 0}")
    print()
    
    if not token:
        print("❌ No token found in .env file")
        return False
    
    # Test different API endpoints and methods
    test_cases = [
        {
            "name": "Store Info",
            "url": "https://api.salla.dev/admin/v2/store/info",
            "method": "GET"
        },
        {
            "name": "Products (with new scope format)",
            "url": "https://api.salla.dev/admin/v2/products",
            "method": "GET",
            "params": {"per_page": 1}
        },
        {
            "name": "Categories",
            "url": "https://api.salla.dev/admin/v2/categories", 
            "method": "GET",
            "params": {"per_page": 1}
        },
        {
            "name": "Settings (new scope)",
            "url": "https://api.salla.dev/admin/v2/settings",
            "method": "GET"
        }
    ]
    
    # Different header formats to try
    header_formats = [
        {
            "name": "Standard Bearer",
            "headers": {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        },
        {
            "name": "Bearer with User-Agent",
            "headers": {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'SallaBot/1.0'
            }
        },
        {
            "name": "X-API-KEY format",
            "headers": {
                'X-API-KEY': token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        
        for header_format in header_formats:
            print(f"\n   📋 Header format: {header_format['name']}")
            
            try:
                response = requests.get(
                    test_case['url'],
                    headers=header_format['headers'],
                    params=test_case.get('params', {}),
                    timeout=30
                )
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("      ✅ SUCCESS!")
                    try:
                        data = response.json()
                        if 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"      📊 Found {len(data['data'])} items")
                            elif isinstance(data['data'], dict):
                                if 'name' in data['data']:
                                    print(f"      🏪 Store: {data['data']['name']}")
                                if 'id' in data['data']:
                                    print(f"      🆔 ID: {data['data']['id']}")
                        print(f"      📄 Sample data: {str(data)[:100]}...")
                    except:
                        print(f"      📄 Response: {response.text[:100]}...")
                    
                    success_count += 1
                    
                    # If we found a working combination, save it
                    print(f"\n🎉 WORKING COMBINATION FOUND!")
                    print(f"   Endpoint: {test_case['name']}")
                    print(f"   Headers: {header_format['name']}")
                    print(f"   This proves your token is valid!")
                    
                    return True
                    
                elif response.status_code == 401:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                        print(f"      ❌ 401: {error_msg}")
                    except:
                        print(f"      ❌ 401: Unauthorized")
                        
                elif response.status_code == 403:
                    print(f"      ❌ 403: Forbidden - Check permissions")
                    
                else:
                    print(f"      ❌ {response.status_code}: {response.text[:50]}...")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        print(f"   " + "-" * 40)
    
    print(f"\n" + "=" * 50)
    print(f"📊 Test Results: {success_count} successful requests")
    
    if success_count == 0:
        print(f"\n❌ All tests failed. Possible issues:")
        print(f"1. Token is not a valid access token")
        print(f"2. Token has expired")
        print(f"3. App permissions are still not correct")
        print(f"4. Store hasn't installed the app")
        print(f"5. Salla API endpoint URLs have changed")
        
        print(f"\n🔧 Debugging info:")
        print(f"   Token format: {'Valid hex' if all(c in '0123456789abcdef' for c in token.lower()) else 'Not hex'}")
        print(f"   Token length: {len(token)} chars")
        
        # Try to decode if it looks like base64 or JWT
        if '.' in token:
            print(f"   Token type: Looks like JWT (has dots)")
        elif len(token) == 64:
            print(f"   Token type: Looks like hex API key")
        else:
            print(f"   Token type: Unknown format")
            
        return False
    else:
        return True

if __name__ == "__main__":
    print("🔍 Final Salla API Comprehensive Test")
    print("This will test every possible combination to find what works.")
    print()
    
    success = comprehensive_salla_test()
    
    if success:
        print(f"\n🎯 SUCCESS! Your Salla API is working!")
        print(f"You can now run your price optimizer:")
        print(f"python run_optimizer.py")
    else:
        print(f"\n💡 Next steps:")
        print(f"1. Double-check that you completed the OAuth flow correctly")
        print(f"2. Verify the authorization code was exchanged for an access token")
        print(f"3. Make sure your app is installed on your Salla store")
        print(f"4. Contact Salla support if the issue persists")