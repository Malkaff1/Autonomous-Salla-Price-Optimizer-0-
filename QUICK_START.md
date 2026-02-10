# Quick Start Guide - Docker Build Fix

## The Problem
Docker build was failing with `ResolutionImpossible` error due to conflicting dependency versions between CrewAI packages and Pydantic.

## The Solution (Applied)

### ✅ Fixed Files
1. **requirements_saas.txt** - Adjusted pydantic to `>=2.4.1,<2.6.0` (compatible range)
2. **Dockerfile** - Added fallback resolver strategy
3. **REBUILD_CLEAN.bat** - Deep clean and rebuild script (Windows)
4. **rebuild_clean.sh** - Deep clean and rebuild script (Linux/Mac)

## 🚀 How to Build Now

### Windows (Recommended)
```batch
REBUILD_CLEAN.bat
```

### Linux/Mac
```bash
chmod +x rebuild_clean.sh
./rebuild_clean.sh
```

### Manual (All Platforms)
```bash
# Clean everything
docker-compose down -v
docker system prune -af --volumes

# Build fresh
docker-compose build --no-cache

# Start services
docker-compose up -d
```

## ✅ Verify Build Success

### 1. Check if build completed
```bash
docker-compose build web
```
Should finish without errors.

### 2. Test dependencies inside container
```bash
docker-compose run --rm web python test_dependencies.py
```
Should show all tests passing.

### 3. Check installed versions
```bash
docker-compose run --rm web pip list | findstr /I "pydantic crewai langchain"
```

Expected:
- pydantic: 2.4.x or 2.5.x
- crewai: 0.28.8+
- crewai-tools: 0.1.6+
- langchain: 0.1.x

## 🎯 Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 🌐 Access Points

- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **Celery Monitor**: http://localhost:5555
- **API Docs**: http://localhost:8000/docs

## 🔧 Troubleshooting

### Build still fails?
1. Check Docker has 4GB+ RAM
2. Check disk space
3. Try: `docker system prune -af --volumes`
4. Restart Docker Desktop

### Services won't start?
```bash
# Check logs
docker-compose logs web
docker-compose logs db

# Check environment
docker-compose config

# Restart specific service
docker-compose restart web
```

### Database issues?
```bash
# Initialize database
docker-compose exec web python -c "from database.db import init_db; init_db()"

# Check connection
docker-compose exec db psql -U salla_user -d salla_optimizer -c "SELECT 1;"
```

## 📚 More Help

- **Detailed Fix Guide**: See `DOCKER_FIX_GUIDE.md`
- **Docker Commands**: See `DOCKER_COMMANDS.md`
- **Deployment Guide**: See `DOCKER_DEPLOYMENT.md`
- **General Troubleshooting**: See `TROUBLESHOOTING.md`

## 🎉 Success Checklist

- [ ] Build completes without errors
- [ ] `test_dependencies.py` passes all tests
- [ ] All services start successfully
- [ ] Can access API at http://localhost:8000
- [ ] Can access Dashboard at http://localhost:8501
- [ ] Database connection works

---

**Need more help?** Check the logs: `docker-compose logs -f`
