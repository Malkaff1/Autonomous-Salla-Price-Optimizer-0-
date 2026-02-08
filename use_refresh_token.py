#!/usr/bin/env python3
"""Use refresh token to get new access token"""
import requests
from dotenv import set_key

# From your screenshot
CLIENT_ID = "30d2c6a1-36de-45e0-8fca-53219670db91"
CLIENT_SECRET = "8b7a9771a8c2b4e10be05f631577ed12dec396146a6290a3a2f54a8326e64a6f"
REFRESH_TOKEN = "ory_rt_wQSqhrkkHSbdmmHb9djzM6ChnDaYhbLGf69Mz1Hs2dY.sFQaEmcWcrOy9wxIG5RzfT3vM21_5xC8Vnf89_hpv3U"

print("🔄 Using Refresh Token to Get New Access Token")
print("=" * 50)
print()

token_url = "https://accounts.salla.sa/oauth2/token"

data = {
    'grant_type': 'refresh_token',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN
}

try:
    print("📤 Sending refresh token request...")
    response = requests.post(token_url, data=data, timeout=30)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        
        new_access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token', REFRESH_TOKEN)
        expires_in = token_data.get('expires_in', 0)
        
        print(f"\n🎉 SUCCESS!")
        print(f"New Access Token: {new_access_token}")
        print(f"New Refresh Token: {new_refresh_token}")
        print(f"Expires in: {expires_in} seconds ({expires_in//86400} days)")
        
        # Test the new token
        print(f"\n🧪 Testing new token...")
        test_response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {new_access_token}'},
            timeout=10
        )
        
        if test_response.status_code == 200:
            store_data = test_response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ Token works! Store: {store_name}")
            
            # Save to .env
            print(f"\n💾 Saving to .env...")
            set_key('.env', 'SALLA_ACCESS_TOKEN', new_access_token)
            set_key('.env', 'SALLA_REFRESH_TOKEN', new_refresh_token)
            set_key('.env', 'SALLA_CLIENT_ID', CLIENT_ID)
            set_key('.env', 'SALLA_CLIENT_SECRET', CLIENT_SECRET)
            print(f"✅ Saved!")
            
            print(f"\n🎯 All Done! You can now:")
            print(f"1. Run dashboard: streamlit run dashboard.py")
            print(f"2. Run optimizer: python main.py")
            
        else:
            print(f"❌ Token test failed: {test_response.status_code}")
            print(test_response.text)
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
