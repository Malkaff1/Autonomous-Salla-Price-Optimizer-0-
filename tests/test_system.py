#!/usr/bin/env python3
"""Quick system test with real data"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SALLA_ACCESS_TOKEN")

print("🧪 Testing Complete System")
print("=" * 50)

# Test 1: Get products
print("\n📦 Step 1: Fetching products...")
response = requests.get(
    'https://api.salla.dev/admin/v2/products?per_page=3',
    headers={'Authorization': f'Bearer {token}'},
    timeout=10
)

if response.status_code == 200:
    products = response.json().get('data', [])
    print(f"✅ Found {len(products)} products")
    
    for i, product in enumerate(products, 1):
        price_data = product.get('price', {})
        if isinstance(price_data, dict):
            price = price_data.get('amount', 0)
        else:
            price = price_data
            
        print(f"\n{i}. {product.get('name')}")
        print(f"   ID: {product.get('id')}")
        print(f"   Price: {price} SAR")
        print(f"   Cost: {product.get('cost_price', 0)} SAR")
    
    print(f"\n✅ System is ready!")
    print(f"\nNext steps:")
    print(f"1. Run optimizer: python main.py")
    print(f"2. View dashboard: streamlit run dashboard.py")
    
else:
    print(f"❌ Failed: {response.status_code}")
