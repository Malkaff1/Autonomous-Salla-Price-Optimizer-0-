#!/usr/bin/env python3
"""
Quick test script to verify all critical dependencies are installed correctly
and compatible with each other.
"""

import sys

def test_imports():
    """Test that all critical packages can be imported."""
    print("Testing dependency imports...\n")
    
    tests = [
        ("pydantic", "Pydantic (Data Validation)"),
        ("crewai", "CrewAI (Agent Framework)"),
        ("crewai_tools", "CrewAI Tools"),
        ("langchain", "LangChain (LLM Framework)"),
        ("langchain_openai", "LangChain OpenAI"),
        ("openai", "OpenAI SDK"),
        ("fastapi", "FastAPI (Web Framework)"),
        ("sqlalchemy", "SQLAlchemy (Database ORM)"),
        ("celery", "Celery (Task Queue)"),
        ("streamlit", "Streamlit (Dashboard)"),
    ]
    
    failed = []
    passed = []
    
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✓ {description:30} - OK")
            passed.append(module_name)
        except ImportError as e:
            print(f"✗ {description:30} - FAILED: {e}")
            failed.append(module_name)
    
    print(f"\n{'='*60}")
    print(f"Results: {len(passed)} passed, {len(failed)} failed")
    print(f"{'='*60}\n")
    
    return len(failed) == 0

def test_versions():
    """Check versions of critical packages."""
    print("Checking package versions...\n")
    
    try:
        import pydantic
        import crewai
        import langchain
        import openai
        import fastapi
        
        print(f"pydantic:  {pydantic.__version__}")
        print(f"crewai:    {crewai.__version__}")
        print(f"langchain: {langchain.__version__}")
        print(f"openai:    {openai.__version__}")
        print(f"fastapi:   {fastapi.__version__}")
        
        # Check pydantic version compatibility
        pydantic_version = tuple(map(int, pydantic.__version__.split('.')[:2]))
        if pydantic_version >= (2, 4) and pydantic_version < (2, 6):
            print(f"\n✓ Pydantic version {pydantic.__version__} is compatible!")
            return True
        else:
            print(f"\n✗ Pydantic version {pydantic.__version__} may cause conflicts!")
            print(f"  Expected: 2.4.x or 2.5.x")
            return False
            
    except Exception as e:
        print(f"\n✗ Error checking versions: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key packages."""
    print("\nTesting basic functionality...\n")
    
    try:
        # Test Pydantic
        from pydantic import BaseModel
        class TestModel(BaseModel):
            name: str
            value: int
        
        test = TestModel(name="test", value=42)
        print(f"✓ Pydantic model creation works")
        
        # Test FastAPI
        from fastapi import FastAPI
        app = FastAPI()
        print(f"✓ FastAPI app creation works")
        
        # Test CrewAI imports
        from crewai import Agent, Task, Crew
        print(f"✓ CrewAI core classes import successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DEPENDENCY COMPATIBILITY TEST")
    print("="*60 + "\n")
    
    test1 = test_imports()
    print()
    test2 = test_versions()
    print()
    test3 = test_basic_functionality()
    
    print("\n" + "="*60)
    if test1 and test2 and test3:
        print("✓ ALL TESTS PASSED - Dependencies are compatible!")
        print("="*60 + "\n")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Check output above")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
