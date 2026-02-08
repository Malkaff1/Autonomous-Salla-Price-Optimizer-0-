"""
Celery tasks for automated price optimization
"""

from celery import Task
from datetime import datetime, timedelta
import logging
import time
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler.celery_app import celery_app
from database.db import get_db, DatabaseManager
from database.models import Store, OptimizationRun, ActivityLog
from optimizer.multi_tenant_optimizer import MultiTenantOptimizer

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True, name='scheduler.tasks.optimize_store')
def optimize_store(self, store_id: str, run_type: str = 'scheduled'):
    """
    Optimize prices for a single store
    
    Args:
        store_id: Salla store ID
        run_type: 'scheduled', 'manual', or 'triggered'
    """
    logger.info(f"🚀 Starting optimization for store: {store_id}")
    
    start_time = time.time()
    
    try:
        # Get store from database
        with get_db() as db:
            store = db.query(Store).filter(Store.store_id == store_id).first()
            
            if not store:
                logger.error(f"Store {store_id} not found")
                return {"status": "error", "message": "Store not found"}
            
            if not store.is_active:
                logger.info(f"Store {store_id} is inactive, skipping")
                return {"status": "skipped", "message": "Store is inactive"}
            
            # Check if token is expired
            if store.is_token_expired():
                logger.warning(f"Token expired for store {store_id}")
                # Try to refresh token
                from optimizer.token_manager import TokenManager
                token_manager = TokenManager()
                success = token_manager.refresh_store_token(store_id)
                
                if not success:
                    logger.error(f"Failed to refresh token for store {store_id}")
                    return {"status": "error", "message": "Token expired and refresh failed"}
            
            # Create optimization run record
            run = OptimizationRun(
                store_id=store_id,
                run_type=run_type,
                status='running'
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            run_id = run.id
        
        # Run optimization
        optimizer = MultiTenantOptimizer()
        result = optimizer.optimize_single_store(store_id)
        
        # Calculate duration
        duration = int(time.time() - start_time)
        
        # Update run record with results
        with get_db() as db:
            run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
            if run:
                run.status = 'completed' if result.get('success') else 'failed'
                run.completed_at = datetime.utcnow()
                run.duration_seconds = duration
                run.products_analyzed = result.get('products_analyzed', 0)
                run.products_updated = result.get('products_updated', 0)
                run.products_skipped = result.get('products_skipped', 0)
                run.competitors_found = result.get('competitors_found', 0)
                run.error_message = result.get('error_message')
                db.commit()
            
            # Update store's last optimization run
            store = db.query(Store).filter(Store.store_id == store_id).first()
            if store:
                store.last_optimization_run = datetime.utcnow()
                db.commit()
            
            # Log activity
            activity = ActivityLog(
                store_id=store_id,
                activity_type='optimization_completed',
                description=f"Optimization run completed in {duration}s",
                metadata=result
            )
            db.add(activity)
            db.commit()
        
        logger.info(f"✅ Optimization completed for store {store_id} in {duration}s")
        
        return {
            "status": "success",
            "store_id": store_id,
            "duration": duration,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Error optimizing store {store_id}: {str(e)}")
        
        # Update run record with error
        try:
            with get_db() as db:
                run = db.query(OptimizationRun).filter(
                    OptimizationRun.store_id == store_id,
                    OptimizationRun.status == 'running'
                ).order_by(OptimizationRun.started_at.desc()).first()
                
                if run:
                    run.status = 'failed'
                    run.completed_at = datetime.utcnow()
                    run.error_message = str(e)
                    run.duration_seconds = int(time.time() - start_time)
                    db.commit()
        except:
            pass
        
        return {
            "status": "error",
            "store_id": store_id,
            "error": str(e)
        }


@celery_app.task(name='scheduler.tasks.optimize_all_stores')
def optimize_all_stores():
    """
    Optimize prices for all active stores
    Runs every 6 hours via Celery Beat
    """
    logger.info("🔄 Starting optimization for all active stores")
    
    try:
        stores = DatabaseManager.get_active_stores()
        
        if not stores:
            logger.info("No active stores found")
            return {"status": "success", "stores_processed": 0}
        
        logger.info(f"Found {len(stores)} active stores")
        
        # Queue optimization tasks for each store
        results = []
        for store in stores:
            # Check automation mode
            if store.automation_mode == 'manual':
                logger.info(f"Skipping store {store.store_id} (manual mode)")
                continue
            
            # Queue task
            task = optimize_store.delay(store.store_id, run_type='scheduled')
            results.append({
                "store_id": store.store_id,
                "task_id": task.id
            })
            logger.info(f"Queued optimization for store {store.store_id}")
        
        return {
            "status": "success",
            "stores_processed": len(results),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error in optimize_all_stores: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name='scheduler.tasks.check_and_optimize_stores')
def check_and_optimize_stores():
    """
    Check which stores need optimization based on their schedule
    Runs every hour via Celery Beat
    """
    logger.info("🔍 Checking stores needing optimization")
    
    try:
        stores = DatabaseManager.get_stores_needing_optimization()
        
        if not stores:
            logger.info("No stores need optimization at this time")
            return {"status": "success", "stores_processed": 0}
        
        logger.info(f"Found {len(stores)} stores needing optimization")
        
        # Queue optimization tasks
        results = []
        for store in stores:
            task = optimize_store.delay(store.store_id, run_type='scheduled')
            results.append({
                "store_id": store.store_id,
                "task_id": task.id
            })
            logger.info(f"Queued optimization for store {store.store_id}")
        
        return {
            "status": "success",
            "stores_processed": len(results),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error in check_and_optimize_stores: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name='scheduler.tasks.refresh_expired_tokens')
def refresh_expired_tokens():
    """
    Refresh expired OAuth tokens for all stores
    Runs daily at 2 AM via Celery Beat
    """
    logger.info("🔄 Refreshing expired tokens")
    
    try:
        from optimizer.token_manager import TokenManager
        token_manager = TokenManager()
        
        with get_db() as db:
            # Get stores with expired or soon-to-expire tokens
            threshold = datetime.utcnow() + timedelta(hours=24)
            stores = db.query(Store).filter(
                Store.is_active == True,
                Store.token_expires_at < threshold
            ).all()
            
            if not stores:
                logger.info("No tokens need refreshing")
                return {"status": "success", "tokens_refreshed": 0}
            
            logger.info(f"Found {len(stores)} stores with expiring tokens")
            
            refreshed = 0
            failed = 0
            
            for store in stores:
                success = token_manager.refresh_store_token(store.store_id)
                if success:
                    refreshed += 1
                    logger.info(f"✅ Refreshed token for store {store.store_id}")
                else:
                    failed += 1
                    logger.error(f"❌ Failed to refresh token for store {store.store_id}")
            
            return {
                "status": "success",
                "tokens_refreshed": refreshed,
                "tokens_failed": failed
            }
            
    except Exception as e:
        logger.error(f"Error in refresh_expired_tokens: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name='scheduler.tasks.cleanup_old_data')
def cleanup_old_data():
    """
    Clean up old data from database
    Runs weekly on Sunday at 3 AM via Celery Beat
    """
    logger.info("🧹 Cleaning up old data")
    
    try:
        with get_db() as db:
            # Delete old activity logs (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            deleted_logs = db.query(ActivityLog).filter(
                ActivityLog.created_at < cutoff_date
            ).delete()
            
            # Delete old competitor data (older than 30 days)
            from database.models import Competitor
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted_competitors = db.query(Competitor).filter(
                Competitor.last_checked < cutoff_date
            ).delete()
            
            # Delete old optimization runs (older than 60 days)
            cutoff_date = datetime.utcnow() - timedelta(days=60)
            deleted_runs = db.query(OptimizationRun).filter(
                OptimizationRun.started_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"✅ Cleaned up: {deleted_logs} logs, {deleted_competitors} competitors, {deleted_runs} runs")
            
            return {
                "status": "success",
                "deleted_logs": deleted_logs,
                "deleted_competitors": deleted_competitors,
                "deleted_runs": deleted_runs
            }
            
    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name='scheduler.tasks.manual_optimize')
def manual_optimize(store_id: str):
    """
    Manually trigger optimization for a specific store
    Called from dashboard or API
    """
    logger.info(f"🎯 Manual optimization triggered for store {store_id}")
    return optimize_store(store_id, run_type='manual')
