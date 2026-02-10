# 🐳 Docker Commands Quick Reference

## 🚀 Getting Started

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Start everything (Linux/Mac)
chmod +x start.sh stop.sh entrypoint.sh
./start.sh

# 2. Start everything (Windows)
docker-compose up -d

# 3. Check status
docker-compose ps
```

---

## 📦 Service Management

### Start/Stop

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d web

# Stop all services
docker-compose down

# Stop specific service
docker-compose stop web

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Build

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build web

# Build without cache
docker-compose build --no-cache

# Build and start
docker-compose up -d --build
```

---

## 📊 Monitoring

### Status

```bash
# Check service status
docker-compose ps

# Check resource usage
docker stats

# Check specific container
docker stats salla-api
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Last 100 lines
docker-compose logs --tail=100

# With timestamps
docker-compose logs -f --timestamps
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U salla_user

# Redis health
docker-compose exec redis redis-cli ping
```

---

## 🗄️ Database Operations

### Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U salla_user -d salla_optimizer

# Run SQL query
docker-compose exec db psql -U salla_user -d salla_optimizer -c "SELECT COUNT(*) FROM stores;"

# List tables
docker-compose exec db psql -U salla_user -d salla_optimizer -c "\dt"
```

### Backup

```bash
# Create backup
docker-compose exec db pg_dump -U salla_user salla_optimizer > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20240209.sql | docker-compose exec -T db psql -U salla_user -d salla_optimizer

# Backup with compression
docker-compose exec db pg_dump -U salla_user salla_optimizer | gzip > backup.sql.gz
```

### Reset

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm salla-postgres-data

# Start fresh
docker-compose up -d
```

---

## 🔴 Redis Operations

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check keys
docker-compose exec redis redis-cli KEYS '*'

# Get value
docker-compose exec redis redis-cli GET key_name

# Flush all data
docker-compose exec redis redis-cli FLUSHALL
```

---

## 🔧 Debugging

### Execute Commands

```bash
# Open bash in container
docker-compose exec web bash

# Run Python command
docker-compose exec web python -c "print('Hello')"

# Check Python version
docker-compose exec web python --version

# List files
docker-compose exec web ls -la
```

### Inspect

```bash
# Inspect container
docker inspect salla-api

# Inspect network
docker network inspect salla-network

# Inspect volume
docker volume inspect salla-postgres-data
```

### Environment

```bash
# View environment variables
docker-compose exec web env

# Check specific variable
docker-compose exec web printenv DATABASE_URL
```

---

## 📈 Scaling

### Workers

```bash
# Scale to 4 workers
docker-compose up -d --scale celery_worker=4

# Scale to 1 worker
docker-compose up -d --scale celery_worker=1
```

### Resources

```bash
# View resource usage
docker stats

# Limit resources (edit docker-compose.yml)
services:
  web:
    mem_limit: 1g
    cpus: '0.5'
```

---

## 🧹 Cleanup

### Remove Services

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all
```

### System Cleanup

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 🔄 Updates

### Update Code

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
# Edit requirements_saas.txt
# Then rebuild
docker-compose build --no-cache web
docker-compose up -d
```

---

## 🌐 Networking

### Network Commands

```bash
# List networks
docker network ls

# Inspect network
docker network inspect salla-network

# Connect container to network
docker network connect salla-network container_name

# Disconnect container
docker network disconnect salla-network container_name
```

---

## 📦 Volume Management

### Volume Commands

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect salla-postgres-data

# Backup volume
docker run --rm -v salla-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volume
docker run --rm -v salla-postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## 🎯 Production Commands

### Deploy

```bash
# Production build
docker-compose -f docker-compose.yml build

# Start in production mode
docker-compose -f docker-compose.yml up -d

# View production logs
docker-compose -f docker-compose.yml logs -f
```

### Monitoring

```bash
# Check all services
docker-compose ps

# Check specific service health
docker-compose exec web curl http://localhost:8000/health

# View Flower UI
open http://localhost:5555
```

---

## 🐛 Troubleshooting Commands

### Port Conflicts

```bash
# Check what's using port 8000
netstat -tulpn | grep 8000

# Kill process on port (Linux)
kill -9 $(lsof -t -i:8000)

# Kill process on port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Container Issues

```bash
# Check container logs
docker logs salla-api

# Check container processes
docker top salla-api

# Check container stats
docker stats salla-api

# Restart container
docker restart salla-api
```

### Network Issues

```bash
# Test connectivity between containers
docker-compose exec web ping db
docker-compose exec web ping redis

# Check DNS resolution
docker-compose exec web nslookup db
```

---

## 📚 Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dcr='docker-compose restart'

# Salla specific
alias salla-start='docker-compose up -d'
alias salla-stop='docker-compose down'
alias salla-logs='docker-compose logs -f'
alias salla-status='docker-compose ps'
alias salla-db='docker-compose exec db psql -U salla_user -d salla_optimizer'
```

---

## 🎉 Quick Reference Card

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Restart
docker-compose restart

# Database
docker-compose exec db psql -U salla_user -d salla_optimizer

# Redis
docker-compose exec redis redis-cli

# Shell
docker-compose exec web bash

# Health
curl http://localhost:8000/health
```

---

**💡 Pro Tip:** Keep this file open in a terminal for quick reference!
