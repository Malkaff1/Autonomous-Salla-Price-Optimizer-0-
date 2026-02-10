# 🚀 START HERE - Salla Price Optimizer

## ⚡ Quick Start (3 Steps)

### Step 1: Open Docker Desktop
Make sure Docker Desktop is running (green icon in system tray)

### Step 2: Run This File
Double-click: **`START_DOCKER.bat`**

### Step 3: View Containers
1. Open **Docker Desktop**
2. Click **"Containers"** on the left
3. You'll see **7 containers** running under "salla-price-optimizer"

---

## 🎯 Access Your Services

| Service | URL | Description |
|---------|-----|-------------|
| 🛍️ **Dashboard** | http://localhost:8501 | Main SaaS Dashboard |
| 🔐 **API** | http://localhost:8000 | OAuth & REST API |
| 🌸 **Flower** | http://localhost:5555 | Task Monitor |
| 📊 **API Docs** | http://localhost:8000/docs | API Documentation |

---

## ❌ If Containers Don't Show

### Option 1: Run Diagnostics
```bash
diagnose.bat
```
This will check everything and tell you what's wrong.

### Option 2: View Logs
```bash
check_logs.bat
```
This will show you error messages.

### Option 3: Force Rebuild
```bash
rebuild.bat
```
This will delete everything and start fresh.

---

## 📚 Need Help?

| Problem | Solution File |
|---------|--------------|
| Containers not showing | `TROUBLESHOOTING.md` |
| Want to understand system | `SYSTEM_STATUS.md` |
| Arabic guide | `README_AR.md` |
| Deployment checklist | `DEPLOYMENT_CHECKLIST.md` |
| What was fixed | `FIXES_APPLIED.md` |

---

## 🔧 Useful Commands

```bash
# Start everything
START_DOCKER.bat

# Stop everything
STOP_DOCKER.bat

# View logs
check_logs.bat

# Run diagnostics
diagnose.bat

# Force rebuild
rebuild.bat

# Fix line endings (Windows)
fix_line_endings.bat
```

---

## ✅ Success Checklist

After running `START_DOCKER.bat`, you should see:

- ✅ 7 containers in Docker Desktop
- ✅ All containers show "Running" status
- ✅ Dashboard opens at http://localhost:8501
- ✅ API responds at http://localhost:8000
- ✅ No errors in logs

---

## 🆘 Still Having Issues?

1. **Run diagnostics:**
   ```bash
   diagnose.bat
   ```

2. **Check logs:**
   ```bash
   check_logs.bat
   ```

3. **Read troubleshooting guide:**
   Open `TROUBLESHOOTING.md`

4. **Try complete rebuild:**
   ```bash
   rebuild.bat
   ```

---

## 📦 The 7 Containers

1. **salla-postgres** - Database (PostgreSQL)
2. **salla-redis** - Cache (Redis)
3. **salla-api** - API Server (FastAPI)
4. **salla-celery-worker** - Background Jobs
5. **salla-celery-beat** - Task Scheduler
6. **salla-flower** - Task Monitor
7. **salla-dashboard** - Dashboard (Streamlit)

---

## 🎉 That's It!

Just run `START_DOCKER.bat` and you're good to go!

**Next:** Open http://localhost:8501 and start using your price optimizer!
