# 🤖 Automated SaaS Model - Implementation Guide

## Overview
The Salla Price Optimizer now operates as a fully automated SaaS platform with proactive token management and multi-tenant background optimization.

---

## 🔄 Automated Token Lifecycle

### 1. Proactive Token Refresh

**Schedule:** Every 12 hours (configurable)

**Logic:**
- Checks all active stores for tokens expiring within 24 hours
- Automatically refreshes tokens before they expire
- Logs all refresh activities as "System Action"

**Implementation:**
```python
# scheduler/celery_app.py
'refresh-tokens-12h': {
    'task': 'scheduler.tasks.refresh_expired_tokens',
    'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
}
```

### 2. Error Handling

**Scenarios:**

**A. Token Refresh Fails (401 Unauthorized):**
- Store marked as `is_active = False`
- Activity log created: "System Action: Store deactivated - Token refresh unauthorized"
- Reason: Store likely uninstalled the app

**B. Invalid Refresh Token (400 Bad Request):**
- Store marked as `is_active = False`
- Activity log created: "System Action: Store deactivated - Invalid refresh token"

**C. Network Timeout:**
- Retry on next scheduled run
- Store remains active
- Error logged for monitoring

### 3. Token Health Monitoring

**Check Token Health:**
```python
from optimizer.token_manager import TokenManager

token_manager = TokenManager()
health = token_manager.check_token_health(store_id)

# Returns:
{
    'healthy': True/False,
    'reason': 'Token valid' | 'Token expired' | 'Token expires soon',
    'needs_refresh': True/False,
    'hours_until_expiry': 48.5
}
```

**Get System-Wide Status:**
```python
status = token_manager.get_token_status_summary()

# Returns:
{
    'total_stores': 10,
    'active_stores': 8,
    'inactive_stores': 2,
    'tokens_expiring_soon': 3,
    'tokens_expired': 0,
    'healthy_tokens': 5
}
```

---

## 🏢 Multi-Tenant Background Optimization

### 1. Store-Specific Context

**Each store gets:**
- Unique CrewAI instance
- Individual settings from database:
  - `min_profit_margin`
  - `automation_mode`
  - `risk_tolerance`
  - `update_frequency_hours`

**Implementation:**
```python
# optimizer/multi_tenant_optimizer.py

# Set store-specific environment
os.environ["MIN_PROFIT_MARGIN"] = str(store.min_profit_margin)
os.environ["AUTOMATION_MODE"] = store.automation_mode
os.environ["RISK_TOLERANCE"] = store.risk_tolerance

# Create LLM with store context
llm = LLM(
    model="gpt-4o",
    temperature=0,
    system_message=f"You are optimizing prices for {store.store_name}. "
                  f"Minimum profit margin: {store.min_profit_margin}%. "
                  f"Automation mode: {store.automation_mode}."
)

# Create unique crew for this store
crew = Crew(
    agents=[scout_agent, analyst_agent, executor_agent],
    tasks=[scout_task, analyst_task, executor_task],
    process=Process.sequential,
    context=f"Store: {store.store_name} (ID: {store.store_id})"
)
```

### 2. Zero-.env Dependency

**System Credentials Storage:**

**Option A: Database (Recommended)**
```sql
-- system_settings table
INSERT INTO system_settings (setting_key, setting_value, description)
VALUES 
  ('SALLA_CLIENT_ID', 'your-client-id', 'System-wide Salla OAuth Client ID'),
  ('SALLA_CLIENT_SECRET', 'your-secret', 'System-wide Salla OAuth Client Secret');
```

**Initialize from .env:**
```bash
python scripts/init_system_settings.py
```

This reads from `.env` once and stores in database.

**Option B: Environment Variables (Fallback)**
- System reads from environment if not in database
- Logs warning: "System credentials not in database, using environment fallback"

**Store-Specific Tokens:**
- NEVER stored in `.env`
- Always fetched from database per store
- Isolated per tenant

### 3. Optimization Schedule

**Three Scheduling Strategies:**

**A. Batch Optimization (Every 6 hours):**
```python
'optimize-all-stores-6h': {
    'task': 'scheduler.tasks.optimize_all_stores',
    'schedule': crontab(minute=0, hour='*/6'),
}
```
- Optimizes all active stores
- Skips stores in `manual` mode
- Queues individual tasks per store

**B. Smart Scheduling (Hourly):**
```python
'check-stores-hourly': {
    'task': 'scheduler.tasks.check_and_optimize_stores',
    'schedule': crontab(minute=0),  # Every hour
}
```
- Checks each store's `update_frequency_hours`
- Only optimizes stores that need it
- Respects individual schedules

**C. Manual Trigger:**
```python
from scheduler.tasks import manual_optimize
task = manual_optimize.delay(store_id)
```
- Triggered from dashboard
- Immediate execution
- Bypasses schedule

---

## 📊 Monitoring & Verification

### 1. Flower Dashboard

**Access:** http://localhost:5555

**Username:** admin  
**Password:** admin123

**What You Can See:**
- Active tasks (currently running)
- Scheduled tasks (upcoming)
- Completed tasks (history)
- Task success/failure rates
- Worker status
- Task execution times

**Key Tasks to Monitor:**
- `scheduler.tasks.refresh_expired_tokens` - Every 12 hours
- `scheduler.tasks.optimize_all_stores` - Every 6 hours
- `scheduler.tasks.check_and_optimize_stores` - Hourly
- `scheduler.tasks.optimize_store` - Per-store optimization
- `scheduler.tasks.cleanup_old_data` - Weekly

### 2. Activity Logs in Dashboard

**System Actions Visible:**

**Token Refresh:**
```
🟢 System Token Refresh
2026-02-13 14:30:00
System Action: OAuth token refreshed automatically (proactive)
```

**Store Deactivation:**
```
🔴 System Store Deactivated
2026-02-13 14:35:00
System Action: Store deactivated - Token refresh unauthorized
```

**Batch Refresh:**
```
🟢 System Token Refresh Batch
2026-02-13 14:00:00
System Action: Batch token refresh completed
```

**Filter by Activity Type:**
- `system_token_refresh` - Individual token refresh
- `system_token_refresh_batch` - Batch refresh summary
- `system_store_deactivated` - Store deactivation
- `optimization_completed` - Optimization runs

### 3. Database Queries

**Check Token Status:**
```sql
SELECT 
    store_id,
    store_name,
    is_active,
    token_expires_at,
    EXTRACT(EPOCH FROM (token_expires_at - NOW())) / 3600 AS hours_until_expiry
FROM stores
WHERE is_active = true
ORDER BY token_expires_at ASC;
```

**Recent System Actions:**
```sql
SELECT 
    activity_type,
    description,
    created_at,
    activity_metadata
FROM activity_logs
WHERE activity_type LIKE 'system_%'
ORDER BY created_at DESC
LIMIT 20;
```

**Optimization Statistics:**
```sql
SELECT 
    store_id,
    COUNT(*) as total_runs,
    AVG(duration_seconds) as avg_duration,
    SUM(products_updated) as total_updates
FROM optimization_runs
WHERE status = 'completed'
  AND started_at > NOW() - INTERVAL '7 days'
GROUP BY store_id;
```

---

## 🔧 Configuration

### 1. Token Refresh Frequency

**Change from 12 hours to 6 hours:**
```python
# scheduler/celery_app.py
'refresh-tokens-6h': {
    'task': 'scheduler.tasks.refresh_expired_tokens',
    'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
}
```

**Change proactive threshold from 24 hours to 48 hours:**
```python
# optimizer/token_manager.py
threshold = datetime.utcnow() + timedelta(hours=48)  # 48 hours instead of 24
```

### 2. Optimization Frequency

**Per-Store Settings (in database):**
```python
# Update via dashboard or API
store.update_frequency_hours = 12  # Optimize every 12 hours
```

**Global Batch (in Celery Beat):**
```python
# scheduler/celery_app.py
'optimize-all-stores-12h': {
    'task': 'scheduler.tasks.optimize_all_stores',
    'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
}
```

### 3. Automation Modes

**Manual:**
- No automatic optimization
- User must click "Run Now"
- All price changes require approval

**Semi-Auto:**
- Automatic optimization runs on schedule
- Low-risk changes auto-approved
- Medium/High-risk require approval

**Full-Auto:**
- Automatic optimization runs on schedule
- All changes auto-approved (except High-risk)
- Fully autonomous

---

## 🚀 Deployment Checklist

### Initial Setup

1. **Initialize Database:**
   ```bash
   python scripts/init_saas.py
   ```

2. **Store System Credentials:**
   ```bash
   python scripts/init_system_settings.py
   ```

3. **Start All Services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify Containers:**
   ```bash
   docker ps
   ```
   Should show 7 healthy containers.

5. **Check Flower:**
   ```
   http://localhost:5555
   ```
   Should show scheduled tasks.

6. **Check Dashboard:**
   ```
   http://localhost:8501
   ```
   Should show activity logs.

### Ongoing Monitoring

**Daily:**
- Check Flower for failed tasks
- Review activity logs for system actions
- Verify token refresh is running

**Weekly:**
- Review optimization statistics
- Check for deactivated stores
- Verify data cleanup is running

**Monthly:**
- Review system performance
- Optimize database if needed
- Update credentials if changed

---

## 🎯 Success Criteria

System is fully automated when:

- ✅ Tokens refresh automatically every 12 hours
- ✅ Stores deactivate automatically on auth failure
- ✅ Each store gets unique CrewAI instance
- ✅ No user tokens in `.env` file
- ✅ System credentials in database
- ✅ Activity logs show "System Action" entries
- ✅ Flower shows scheduled tasks
- ✅ Optimization runs respect store settings

---

## 📞 Troubleshooting

### Tokens Not Refreshing

**Check:**
1. Celery Beat is running: `docker ps | grep celery-beat`
2. Task is scheduled: Check Flower dashboard
3. System credentials exist: Query `system_settings` table
4. Logs: `docker logs salla-celery-beat`

**Fix:**
```bash
docker-compose restart celery_beat
```

### Store Deactivated Unexpectedly

**Reasons:**
1. Store uninstalled app
2. OAuth access revoked
3. Invalid refresh token

**Check:**
```sql
SELECT * FROM activity_logs 
WHERE store_id = 'YOUR_STORE_ID' 
  AND activity_type = 'system_store_deactivated'
ORDER BY created_at DESC;
```

**Reactivate:**
- Store must re-authorize via OAuth
- Visit: `http://localhost:8000/oauth/authorize`

### Optimization Not Running

**Check:**
1. Store is active: `is_active = true`
2. Automation mode: Not `manual`
3. Celery worker running: `docker ps | grep celery-worker`
4. Flower dashboard: Check for errors

**Fix:**
```bash
docker-compose restart celery_worker
```

---

**Status:** ✅ Fully Automated SaaS Model Implemented

**Next Steps:** Monitor system for 24 hours to verify automation
