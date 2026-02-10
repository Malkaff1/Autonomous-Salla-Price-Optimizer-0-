#!/bin/bash
set -e

echo "🚀 Starting Salla Price Optimizer Entrypoint..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
MAX_RETRIES=30
RETRY_COUNT=0

until pg_isready -h db -U salla_user -d salla_optimizer 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ PostgreSQL failed to start after $MAX_RETRIES attempts"
    exit 1
  fi
  echo "PostgreSQL is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
RETRY_COUNT=0

until redis-cli -h redis ping > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Redis failed to start after $MAX_RETRIES attempts"
    exit 1
  fi
  echo "Redis is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done
echo "✅ Redis is ready!"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/store-data /app/logs /app/ai-agent-output
echo "✅ Directories created!"

# Initialize database if needed
echo "🗄️  Initializing database..."
python3 << 'PYTHON_SCRIPT'
import sys
import os

try:
    from database.db import init_db, engine
    from sqlalchemy import inspect
    
    # Check if tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print('📋 Creating database schema...')
        init_db()
        print('✅ Database initialized!')
    else:
        print(f'✅ Database already initialized ({len(tables)} tables found)')
        
except Exception as e:
    print(f'⚠️  Database initialization error: {str(e)}')
    print('⚠️  Continuing anyway - tables may be created on first request')
    sys.exit(0)
PYTHON_SCRIPT

echo "🎉 Entrypoint completed successfully!"
echo "🚀 Starting application..."
