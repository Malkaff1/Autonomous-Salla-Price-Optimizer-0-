"""
Mock Salla API for testing the Price Optimizer system.
This provides fake responses that simulate the real Salla API.
"""

import json
import random
from typing import Dict, Any, List

class MockSallaAPI:
    """Mock implementation of Salla API for testing."""
    
    def __init__(self):
        self.products = {
            "بطاقة شحن سوا 100": {
                "id": "12345",
                "name": "بطاقة شحن سوا 100 ريال",
                "price": {"amount": 105.0, "currency": "SAR"},
                "cost_price": 95.0,
                "status": "active",
                "sku": "STC-100-SAR"
            },
            "iPhone 15 Pro": {
                "id": "67890",
                "name": "iPhone 15 Pro 256GB",
                "price": {"amount": 4299.0, "currency": "SAR"},
                "cost_price": 3800.0,
                "status": "active",
                "sku": "IPHONE-15-PRO-256"
            },
            "Samsung Galaxy S24": {
                "id": "11111",
                "name": "Samsung Galaxy S24 Ultra 512GB",
                "price": {"amount": 3999.0, "currency": "SAR"},
                "cost_price": 3500.0,
                "status": "active",
                "sku": "SAMSUNG-S24-ULTRA-512"
            }
        }
    
    def search_products(self, keyword: str) -> Dict[str, Any]:
        """Mock product search endpoint."""
        matching_products = []
        
        for product_name, product_data in self.products.items():
            if keyword.lower() in product_name.lower() or keyword.lower() in product_data["name"].lower():
                matching_products.append({
                    "id": product_data["id"],
                    "name": product_data["name"],
                    "price": product_data["price"],
                    "cost_price": product_data["cost_price"],
                    "status": product_data["status"],
                    "sku": product_data["sku"]
                })
        
        return {
            "status": 200,
            "success": True,
            "data": matching_products,
            "pagination": {
                "count": len(matching_products),
                "total": len(matching_products),
                "per_page": 15,
                "current_page": 1,
                "total_pages": 1
            }
        }
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Mock get single product endpoint."""
        for product_data in self.products.values():
            if product_data["id"] == product_id:
                return {
                    "status": 200,
                    "success": True,
                    "data": {
                        "id": product_data["id"],
                        "name": product_data["name"],
                        "price": product_data["price"],
                        "cost_price": product_data["cost_price"],
                        "status": product_data["status"],
                        "sku": product_data["sku"]
                    }
                }
        
        return {
            "status": 404,
            "success": False,
            "error": {"message": "Product not found"}
        }
    
    def update_product_price(self, product_id: str, new_price: float) -> Dict[str, Any]:
        """Mock update product price endpoint."""
        for product_data in self.products.values():
            if product_data["id"] == product_id:
                old_price = product_data["price"]["amount"]
                product_data["price"]["amount"] = new_price
                
                return {
                    "status": 200,
                    "success": True,
                    "data": {
                        "id": product_id,
                        "name": product_data["name"],
                        "old_price": old_price,
                        "new_price": new_price,
                        "updated_at": "2024-02-03T01:45:00Z"
                    }
                }
        
        return {
            "status": 404,
            "success": False,
            "error": {"message": "Product not found"}
        }

# Mock competitor data for testing
MOCK_COMPETITOR_DATA = {
    "بطاقة شحن سوا 100": [
        {"store_name": "Noon", "price": 102.0, "url": "https://noon.com/sawa-100", "is_valid": True},
        {"store_name": "Jarir", "price": 104.0, "url": "https://jarir.com/sawa-card-100", "is_valid": True},
        {"store_name": "Extra", "price": 103.5, "url": "https://extra.com/sawa-100-sar", "is_valid": True},
        {"store_name": "Amazon KSA", "price": 101.5, "url": "https://amazon.sa/sawa-recharge", "is_valid": True}
    ],
    "iPhone 15 Pro": [
        {"store_name": "Noon", "price": 4199.0, "url": "https://noon.com/iphone-15-pro", "is_valid": True},
        {"store_name": "Jarir", "price": 4250.0, "url": "https://jarir.com/iphone-15-pro-256", "is_valid": True},
        {"store_name": "Extra", "price": 4299.0, "url": "https://extra.com/iphone-15-pro", "is_valid": True},
        {"store_name": "Amazon KSA", "price": 4180.0, "url": "https://amazon.sa/iphone-15-pro", "is_valid": True}
    ]
}

def get_mock_competitor_data(product_name: str) -> List[Dict[str, Any]]:
    """Get mock competitor data for a product."""
    for mock_product, competitors in MOCK_COMPETITOR_DATA.items():
        if product_name.lower() in mock_product.lower() or mock_product.lower() in product_name.lower():
            return competitors
    
    # Return random competitor data if no specific match
    return [
        {"store_name": "Noon", "price": random.uniform(50, 500), "url": "https://noon.com/product", "is_valid": True},
        {"store_name": "Jarir", "price": random.uniform(50, 500), "url": "https://jarir.com/product", "is_valid": True},
        {"store_name": "Extra", "price": random.uniform(50, 500), "url": "https://extra.com/product", "is_valid": True}
    ]

# Example usage
if __name__ == "__main__":
    # Test the mock API
    mock_api = MockSallaAPI()
    
    # Test product search
    result = mock_api.search_products("بطاقة شحن سوا")
    print("Search result:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test price update
    update_result = mock_api.update_product_price("12345", 99.99)
    print("Update result:", json.dumps(update_result, indent=2, ensure_ascii=False))
    
    # Test competitor data
    competitors = get_mock_competitor_data("بطاقة شحن سوا 100")
    print("Competitors:", json.dumps(competitors, indent=2, ensure_ascii=False))