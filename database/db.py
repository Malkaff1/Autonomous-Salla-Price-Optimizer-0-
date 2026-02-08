"""
Database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from dotenv import load_dotenv

from database.models import Base

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/salla_optimizer"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe session
Session = scoped_session(SessionLocal)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def drop_db():
    """Drop all tables - USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped")


@contextmanager
def get_db():
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as db:
            store = db.query(Store).first()
    """
    db = Session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session():
    """
    Get database session for dependency injection.
    
    Usage (FastAPI):
        @app.get("/stores")
        def get_stores(db: Session = Depends(get_db_session)):
            return db.query(Store).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database utility functions
class DatabaseManager:
    """Helper class for common database operations"""
    
    @staticmethod
    def get_store_by_id(store_id: str):
        """Get store by Salla store ID"""
        with get_db() as db:
            from database.models import Store
            return db.query(Store).filter(Store.store_id == store_id).first()
    
    @staticmethod
    def get_active_stores():
        """Get all active stores"""
        with get_db() as db:
            from database.models import Store
            return db.query(Store).filter(Store.is_active == True).all()
    
    @staticmethod
    def get_stores_needing_optimization():
        """Get stores that need optimization run"""
        with get_db() as db:
            from database.models import Store
            stores = db.query(Store).filter(Store.is_active == True).all()
            return [store for store in stores if store.needs_optimization()]
    
    @staticmethod
    def create_store(store_data: dict):
        """Create new store record"""
        with get_db() as db:
            from database.models import Store
            store = Store(**store_data)
            db.add(store)
            db.commit()
            db.refresh(store)
            return store
    
    @staticmethod
    def update_store_tokens(store_id: str, access_token: str, refresh_token: str, expires_at):
        """Update store OAuth tokens"""
        with get_db() as db:
            from database.models import Store
            store = db.query(Store).filter(Store.store_id == store_id).first()
            if store:
                store.access_token = access_token
                store.refresh_token = refresh_token
                store.token_expires_at = expires_at
                db.commit()
                return store
            return None
    
    @staticmethod
    def log_activity(store_id: str, activity_type: str, description: str, metadata: dict = None):
        """Log user activity"""
        with get_db() as db:
            from database.models import ActivityLog
            log = ActivityLog(
                store_id=store_id,
                activity_type=activity_type,
                description=description,
                metadata=metadata
            )
            db.add(log)
            db.commit()
    
    @staticmethod
    def create_optimization_run(store_id: str, run_type: str = 'scheduled'):
        """Create new optimization run record"""
        with get_db() as db:
            from database.models import OptimizationRun
            run = OptimizationRun(
                store_id=store_id,
                run_type=run_type,
                status='running'
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            return run
    
    @staticmethod
    def complete_optimization_run(run_id: int, stats: dict, status: str = 'completed'):
        """Complete optimization run with statistics"""
        with get_db() as db:
            from database.models import OptimizationRun
            from datetime import datetime
            
            run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
            if run:
                run.status = status
                run.completed_at = datetime.utcnow()
                run.products_analyzed = stats.get('products_analyzed', 0)
                run.products_updated = stats.get('products_updated', 0)
                run.products_skipped = stats.get('products_skipped', 0)
                run.competitors_found = stats.get('competitors_found', 0)
                run.duration_seconds = stats.get('duration_seconds', 0)
                run.error_message = stats.get('error_message')
                db.commit()
                return run
            return None


if __name__ == "__main__":
    # Initialize database when run directly
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database setup complete!")
