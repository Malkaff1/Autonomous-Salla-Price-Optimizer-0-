# Docker Dependency Conflict Fix Guide

## Problem Summary
The Docker build was failing with a `ResolutionImpossible` error due to version conflicts between:
- `crewai` (requires `pydantic>=2.4.1`)
- `crewai-tools` (requires `pydantic<2.6.0`)
- Other dependencies with conflicting version requirements

## Solution Applied

### 1. Updated `requirements_saas.txt`
**Key Changes:**
- **Pydantic**: Changed from `>=2.6.1,<3.0.0` to `>=2.4.1,<2.6.0` (compatible with both crewai and crewai-tools)
- **Langchain**: Loosened from `>=0.1.10` to `>=0.1.0` for better compatibility
- **OpenAI**: Loosened from `>=1.13.3` to `>=1.13.0`
- **FastAPI**: Expanded range to `<0.115.0`
- **HTTPX**: Expanded range to `<0.28.0`

### 2. Updated `Dockerfile`
**Key Changes:**
- Added fallback strategy: tries legacy resolver first, then backtracking resolver
- Improved error handling with informative messages
- Maintained separate layer for pip/setuptools/wheel upgrade for better caching

### 3. Created Clean Rebuild Scripts

#### Windows: `REBUILD_CLEAN.bat`
```batch
REBUILD_CLEAN.bat
```

#### Linux/Mac: `rebuild_clean.sh`
```bash
chmod +x rebuild_clean.sh
./rebuild_clean.sh
```

## Step-by-Step Rebuild Process

### Option 1: Using the Clean Rebuild Script (Recommended)

**Windows:**
```batch
REBUILD_CLEAN.bat
```

**Linux/Mac:**
```bash
chmod +x rebuild_clean.sh
./rebuild_clean.sh
```

This script will:
1. Stop all running containers
2. Remove stopped containers
3. Remove dangling images
4. Clear build cache
5. Remove unused volumes
6. Build from scratch with no cache

### Option 2: Manual Commands

```bash
# Stop everything
docker-compose down -v

# Deep clean
docker container prune -f
docker image prune -f
docker builder prune -f
docker volume prune -f

# Rebuild from scratch
docker-compose build --no-cache --progress=plain

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Verification Steps

### 1. Check Build Success
```bash
docker-compose build web
```
Should complete without `ResolutionImpossible` errors.

### 2. Check Installed Versions
```bash
docker-compose run --rm web pip list | grep -E "pydantic|crewai|langchain"
```

Expected output:
```
crewai                    0.28.8
crewai-tools              0.1.6
langchain                 0.1.x
pydantic                  2.5.x (or 2.4.x)
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Check Service Health
```bash
docker-compose ps
docker-compose logs web
```

## Troubleshooting

### If Build Still Fails

1. **Check Docker Resources:**
   - Ensure Docker has enough memory (4GB+ recommended)
   - Check disk space

2. **Try Nuclear Clean:**
   ```bash
   docker system prune -a --volumes -f
   docker-compose build --no-cache
   ```

3. **Check Network:**
   - Ensure PyPI is accessible
   - Try with VPN disabled if applicable

4. **Manual Dependency Test:**
   ```bash
   docker run --rm python:3.11-slim pip install pydantic==2.5.3 crewai==0.28.8 crewai-tools==0.1.6
   ```

### If Services Don't Start

1. **Check Logs:**
   ```bash
   docker-compose logs web
   docker-compose logs celery
   docker-compose logs dashboard
   ```

2. **Check Environment Variables:**
   ```bash
   docker-compose config
   ```

3. **Verify Database Connection:**
   ```bash
   docker-compose exec db psql -U salla_user -d salla_optimizer -c "SELECT 1;"
   ```

## Key Compatibility Matrix

| Package | Version Range | Reason |
|---------|--------------|--------|
| pydantic | 2.4.1 - 2.5.x | Compatible with both crewai and crewai-tools |
| crewai | 0.28.8 - 0.29.x | Core agent framework |
| crewai-tools | 0.1.6 - 0.1.x | Requires pydantic<2.6.0 |
| langchain | 0.1.0 - 0.1.x | Flexible for compatibility |
| fastapi | 0.104.0 - 0.114.x | Web framework |

## Next Steps

After successful build:

1. **Initialize Database:**
   ```bash
   docker-compose exec web python -c "from database.db import init_db; init_db()"
   ```

2. **Access Services:**
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501
   - Flower (Celery Monitor): http://localhost:5555

3. **Run Tests:**
   ```bash
   docker-compose exec web pytest
   ```

## Prevention Tips

1. **Pin Critical Dependencies:** Keep pydantic pinned to compatible range
2. **Test Before Commit:** Always test `docker-compose build` before committing
3. **Use Dependabot:** Set up automated dependency updates with testing
4. **Document Conflicts:** Keep this guide updated with any new conflicts

## Support

If issues persist:
1. Check `docker-compose logs -f`
2. Review `pip list` output in container
3. Verify `.env` file configuration
4. Check Docker daemon logs
