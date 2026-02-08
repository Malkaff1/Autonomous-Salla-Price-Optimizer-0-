# 🐳 Docker Deployment Guide
## Salla Price Optimizer - Complete Docker Setup

---

## 📋 Prerequisites

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** (to clone the repository)

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/salla-price-optimizer.git
cd salla-price-optimizer
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**Required Variables:**
```bash
OPENAI_API_KEY=sk-proj-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

### 3. Build and Start
```bash
# Build images and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Services
```bash
# Check all services are running
docker-compose ps

# Should show 7 services: db, redis, web, celery_worker, celery_beat, flower, dashboard
```

### 5. Access Services
- **API**: http://localhost:8000
- **OAuth**: http://localhost:8000/oauth/authorize
- **Dashboard**: http://localhost:8501
- **Flower (Monitoring)**: http://localhost:5555
- **API Docs**: http://localhost:8000/docs

---

## 📦 Docker Services

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                   (salla-network)                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Web    │  │ Worker   │  │  Beat    │             │
│  │  :8000   │  │          │  │          │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                     │
│       └─────────────┴─────────────┘                     │
│                     │                                   │
│       ┌─────────────┴─────────────┐                     │
│       │                           │                     │
│  ┌────▼────┐              ┌──────▼──────┐              │
│  │   DB    │              │    Redis    │              │
│  │  :5432  │              │    :6379    │              │
│  └─────────┘              └─────────────┘              │
│                                                          │
│  ┌──────────┐  ┌──────────┐                            │
│  │ Flower   │  │Dashboard │                            │
│  │  :5555   │  │  :8501   │                            │
│  └──────────┘  └──────────┘                            │
└─────────────────────────────────────────────────────────┘
```

### Service Details

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| **db** | salla-postgres | 5432 | PostgreSQL database |
| **redis** | salla-redis | 6379 | Message broker & cache |
| **web** | salla-api | 8000 | FastAPI OAuth & API |
| **celery_worker** | salla-celery-worker | - | Background tasks |
| **celery_beat** | salla-celery-beat | - | Task scheduler |
| **flower** | salla-flower | 5555 | Celery monitoring |
| **dashboard** | salla-dashboard | 8501 | Streamlit UI |

---

## 🔧 Docker Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f web
docker-compose logs -f celery_worker

# Check service status
docker-compose ps

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Building & Updating

```bash
# Rebuild images (after code changes)
docker-compose build

# Rebuild specific service
docker-compose build web

# Rebuild and restart
docker-compose up -d --build

# Pull latest images
docker-compose pull
```

### Service Management

```bash
# Start specific service
docker-compose up -d web

# Stop specific service
docker-compose stop web

# Restart specific service
docker-compose restart web

# Scale workers (run 4 workers)
docker-compose up -d --scale celery_worker=4
```

### Debugging

```bash
# Execute command in running container
docker-compose exec web bash

# Check database
docker-compose exec db psql -U salla_user -d salla_optimizer

# Check Redis
docker-compose exec redis redis-cli ping

# View container resource usage
docker stats

# Inspect container
docker inspect salla-api
```

---

## 🗄️ Database Management

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U salla_user -d salla_optimizer

# Run SQL query
docker-compose exec db psql -U salla_user -d salla_optimizer -c "SELECT COUNT(*) FROM stores;"
```

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U salla_user salla_optimizer > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20240209.sql | docker-compose exec -T db psql -U salla_user -d salla_optimizer
```

### Reset Database

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm salla-postgres-data

# Start services (will create fresh database)
docker-compose up -d
```

---

## 📊 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Check all services
docker-compose ps

# View resource usage
docker stats
```

### Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f celery_worker

# Follow logs with timestamps
docker-compose logs -f --timestamps
```

### Flower UI

Access Celery monitoring at: http://localhost:5555

Features:
- Active tasks
- Task history
- Worker status
- Task statistics
- Real-time monitoring

---

## 🔐 Security

### Production Checklist

- [ ] Change default database password
- [ ] Use strong passwords
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Restrict port access
- [ ] Use secrets management
- [ ] Enable firewall
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Update dependencies

### Environment Variables

```bash
# Generate secure password
openssl rand -base64 32

# Update .env
DB_PASSWORD=your-secure-password-here
```

### Network Security

```bash
# Restrict external access (production)
# Edit docker-compose.yml, remove port mappings for internal services

# Example: Remove these lines for production
# ports:
#   - "5432:5432"  # Don't expose PostgreSQL
#   - "6379:6379"  # Don't expose Redis
```

---

## 🚀 Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml salla

# List services
docker service ls

# Scale service
docker service scale salla_celery_worker=4

# Remove stack
docker stack rm salla
```

### Using Kubernetes

```bash
# Convert docker-compose to k8s
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f .

# Check pods
kubectl get pods

# Scale deployment
kubectl scale deployment celery-worker --replicas=4
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/salla
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /dashboard {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs web

# Verify environment variables
docker-compose config

# Check port conflicts
netstat -tulpn | grep -E '8000|5432|6379'
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db pg_isready -U salla_user

# Verify credentials
docker-compose exec db psql -U salla_user -d salla_optimizer
```

### Redis Connection Error

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### Celery Tasks Not Running

```bash
# Check worker is running
docker-compose ps celery_worker

# Check worker logs
docker-compose logs celery_worker

# Check beat is running
docker-compose ps celery_beat

# Inspect active tasks
docker-compose exec celery_worker celery -A scheduler.celery_app inspect active
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory

# Limit container memory in docker-compose.yml
services:
  web:
    mem_limit: 1g
    mem_reservation: 512m
```

### Disk Space Issues

```bash
# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm salla-postgres-data
```

---

## 📈 Performance Tuning

### Worker Scaling

```bash
# Run multiple workers
docker-compose up -d --scale celery_worker=4

# Or edit docker-compose.yml
services:
  celery_worker:
    deploy:
      replicas: 4
```

### Database Optimization

```sql
-- Connect to database
docker-compose exec db psql -U salla_user -d salla_optimizer

-- Analyze tables
ANALYZE stores;
ANALYZE products;

-- Check indexes
\di

-- Vacuum database
VACUUM ANALYZE;
```

### Redis Optimization

```bash
# Edit docker-compose.yml
services:
  redis:
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### Update Dependencies

```bash
# Update requirements_saas.txt
# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Backup Before Update

```bash
# Backup database
docker-compose exec db pg_dump -U salla_user salla_optimizer > backup_pre_update.sql

# Backup volumes
docker run --rm -v salla-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

---

## 📞 Support

### Useful Commands

```bash
# View all containers
docker ps -a

# View all volumes
docker volume ls

# View all networks
docker network ls

# Clean everything
docker system prune -a --volumes
```

### Getting Help

```bash
# Docker Compose help
docker-compose --help

# Service-specific help
docker-compose exec web python --version
docker-compose exec celery_worker celery --help
```

---

## ✅ Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.env` file configured with API keys
- [ ] Database password changed
- [ ] Services built: `docker-compose build`
- [ ] Services started: `docker-compose up -d`
- [ ] Health checks passing: `docker-compose ps`
- [ ] API accessible: http://localhost:8000/health
- [ ] Dashboard accessible: http://localhost:8501
- [ ] Flower accessible: http://localhost:5555
- [ ] OAuth flow tested
- [ ] First store onboarded
- [ ] Background tasks running
- [ ] Logs monitored
- [ ] Backups configured

---

**🎉 Your Dockerized Multi-Tenant SaaS is Ready!**

All services are containerized, networked, and ready for production deployment.
