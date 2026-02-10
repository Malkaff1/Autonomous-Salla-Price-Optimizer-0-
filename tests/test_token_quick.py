#!/usr/bin/env python3
"""Quick token test"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SALLA_ACCESS_TOKEN")
print(f"🔍 Testing token: {token[:20]}...")

try:
    response = requests.get(
        'https://api.salla.dev/admin/v2/store/info',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        store_name = data.get('data', {}).get('name', 'Unknown')
        print(f"✅ Token works! Store: {store_name}")
    elif response.status_code == 401:
        print("❌ Token expired or invalid")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
