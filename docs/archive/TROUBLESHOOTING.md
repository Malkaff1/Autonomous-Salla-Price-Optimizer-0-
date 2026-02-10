# 🔧 Troubleshooting Guide - Salla Price Optimizer

## Quick Diagnostic Commands

```bash
# Run full diagnostics
diagnose.bat

# View logs
check_logs.bat

# Force rebuild everything
rebuild.bat

# Fix line endings
fix_line_endings.bat
```

---

## Common Issues & Solutions

### 1. ❌ Containers Not Showing in Docker Desktop

**Symptoms:**
- Docker Desktop shows no containers
- `docker-compose ps` shows nothing
- Containers exit immediately after starting

**Solutions:**

#### A. Check if Docker is running
```bash
docker info
```
If this fails, start Docker Desktop and wait for it to be ready.

#### B. Check container status
```bash
docker-compose ps
```

#### C. View error logs
```bash
docker-compose logs
```

#### D. Force rebuild
```bash
rebuild.bat
```

---

### 2. 🔴 Database Container Exits with Code 1

**Symptoms:**
- `salla-postgres` container shows "Exited (1)"
- Logs show: "database system was interrupted"

**Solutions:**

#### A. Remove corrupted volume
```bash
docker-compose down -v
docker-compose up -d
```

#### B. Check PostgreSQL logs
```bash
docker-compose logs db
```

#### C. Verify environment variables
Check `.env` file has:
```
DB_PASSWORD=salla_secure_password_2024
```

---

### 3. 🔴 Redis Connection Refused

**Symptoms:**
- Services can't connect to Redis
- Logs show: "Connection refused" or "redis:6379"

**Solutions:**

#### A. Check Redis is running
```bash
docker-compose ps redis
```

#### B. Restart Redis
```bash
docker-compose restart redis
```

#### C. Check Redis logs
```bash
docker-compose logs redis
```

---

### 4. 🔴 Web/API Container Fails to Start

**Symptoms:**
- `salla-api` container exits immediately
- Logs show Python errors or import errors

**Solutions:**

#### A. Check for missing dependencies
```bash
docker-compose logs web
```

Look for:
- `ModuleNotFoundError`
- `ImportError`
- `No module named 'xxx'`

#### B. Rebuild with no cache
```bash
docker-compose build --no-cache web
docker-compose up -d web
```

#### C. Check entrypoint.sh line endings
```bash
fix_line_endings.bat
rebuild.bat
```

---

### 5. 🔴 Port Already in Use

**Symptoms:**
- Error: "port is already allocated"
- Error: "bind: address already in use"

**Solutions:**

#### A. Find what's using the port
```bash
# Check port 8000
netstat -ano | findstr ":8000"

# Check port 8501
netstat -ano | findstr ":8501"

# Check port 5432
netstat -ano | findstr ":5432"
```

#### B. Stop the conflicting process
```bash
# Kill process by PID (from netstat output)
taskkill /PID <PID> /F
```

#### C. Change ports in docker-compose.yml
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

---

### 6. 🔴 Entrypoint.sh Permission Denied

**Symptoms:**
- Error: "permission denied: ./entrypoint.sh"
- Container exits immediately

**Solutions:**

#### A. Fix line endings (Windows issue)
```bash
fix_line_endings.bat
```

#### B. Rebuild image
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

### 7. 🔴 Database Connection Failed

**Symptoms:**
- Services can't connect to database
- Error: "could not connect to server"
- Error: "connection refused"

**Solutions:**

#### A. Check database is healthy
```bash
docker-compose ps db
```

Should show "healthy" status.

#### B. Check DATABASE_URL format
In `docker-compose.yml`, ensure it uses `db:5432` not `localhost:5432`:
```yaml
DATABASE_URL: postgresql://salla_user:password@db:5432/salla_optimizer
```

#### C. Wait longer for database
Database takes 10-30 seconds to initialize on first run.

```bash
docker-compose logs -f db
```

Wait for: "database system is ready to accept connections"

---

### 8. 🔴 Celery Worker Not Processing Tasks

**Symptoms:**
- Tasks stay in "pending" state
- No optimization runs happening
- Flower shows no workers

**Solutions:**

#### A. Check worker is running
```bash
docker-compose ps celery_worker
```

#### B. Check worker logs
```bash
docker-compose logs celery_worker
```

#### C. Restart worker
```bash
docker-compose restart celery_worker
```

#### D. Check Redis connection
```bash
docker-compose logs redis
```

---

### 9. 🔴 Dashboard Shows "No stores found"

**Symptoms:**
- Dashboard loads but shows no stores
- Empty dropdown

**Solutions:**

#### A. Onboard a store first
Visit: http://localhost:8000/oauth/authorize

#### B. Check database has stores
```bash
docker-compose exec web python -c "from database.db import get_db; from database.models import Store; db = next(get_db()); print(db.query(Store).count())"
```

#### C. Check database connection
```bash
docker-compose logs dashboard
```

---

### 10. 🔴 Build Fails with "No space left on device"

**Symptoms:**
- Docker build fails
- Error: "no space left on device"

**Solutions:**

#### A. Clean Docker system
```bash
docker system prune -a --volumes
```

#### B. Remove unused images
```bash
docker image prune -a
```

#### C. Check disk space
```bash
docker system df
```

---

## Advanced Debugging

### View Real-Time Logs for All Services
```bash
docker-compose logs -f
```

### View Logs for Specific Service
```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f db
```

### Execute Commands Inside Container
```bash
# Access database
docker-compose exec db psql -U salla_user -d salla_optimizer

# Access Python shell
docker-compose exec web python

# Check files
docker-compose exec web ls -la
```

### Inspect Container
```bash
docker inspect salla-api
docker inspect salla-postgres
```

### Check Network
```bash
docker network inspect salla-network
```

### Check Volumes
```bash
docker volume ls
docker volume inspect salla-postgres-data
```

---

## Health Check Commands

### Check All Services
```bash
docker-compose ps
```

### Check API Health
```bash
curl http://localhost:8000/health
```

### Check Dashboard Health
```bash
curl http://localhost:8501/_stcore/health
```

### Check Database
```bash
docker-compose exec db pg_isready -U salla_user
```

### Check Redis
```bash
docker-compose exec redis redis-cli ping
```

---

## Complete Reset (Nuclear Option)

If nothing works, do a complete reset:

```bash
# 1. Stop everything
docker-compose down -v

# 2. Remove all Salla-related containers
docker ps -a | findstr "salla" | awk '{print $1}' | xargs docker rm -f

# 3. Remove all Salla-related images
docker images | findstr "salla" | awk '{print $3}' | xargs docker rmi -f

# 4. Remove all Salla-related volumes
docker volume ls | findstr "salla" | awk '{print $2}' | xargs docker volume rm

# 5. Clean Docker system
docker system prune -a --volumes -f

# 6. Rebuild from scratch
rebuild.bat
```

---

## Getting Help

### 1. Run Diagnostics
```bash
diagnose.bat
```

### 2. Collect Logs
```bash
docker-compose logs > logs.txt
```

### 3. Check System Info
```bash
docker info > docker-info.txt
docker-compose config > compose-config.txt
```

### 4. Share Information
When asking for help, provide:
- Output from `diagnose.bat`
- Relevant logs from `check_logs.bat`
- Docker version: `docker --version`
- OS version: `ver`

---

## Prevention Tips

### 1. Always Use Helper Scripts
- ✅ Use `START_DOCKER.bat` instead of manual commands
- ✅ Use `diagnose.bat` before reporting issues
- ✅ Use `check_logs.bat` to view logs

### 2. Keep Docker Updated
- Update Docker Desktop regularly
- Check for updates: Docker Desktop → Settings → Software Updates

### 3. Monitor Resources
- Check Docker Desktop → Settings → Resources
- Ensure enough CPU, Memory, and Disk space allocated

### 4. Regular Maintenance
```bash
# Weekly cleanup
docker system prune -f

# Monthly deep clean
docker system prune -a --volumes
```

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Containers not showing | `diagnose.bat` |
| View logs | `check_logs.bat` |
| Force rebuild | `rebuild.bat` |
| Fix line endings | `fix_line_endings.bat` |
| Stop services | `STOP_DOCKER.bat` |
| Start services | `START_DOCKER.bat` |
| Check status | `docker-compose ps` |
| View all logs | `docker-compose logs -f` |
| Restart service | `docker-compose restart <service>` |
| Complete reset | `docker-compose down -v` |

---

**Still having issues?**

1. Run `diagnose.bat` and share the output
2. Run `check_logs.bat` and check for errors
3. Try `rebuild.bat` for a fresh start
4. Check this guide for your specific error message
