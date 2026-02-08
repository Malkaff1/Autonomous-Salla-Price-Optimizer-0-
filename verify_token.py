#!/usr/bin/env python3
"""Verify the new Salla token"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SALLA_ACCESS_TOKEN")

print("🧪 Verifying Salla Token")
print("=" * 50)
print(f"Token: {token[:30]}...")
print()

try:
    # Test store info
    print("📋 Test 1: Store Info")
    response = requests.get(
        'https://api.salla.dev/admin/v2/store/info',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        store_name = data.get('data', {}).get('name', 'Unknown')
        store_id = data.get('data', {}).get('id', 'Unknown')
        print(f"✅ Store: {store_name} (ID: {store_id})")
        
        # Test products
        print(f"\n📦 Test 2: Products")
        products_response = requests.get(
            'https://api.salla.dev/admin/v2/products?per_page=5',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        
        print(f"Status: {products_response.status_code}")
        
        if products_response.status_code == 200:
            products_data = products_response.json()
            products = products_data.get('data', [])
            print(f"✅ Found {len(products)} products")
            
            if products:
                print("\nProducts:")
                for i, product in enumerate(products, 1):
                    print(f"{i}. {product.get('name')} - {product.get('price')} SAR (ID: {product.get('id')})")
                
                print(f"\n🎉 TOKEN IS WORKING!")
                print(f"✅ Ready to run the optimizer with real data")
            else:
                print("⚠️  No products found in store")
        else:
            print(f"❌ Products API failed: {products_response.status_code}")
            
    elif response.status_code == 401:
        print("❌ Token expired or invalid")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
