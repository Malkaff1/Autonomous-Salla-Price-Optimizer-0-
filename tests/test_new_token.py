#!/usr/bin/env python3
"""Test the new Salla token"""
import requests

# From your screenshot
ACCESS_TOKEN = "ory_at_UgSQcD9MTFUJ7--7N7lly9mlARsQjAg01muW54q87O4.VfNDbuUXHJuu2CsgqRcP2HJFaJdwp9B3D8RsxerCUE"

print("🧪 Testing Salla Token")
print("=" * 50)
print(f"Token: {ACCESS_TOKEN[:30]}...")
print()

try:
    # Test 1: Store Info
    print("📋 Test 1: Getting store info...")
    response = requests.get(
        'https://api.salla.dev/admin/v2/store/info',
        headers={'Authorization': f'Bearer {ACCESS_TOKEN}'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        store_name = data.get('data', {}).get('name', 'Unknown')
        store_id = data.get('data', {}).get('id', 'Unknown')
        print(f"✅ SUCCESS!")
        print(f"Store Name: {store_name}")
        print(f"Store ID: {store_id}")
        print()
        
        # Test 2: Get Products
        print("📦 Test 2: Getting products...")
        products_response = requests.get(
            'https://api.salla.dev/admin/v2/products',
            headers={'Authorization': f'Bearer {ACCESS_TOKEN}'},
            timeout=10
        )
        
        print(f"Status: {products_response.status_code}")
        
        if products_response.status_code == 200:
            products_data = products_response.json()
            products = products_data.get('data', [])
            print(f"✅ Found {len(products)} products")
            
            if products:
                print("\nFirst 3 products:")
                for i, product in enumerate(products[:3], 1):
                    print(f"{i}. {product.get('name')} - {product.get('price')} SAR")
        else:
            print(f"❌ Failed: {products_response.status_code}")
            
    elif response.status_code == 401:
        print("❌ Token expired or invalid")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("🎯 Token Test Complete")
