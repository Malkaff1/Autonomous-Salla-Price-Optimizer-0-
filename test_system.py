#!/usr/bin/env python3
"""
Test script for the Salla Price Optimizer system.
This script validates the system setup and runs basic functionality tests.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to Python path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from our local utils module
import utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test environment variables and dependencies."""
    print("🔧 Testing Environment Setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Validate environment variables
    env_status = utils.validate_environment_variables()
    
    for var_name, is_set in env_status.items():
        status = "✅ SET" if is_set else "❌ MISSING"
        print(f"  {var_name}: {status}")
    
    missing_vars = [var for var, is_set in env_status.items() if not is_set]
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required API keys are set.")
        return False
    
    print("✅ Environment setup is complete!")
    return True

def test_directory_structure():
    """Test directory structure and file permissions."""
    print("\n📁 Testing Directory Structure...")
    
    required_dirs = ["agents", "tools", "ai-agent-output"]
    required_files = [
        "main.py",
        "agents/scout_agent.py",
        "agents/analysis_agent.py", 
        "agents/executor_agent.py",
        "tools/market_search.py",
        "tools/vision_tool.py",
        "requirements.txt"
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  📂 {dir_name}: ✅ EXISTS")
        else:
            print(f"  📂 {dir_name}: ❌ MISSING")
            return False
    
    # Check files
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"  📄 {file_name}: ✅ EXISTS")
        else:
            print(f"  📄 {file_name}: ❌ MISSING")
            return False
    
    # Ensure output directory
    utils.ensure_output_directory()
    print("  📂 ai-agent-output: ✅ READY")
    
    print("✅ Directory structure is correct!")
    return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing Module Imports...")
    
    required_modules = [
        ("crewai", "CrewAI framework"),
        ("openai", "OpenAI API client"),
        ("requests", "HTTP requests"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment variables"),
        ("tavily", "Tavily search client")
    ]
    
    failed_imports = []
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"  📦 {module_name}: ✅ IMPORTED ({description})")
        except ImportError as e:
            print(f"  📦 {module_name}: ❌ FAILED ({description}) - {str(e)}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All modules imported successfully!")
    return True

def test_agent_initialization():
    """Test that agents can be initialized without errors."""
    print("\n🤖 Testing Agent Initialization...")
    
    try:
        # Test basic imports from agent modules
        from agents.scout_agent import scout_agent, scout_task
        print("  🕵️ Scout Agent: ✅ LOADED")
        
        from agents.analysis_agent import get_pricing_analyst
        print("  📊 Analysis Agent: ✅ LOADED")
        
        from agents.executor_agent import get_executor_agent
        print("  ⚡ Executor Agent: ✅ LOADED")
        
        print("✅ All agents loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        return False

def test_tools():
    """Test that custom tools are working."""
    print("\n🛠️ Testing Custom Tools...")
    
    try:
        from tools.market_search import advanced_market_search
        print("  🔍 Market Search Tool: ✅ LOADED")
        
        from tools.vision_tool import analyze_product_image
        print("  👁️ Vision Analysis Tool: ✅ LOADED")
        
        print("✅ All tools loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Tool loading failed: {str(e)}")
        return False

def run_system_test():
    """Run a basic system test without making API calls."""
    print("\n🚀 Running System Integration Test...")
    
    try:
        # Import main components
        from main import main
        print("  📋 Main orchestrator: ✅ READY")
        
        # Test utility functions
        import utils
        
        # Test profit margin calculation
        margin = utils.calculate_profit_margin(100, 80)
        expected_margin = 25.0  # (100-80)/80 * 100
        assert abs(margin['margin_percentage'] - expected_margin) < 0.01
        print("  🧮 Profit calculation: ✅ WORKING")
        
        # Test risk assessment
        risk = utils.get_risk_level(20, 5)
        assert risk == "Low"
        print("  ⚠️ Risk assessment: ✅ WORKING")
        
        print("✅ System integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 Salla Price Optimizer - System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Directory Structure", test_directory_structure),
        ("Module Imports", test_imports),
        ("Agent Initialization", test_agent_initialization),
        ("Custom Tools", test_tools),
        ("System Integration", run_system_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} test failed!")
        except Exception as e:
            print(f"\n💥 {test_name} test crashed: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Salla Price Optimizer is ready to run.")
        print("\nNext steps:")
        print("1. Ensure your .env file has all required API keys")
        print("2. Run: python main.py")
        print("3. Monitor the ai-agent-output/ directory for results")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the system.")
        sys.exit(1)

if __name__ == "__main__":
    main()