# Docker Commands Reference

## 🔨 Build Commands

### Clean Build (Recommended)
```bash
# Windows
REBUILD_CLEAN.bat

# Linux/Mac
chmod +x rebuild_clean.sh
./rebuild_clean.sh
```

### Standard Build
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build web

# Build without cache
docker-compose build --no-cache

# Build with progress output
docker-compose build --progress=plain
```

## 🚀 Start/Stop Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d web

# Rebuild and start
docker-compose up -d --build
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop web
```

## 📊 Monitoring Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00
```

### Check Status
```bash
# List running containers
docker-compose ps

# Detailed container info
docker-compose ps -a

# Check resource usage
docker stats
```

## 🧪 Testing Commands

### Run Tests
```bash
# Test dependencies
docker-compose run --rm web python test_dependencies.py

# Run pytest
docker-compose run --rm web pytest

# Run specific test
docker-compose run --rm web pytest tests/test_api.py
```

### Interactive Shell
```bash
# Python shell
docker-compose exec web python

# Bash shell
docker-compose exec web bash

# Database shell
docker-compose exec db psql -U salla_user -d salla_optimizer
```

## 🔍 Debugging Commands

### Check Configuration
```bash
# View resolved docker-compose config
docker-compose config

# Validate docker-compose.yml
docker-compose config --quiet
```

### Inspect Containers
```bash
# Container details
docker inspect <container_id>

# Container logs
docker logs <container_id>

# Container processes
docker top <container_id>
```

### Check Dependencies
```bash
# List installed packages
docker-compose exec web pip list

# Check specific package
docker-compose exec web pip show pydantic

# Check for conflicts
docker-compose exec web pip check
```

## 🧹 Cleanup Commands

### Remove Containers
```bash
# Remove stopped containers
docker container prune -f

# Remove all containers
docker rm -f $(docker ps -aq)
```

### Remove Images
```bash
# Remove dangling images
docker image prune -f

# Remove all unused images
docker image prune -a -f

# Remove specific image
docker rmi <image_id>
```

### Remove Volumes
```bash
# Remove unused volumes
docker volume prune -f

# Remove specific volume
docker volume rm <volume_name>

# List volumes
docker volume ls
```

### Nuclear Clean
```bash
# Remove everything (use with caution!)
docker system prune -af --volumes

# Remove build cache
docker builder prune -af
```

## 🔄 Restart Commands

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web

# Restart with rebuild
docker-compose up -d --build --force-recreate
```

## 📦 Database Commands

### Initialize Database
```bash
# Run init script
docker-compose exec web python -c "from database.db import init_db; init_db()"

# Run migrations
docker-compose exec web alembic upgrade head
```

### Backup Database
```bash
# Create backup
docker-compose exec db pg_dump -U salla_user salla_optimizer > backup.sql

# Restore backup
docker-compose exec -T db psql -U salla_user salla_optimizer < backup.sql
```

### Database Queries
```bash
# Connect to database
docker-compose exec db psql -U salla_user -d salla_optimizer

# Run query
docker-compose exec db psql -U salla_user -d salla_optimizer -c "SELECT * FROM users;"
```

## 🌐 Network Commands

### Network Info
```bash
# List networks
docker network ls

# Inspect network
docker network inspect <network_name>

# Connect container to network
docker network connect <network_name> <container_name>
```

## 📈 Performance Commands

### Resource Usage
```bash
# Real-time stats
docker stats

# Container resource limits
docker inspect <container_id> | grep -A 10 "Memory"

# Disk usage
docker system df
```

## 🔐 Security Commands

### Scan Images
```bash
# Scan for vulnerabilities (if Docker Scout enabled)
docker scout cves <image_name>

# Check image history
docker history <image_name>
```

## 💡 Useful Combinations

### Full Restart
```bash
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d
```

### Quick Rebuild
```bash
docker-compose down && docker-compose up -d --build
```

### View All Logs
```bash
docker-compose logs -f --tail=100
```

### Clean and Rebuild
```bash
docker-compose down -v && docker system prune -af && docker-compose build --no-cache
```

## 🎯 Service-Specific Commands

### Web Service (FastAPI)
```bash
# Restart web
docker-compose restart web

# View web logs
docker-compose logs -f web

# Shell into web
docker-compose exec web bash
```

### Celery Worker
```bash
# Restart celery
docker-compose restart celery

# View celery logs
docker-compose logs -f celery

# Check celery status
docker-compose exec celery celery -A scheduler.celery_app inspect active
```

### Dashboard (Streamlit)
```bash
# Restart dashboard
docker-compose restart dashboard

# View dashboard logs
docker-compose logs -f dashboard
```

### Redis
```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check Redis info
docker-compose exec redis redis-cli INFO

# Monitor Redis commands
docker-compose exec redis redis-cli MONITOR
```

## 📝 Notes

- Use `-d` flag to run in detached mode (background)
- Use `-f` flag with logs to follow (stream) output
- Use `--rm` flag to automatically remove container after run
- Use `--no-cache` to force rebuild without using cache
- Always check logs if something doesn't work: `docker-compose logs -f`

## 🆘 Emergency Commands

### Service Won't Stop
```bash
docker kill <container_id>
```

### Port Already in Use
```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <pid> /F
```

### Out of Disk Space
```bash
docker system prune -af --volumes
docker builder prune -af
```

### Container Keeps Restarting
```bash
# Check logs
docker-compose logs --tail=50 <service_name>

# Stop auto-restart
docker update --restart=no <container_id>
```
