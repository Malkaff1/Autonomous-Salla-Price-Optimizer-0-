#!/bin/bash
set -e

echo "🚀 Starting Salla Price Optimizer Entrypoint..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h db -U salla_user -d salla_optimizer; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until redis-cli -h redis ping > /dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Initialize database if needed
echo "🗄️  Initializing database..."
python -c "
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
    print('✅ Database already initialized')
" || {
    echo "⚠️  Database initialization failed, but continuing..."
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/store-data /app/logs /app/ai-agent-output
echo "✅ Directories created!"

echo "🎉 Entrypoint completed successfully!"
echo "🚀 Starting application..."
