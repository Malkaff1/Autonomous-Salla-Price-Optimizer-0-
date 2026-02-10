# 🚀 Multi-Tenant SaaS Deployment Guide
## Salla Price Optimizer - Production Setup

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Service Deployment](#service-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Scaling Guide](#scaling-guide)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Store A  │  │ Store B  │  │ Store C  │  ...             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                  API LAYER (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  OAuth Handler  │  Dashboard API  │  Admin API       │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│              BUSINESS LOGIC LAYER                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Multi-Tenant Optimizer  │  Token Manager            │ │
│  │  CrewAI Agents          │  Data Isolation           │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│              TASK QUEUE (Celery + Redis)                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Scheduled Tasks  │  Background Jobs  │  Workers     │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│              DATA LAYER (PostgreSQL)                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Stores  │  Products  │  Competitors  │  Decisions   │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software
- **Python 3.10+**
- **PostgreSQL 14+**
- **Redis 7+**
- **Docker & Docker Compose** (recommended)

### Required API Keys
- OpenAI API Key
- Tavily API Key
- Salla App Credentials (per store)

---

## 🗄️ Database Setup

### Option 1: Local PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE salla_optimizer;
CREATE USER salla_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE salla_optimizer TO salla_user;
\q

# Initialize schema
python -c "from database.db import init_db; init_db()"
```

### Option 2: Docker PostgreSQL

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name salla-postgres \
  -e POSTGRES_DB=salla_optimizer \
  -e POSTGRES_USER=salla_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# Initialize schema
python -c "from database.db import init_db; init_db()"
```

### Option 3: Managed Database (Production)
- **AWS RDS PostgreSQL**
- **Google Cloud SQL**
- **Azure Database for PostgreSQL**
- **DigitalOcean Managed Databases**

---

## ⚙️ Environment Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://salla_user:password@localhost:5432/salla_optimizer

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# API Keys
OPENAI_API_KEY=sk-proj-your-key-here
TAVILY_API_KEY=tvly-your-key-here

# OAuth
OAUTH_CALLBACK_URL=https://yourdomain.com/oauth/callback

# Optional: Salla Default Credentials (for testing)
SALLA_CLIENT_ID=your-default-client-id
SALLA_CLIENT_SECRET=your-default-client-secret

# Security
SECRET_KEY=your-secret-key-for-sessions
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn
```

---

## 🚀 Service Deployment

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements_saas.txt
```

### 2. Start Redis

```bash
# Option A: Local Redis
redis-server

# Option B: Docker Redis
docker run -d --name salla-redis -p 6379:6379 redis:7
```

### 3. Start FastAPI Server

```bash
# Development
uvicorn api.oauth_handler:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn api.oauth_handler:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 4. Start Celery Workers

```bash
# Start Celery worker
celery -A scheduler.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=50

# Start Celery Beat (scheduler)
celery -A scheduler.celery_app beat \
  --loglevel=info

# Start Flower (monitoring UI)
celery -A scheduler.celery_app flower \
  --port=5555
```

### 5. Start Streamlit Dashboard

```bash
# Multi-tenant dashboard
streamlit run dashboard_multi_tenant.py --server.port 8501
```

---

## 🐳 Docker Compose Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: salla_optimizer
      POSTGRES_USER: salla_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U salla_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    command: gunicorn api.oauth_handler:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  celery_worker:
    build: .
    command: celery -A scheduler.celery_app worker --loglevel=info --concurrency=4
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  celery_beat:
    build: .
    command: celery -A scheduler.celery_app beat --loglevel=info
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  flower:
    build: .
    command: celery -A scheduler.celery_app flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - .env
    depends_on:
      - redis
    restart: unless-stopped

  dashboard:
    build: .
    command: streamlit run dashboard_multi_tenant.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    env_file:
      - .env
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
```

Deploy:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Celery Flower UI
open http://localhost:5555

# Database Status
psql -U salla_user -d salla_optimizer -c "SELECT COUNT(*) FROM stores;"
```

### Logs

```bash
# API logs
tail -f logs/api.log

# Celery logs
tail -f logs/celery.log

# Database logs
tail -f /var/log/postgresql/postgresql-14-main.log
```

### Backup

```bash
# Database backup
pg_dump -U salla_user salla_optimizer > backup_$(date +%Y%m%d).sql

# Restore
psql -U salla_user salla_optimizer < backup_20240209.sql
```

---

## 📈 Scaling Guide

### Horizontal Scaling

```bash
# Add more Celery workers
celery -A scheduler.celery_app worker --loglevel=info --concurrency=8

# Add more API instances (behind load balancer)
gunicorn api.oauth_handler:app --workers 8 --bind 0.0.0.0:8001
```

### Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX CONCURRENTLY idx_stores_active ON stores(is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_products_tracked ON products(store_id, is_tracked) WHERE is_tracked = TRUE;
CREATE INDEX CONCURRENTLY idx_runs_recent ON optimization_runs(store_id, started_at DESC);

-- Analyze tables
ANALYZE stores;
ANALYZE products;
ANALYZE optimization_runs;
```

### Caching

```python
# Add Redis caching for frequently accessed data
from redis import Redis
cache = Redis.from_url(os.getenv("REDIS_URL"))

# Cache store data
cache.setex(f"store:{store_id}", 3600, json.dumps(store_data))
```

---

## 🔒 Security Best Practices

1. **Use HTTPS** for all production endpoints
2. **Rotate secrets** regularly
3. **Implement rate limiting** on API endpoints
4. **Use environment variables** for sensitive data
5. **Enable database encryption** at rest
6. **Implement API authentication** (JWT tokens)
7. **Regular security audits**

---

## 🎯 Next Steps

1. **Deploy to production** using Docker Compose
2. **Set up monitoring** with Sentry or similar
3. **Configure backups** (daily database backups)
4. **Set up CI/CD** pipeline
5. **Add user authentication** to dashboard
6. **Implement billing** system (Stripe integration)
7. **Add email notifications** for optimization results

---

## 📞 Support

For issues or questions:
- Check logs first
- Review this guide
- Contact support team

---

**🎉 Your Multi-Tenant SaaS is Ready!**
