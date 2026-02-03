#!/usr/bin/env python3
"""
Test script for the Fashion-focused Salla Price Optimizer System
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment setup."""
    logger.info("🔧 Testing environment setup...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY", 
        "SALLA_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            logger.info(f"✅ {var}: {'*' * 10}...{os.getenv(var)[-4:]}")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Environment setup complete")
    return True

def test_salla_connection():
    """Test Salla API connection and product discovery."""
    logger.info("🔗 Testing Salla API connection...")
    
    try:
        import requests
        
        # Test direct API call
        token = os.getenv("SALLA_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.salla.dev/admin/v2/products"
        params = {"per_page": 5, "page": 1}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data'):
            products = data['data']
            logger.info(f"✅ Connected to Salla store successfully")
            logger.info(f"📦 Found {len(products)} products")
            
            for i, product in enumerate(products[:3], 1):
                name = product.get('name', 'Unknown Product')
                price = product.get('price', {}).get('amount', 0)
                logger.info(f"   {i}. {name} - {price} SAR")
            
            return True
        else:
            logger.error("❌ No products found in store")
            return False
            
    except Exception as e:
        logger.error(f"❌ Salla connection test failed: {str(e)}")
        return False

def test_fashion_search():
    """Test fashion market search functionality."""
    logger.info("🔍 Testing fashion market search...")
    
    try:
        from tavily import TavilyClient
        
        # Test Tavily connection
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Test with a simple search
        search_results = tavily_client.search(
            query="فستان سهرة السعودية",  # Evening dress Saudi Arabia
            search_depth="basic",
            max_results=3
        )
        
        if search_results.get('results'):
            logger.info(f"✅ Fashion search working - found {len(search_results['results'])} results")
            for i, result in enumerate(search_results['results'][:2], 1):
                title = result.get('title', 'No title')[:50]
                logger.info(f"   {i}. {title}...")
            return True
        else:
            logger.warning("⚠️ Fashion search returned no results")
            return True  # Not necessarily an error
            
    except Exception as e:
        logger.error(f"❌ Fashion search test failed: {str(e)}")
        return False

def test_system_integration():
    """Test full system integration."""
    logger.info("🎯 Testing system integration...")
    
    try:
        # Import main components
        from agents.scout_agent import scout_agent, scout_task
        from agents.analysis_agent import get_pricing_analyst
        from agents.executor_agent import get_executor_agent
        from crewai import LLM
        
        # Test LLM initialization
        llm = LLM(model="gpt-4o", temperature=0)
        logger.info("✅ LLM initialized")
        
        # Test agent creation
        analyst_agent, analyst_task = get_pricing_analyst(llm, scout_task)
        executor_agent, executor_task = get_executor_agent(llm, analyst_task)
        logger.info("✅ All agents created successfully")
        
        logger.info("✅ System integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ System integration test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Fashion Price Optimizer System Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Salla API Connection", test_salla_connection),
        ("Fashion Market Search", test_fashion_search),
        ("System Integration", test_system_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: FAILED with exception: {str(e)}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready for fashion price optimization.")
        logger.info("💡 Run 'python run_optimizer.py' to start the full workflow")
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()