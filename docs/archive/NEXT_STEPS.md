# Next Steps - After Dependency Fix

## 🎯 Immediate Actions

### 1. Clean Build (Required)
Run the clean rebuild script to apply all fixes:

**Windows:**
```batch
REBUILD_CLEAN.bat
```

**Linux/Mac:**
```bash
chmod +x rebuild_clean.sh
./rebuild_clean.sh
```

**Expected Time:** 5-10 minutes

### 2. Verify Build Success
After build completes, verify everything works:

```bash
# Test dependencies
docker-compose run --rm web python test_dependencies.py

# Check installed versions
docker-compose run --rm web pip list | findstr /I "pydantic crewai langchain"
```

**Expected Output:**
```
✓ ALL TESTS PASSED - Dependencies are compatible!
pydantic: 2.4.x or 2.5.x
crewai: 0.28.8+
crewai-tools: 0.1.6+
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Verify Services Running
```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs -f
```

**All services should show "Up" or "Up (healthy)"**

## 🔍 Verification Checklist

- [ ] Build completed without errors
- [ ] `test_dependencies.py` shows all tests passed
- [ ] Pydantic version is 2.4.x or 2.5.x
- [ ] All services are running (`docker-compose ps`)
- [ ] API responds at http://localhost:8000
- [ ] Dashboard loads at http://localhost:8501
- [ ] Flower (Celery monitor) at http://localhost:5555
- [ ] No error logs in `docker-compose logs`

## 🚀 Post-Verification Steps

### 1. Initialize Database
```bash
docker-compose exec web python -c "from database.db import init_db; init_db()"
```

### 2. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs
```

### 3. Access Dashboard
Open browser: http://localhost:8501

### 4. Monitor Celery Tasks
Open browser: http://localhost:5555

## 📊 What Changed?

### Critical Fix
- **Pydantic version**: Changed from `>=2.6.1` to `>=2.4.1,<2.6.0`
- **Why**: `crewai-tools` requires `pydantic<2.6.0`

### Other Improvements
- Loosened version constraints for better compatibility
- Added fallback resolver in Dockerfile
- Created comprehensive documentation
- Added automated testing script

## 🎓 Understanding the Fix

### The Dependency Chain
```
crewai (0.28.8)
  └─ requires: pydantic>=2.4.1

crewai-tools (0.1.6)
  └─ requires: pydantic<2.6.0

Solution: pydantic>=2.4.1,<2.6.0
  └─ Satisfies both requirements!
```

### Why Legacy Resolver?
The legacy resolver is better at handling complex AI library dependency chains. If it fails, the Dockerfile automatically falls back to the standard resolver.

## 🛠️ Common Issues & Solutions

### Issue: Build Still Fails
**Solution:**
```bash
# Nuclear clean
docker system prune -af --volumes
docker-compose build --no-cache
```

### Issue: Services Won't Start
**Solution:**
```bash
# Check logs
docker-compose logs web

# Check environment
docker-compose config

# Restart specific service
docker-compose restart web
```

### Issue: Port Already in Use
**Solution (Windows):**
```batch
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <pid> /F
```

### Issue: Database Connection Error
**Solution:**
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `QUICK_START.md` | Fast reference for building and starting |
| `DOCKER_FIX_GUIDE.md` | Detailed explanation of the fix |
| `COMMANDS_REFERENCE.md` | Complete Docker command reference |
| `FIX_SUMMARY.md` | Summary of what was changed |
| `NEXT_STEPS.md` | This file - what to do next |

## 🎯 Development Workflow

### Daily Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Make code changes (hot reload enabled)

# Restart if needed
docker-compose restart web
```

### After Dependency Changes
```bash
# Rebuild specific service
docker-compose build web

# Restart with new build
docker-compose up -d --build web
```

### Testing
```bash
# Run tests
docker-compose exec web pytest

# Test specific file
docker-compose exec web pytest tests/test_api.py

# Test with coverage
docker-compose exec web pytest --cov
```

## 🔄 Maintenance Tasks

### Weekly
- Check logs for errors: `docker-compose logs --tail=100`
- Monitor resource usage: `docker stats`
- Backup database (see `COMMANDS_REFERENCE.md`)

### Monthly
- Update dependencies (test in dev first!)
- Clean unused images: `docker image prune -a`
- Review and rotate logs

### Before Production
- Run full test suite
- Check security vulnerabilities
- Verify all environment variables
- Test backup/restore procedures

## 🎉 Success!

If all verification steps pass, you're ready to:
1. ✅ Continue development
2. ✅ Deploy to staging/production
3. ✅ Onboard team members

## 🆘 Need Help?

1. **Check logs first**: `docker-compose logs -f`
2. **Run diagnostics**: `docker-compose exec web python test_dependencies.py`
3. **Review documentation**: See files listed above
4. **Check Docker resources**: Ensure 4GB+ RAM available
5. **Try clean rebuild**: `REBUILD_CLEAN.bat`

## 📞 Quick Commands

```bash
# Status check
docker-compose ps

# View logs
docker-compose logs -f

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Clean rebuild
REBUILD_CLEAN.bat  # or ./rebuild_clean.sh
```

---

**Current Status:** ✅ Fix Applied - Ready for Clean Build  
**Next Action:** Run `REBUILD_CLEAN.bat` (Windows) or `./rebuild_clean.sh` (Linux/Mac)  
**Expected Time:** 5-10 minutes for build  
**Documentation:** All guides created and ready
