#!/usr/bin/env python3
"""
Initialize Multi-Tenant SaaS System
Run this script to set up the database and verify configuration
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_requirements():
    """Check if all required packages are installed"""
    print("📦 Checking requirements...")
    
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'psycopg2',
        'celery',
        'redis',
        'crewai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install -r requirements_saas.txt")
        return False
    
    print("✅ All requirements installed\n")
    return True


def check_environment():
    """Check if required environment variables are set"""
    print("⚙️  Checking environment variables...")
    
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string',
        'REDIS_URL': 'Redis connection string',
        'OPENAI_API_KEY': 'OpenAI API key',
        'TAVILY_API_KEY': 'Tavily API key',
        'OAUTH_CALLBACK_URL': 'OAuth callback URL'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                display_value = value[:10] + '...'
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var} - MISSING ({description})")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print(f"Add them to your .env file")
        return False
    
    print("✅ All environment variables set\n")
    return True


def test_database_connection():
    """Test database connection"""
    print("🗄️  Testing database connection...")
    
    try:
        from database.db import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✅ Database connection successful")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("🔴 Testing Redis connection...")
    
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print("  ✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Redis connection failed: {e}")
        return False


def initialize_database():
    """Initialize database schema"""
    print("🔧 Initializing database schema...")
    
    try:
        from database.db import init_db
        init_db()
        print("  ✅ Database schema created")
        return True
    except Exception as e:
        print(f"  ❌ Database initialization failed: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'store-data',
        'logs',
        'database',
        'api',
        'scheduler',
        'optimizer'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ All directories created\n")
    return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 INITIALIZATION COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:\n")
    
    print("1️⃣  Start Redis:")
    print("   redis-server")
    print("   OR")
    print("   docker run -d --name salla-redis -p 6379:6379 redis:7\n")
    
    print("2️⃣  Start FastAPI Server:")
    print("   uvicorn api.oauth_handler:app --reload --port 8000\n")
    
    print("3️⃣  Start Celery Worker:")
    print("   celery -A scheduler.celery_app worker --loglevel=info\n")
    
    print("4️⃣  Start Celery Beat (Scheduler):")
    print("   celery -A scheduler.celery_app beat --loglevel=info\n")
    
    print("5️⃣  Start Flower (Monitoring):")
    print("   celery -A scheduler.celery_app flower --port=5555\n")
    
    print("6️⃣  Test OAuth Flow:")
    print("   Open: http://localhost:8000/oauth/authorize\n")
    
    print("📚 Documentation:")
    print("   - SAAS_DEPLOYMENT_GUIDE.md")
    print("   - SAAS_ARCHITECTURE_SUMMARY.md\n")
    
    print("🐳 Or use Docker Compose:")
    print("   docker-compose up -d\n")
    
    print("="*60)


def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("🚀 SALLA PRICE OPTIMIZER - SAAS INITIALIZATION")
    print("="*60 + "\n")
    
    steps = [
        ("Checking requirements", check_requirements),
        ("Checking environment", check_environment),
        ("Testing database", test_database_connection),
        ("Testing Redis", test_redis_connection),
        ("Creating directories", create_directories),
        ("Initializing database", initialize_database),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
        print()
    
    if failed_steps:
        print("\n⚠️  INITIALIZATION INCOMPLETE")
        print(f"Failed steps: {', '.join(failed_steps)}")
        print("\nPlease fix the issues above and run again.")
        sys.exit(1)
    else:
        print_next_steps()
        sys.exit(0)


if __name__ == "__main__":
    main()
