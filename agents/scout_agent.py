import os
import requests
import json
import time
import logging
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai_tools import TavilySearchTool 
from dotenv import load_dotenv

# Import the fashion market search tool
from tools.market_search import fashion_market_search

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class CompetitorPrice(BaseModel):
    store_name: str = Field(..., description="Name of the competitor store")
    price: float = Field(..., description="Product price in SAR")
    url: str = Field(..., description="URL to the product page")
    is_valid: bool = Field(default=True, description="Whether this price is considered valid")

class ExtractedProductPrices(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    product_id: str = Field(..., description="Salla product ID for API updates")
    internal_price: float = Field(..., description="Current price in our Salla store")
    cost_price: float = Field(..., description="Cost price of the product")
    competitors: List[CompetitorPrice] = Field(..., description="List of competitor prices")

# Environment setup
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
output_dir = "./ai-agent-output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

basic_llm = LLM(model="gpt-4o", temperature=0)
search_tool = TavilySearchTool(max_results=10)

@tool("salla_inventory_discovery")
def salla_inventory_discovery():
    """Discover all products in the Salla store dynamically."""
    token = os.getenv("SALLA_ACCESS_TOKEN")
    
    if not token:
        logger.error("No Salla access token found")
        return {
            "products": [],
            "error": "No access token configured"
        }
    
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.salla.dev/admin/v2/products"
    params = {"per_page": 20, "page": 1}  # Get top 20 products
    
    try:
        logger.info("🔍 Discovering products in Salla store...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            products = []
            for product in data['data'][:5]:  # Top 5 products
                try:
                    # Safely extract price and cost with fallbacks
                    price_data = product.get('price', {})
                    if isinstance(price_data, dict):
                        price_amount = price_data.get('amount', 0)
                    else:
                        price_amount = price_data or 0
                    
                    # Convert to float safely
                    try:
                        price = float(price_amount) if price_amount else 0.0
                    except (ValueError, TypeError):
                        price = 0.0
                    
                    # Safely extract cost price
                    cost_price = product.get('cost_price', 0)
                    try:
                        cost = float(cost_price) if cost_price else 0.0
                    except (ValueError, TypeError):
                        cost = 0.0
                    
                    product_info = {
                        "product_id": str(product.get('id', '')),
                        "name": product.get('name', 'Unknown Product'),
                        "price": price,
                        "cost": cost,
                        "category": product.get('category', {}).get('name', 'Fashion') if product.get('category') else 'Fashion',
                        "status": product.get('status', 'active'),
                        "sku": product.get('sku', ''),
                        "description": product.get('description', '')[:100] if product.get('description') else ''
                    }
                    
                    # Only add products with valid prices
                    if price > 0:
                        products.append(product_info)
                        logger.info(f"📦 Found product: {product_info['name']} - {product_info['price']} SAR")
                    else:
                        logger.warning(f"⚠️ Skipping product with invalid price: {product.get('name', 'Unknown')}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error processing product {product.get('name', 'Unknown')}: {str(e)}")
                    continue
            
            logger.info(f"✅ Successfully discovered {len(products)} products from store")
            return {
                "products": products,
                "total_found": len(data['data']),
                "store_connected": True
            }
        else:
            logger.warning("No products found in Salla store")
            return {
                "products": [],
                "total_found": 0,
                "store_connected": True,
                "note": "Store is empty or no products match criteria"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Salla API request failed: {str(e)}")
        return {
            "products": [],
            "error": f"API Error: {str(e)}",
            "store_connected": False
        }
    except Exception as e:
        logger.error(f"Unexpected error in product discovery: {str(e)}")
        return {
            "products": [],
            "error": f"Unexpected error: {str(e)}",
            "store_connected": False
        }

@tool("salla_product_details")
def salla_product_details(product_id: str):
    """Get detailed information for a specific product by ID."""
    token = os.getenv("SALLA_ACCESS_TOKEN")
    
    if not token:
        return {"error": "No access token configured"}
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.salla.dev/admin/v2/products/{product_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data'):
            product = data['data']
            
            # Safely extract price and cost
            price_data = product.get('price', {})
            if isinstance(price_data, dict):
                price_amount = price_data.get('amount', 0)
            else:
                price_amount = price_data or 0
            
            try:
                price = float(price_amount) if price_amount else 0.0
            except (ValueError, TypeError):
                price = 0.0
            
            cost_price = product.get('cost_price', 0)
            try:
                cost = float(cost_price) if cost_price else 0.0
            except (ValueError, TypeError):
                cost = 0.0
            
            return {
                "product_id": str(product.get('id', '')),
                "name": product.get('name', ''),
                "price": price,
                "cost": cost,
                "category": product.get('category', {}).get('name', 'Fashion') if product.get('category') else 'Fashion',
                "brand": product.get('brand', {}).get('name', '') if product.get('brand') else '',
                "description": product.get('description', ''),
                "images": [img.get('url', '') for img in product.get('images', [])],
                "status": product.get('status', 'active')
            }
        else:
            return {"error": "Product not found"}
            
    except Exception as e:
        logger.error(f"Error fetching product details: {str(e)}")
        return {"error": f"API Error: {str(e)}"}

scout_agent = Agent(
    role="Fashion Market Intelligence Scout",
    goal="\n".join([
        "DISCOVER products dynamically from the Salla fashion store",
        "EXTRACT accurate product data for women's fashion items",
        "SEARCH competitor prices across Saudi fashion retailers",
        "VALIDATE and filter competitor data for quality and relevance"
    ]),
    backstory=(
        "You are an expert fashion market researcher specializing in the Saudi women's fashion market. "
        "You have deep knowledge of Salla platform operations and fashion retail competitor analysis. "
        "Your mission is to dynamically discover fashion products in the store and gather precise, "
        "actionable market intelligence from fashion retailers like Namshi, Styli, H&M, and Zara. "
        "You excel at filtering noise from valuable fashion pricing data."
    ),
    verbose=True,
    tools=[salla_inventory_discovery, salla_product_details, fashion_market_search],
    llm=basic_llm,
    max_iter=3,
    allow_delegation=False
)

scout_task = Task(
    description="\n".join([
        "PHASE 1 - Dynamic Product Discovery:",
        "1. Use salla_inventory_discovery to fetch ALL products currently in the fashion store",
        "2. Select the top 3-5 most important products for price optimization",
        "3. Extract: product_id, name, current_price, cost_price, and category for each",
        "",
        "PHASE 2 - Fashion Market Intelligence:",
        "4. For each selected product, use fashion_market_search to find competitors",
        "5. Focus on Saudi fashion retailers: Namshi, Styli, H&M, Zara, Centrepoint",
        "6. Search with both English and Arabic terms for better coverage",
        "",
        "PHASE 3 - Data Validation & Compilation:",
        "7. Filter out suspicious prices (too low/high, broken links, non-fashion items)",
        "8. Ensure all prices are in SAR and from reputable fashion retailers",
        "9. Compile comprehensive market intelligence for all discovered products",
        "",
        "CRITICAL: Focus on ACTUAL products from the store, not hardcoded examples.",
        "The output should reflect real women's fashion items currently available."
    ]),
    expected_output="Comprehensive JSON with discovered fashion products and their competitor analysis.",
    output_json=ExtractedProductPrices,
    output_file=os.path.join(output_dir, "step_1_fashion_market_intelligence.json"),
    agent=scout_agent
)