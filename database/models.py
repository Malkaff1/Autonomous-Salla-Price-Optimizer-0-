"""
SQLAlchemy ORM Models for Multi-Tenant Salla Price Optimizer
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Decimal, Boolean, 
    DateTime, ForeignKey, Index, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Store(Base):
    """Main store/user table with OAuth credentials"""
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), unique=True, nullable=False, index=True)
    store_name = Column(String(255), nullable=False)
    store_domain = Column(String(255))
    owner_email = Column(String(255))
    owner_name = Column(String(255))
    
    # OAuth
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    client_id = Column(String(100))
    client_secret = Column(String(255))
    
    # Settings
    min_profit_margin = Column(Decimal(5, 2), default=10.00)
    automation_mode = Column(String(20), default='manual')  # manual, semi-auto, full-auto
    update_frequency_hours = Column(Integer, default=12)
    risk_tolerance = Column(String(20), default='low')  # low, medium, high
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    subscription_plan = Column(String(50), default='free')
    last_optimization_run = Column(DateTime, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="store", cascade="all, delete-orphan")
    pricing_decisions = relationship("PricingDecision", back_populates="store", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="store", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="store", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Store(store_id='{self.store_id}', name='{self.store_name}')>"
    
    def is_token_expired(self):
        """Check if access token is expired"""
        return datetime.utcnow() >= self.token_expires_at
    
    def needs_optimization(self):
        """Check if store needs optimization run"""
        if not self.is_active or self.automation_mode == 'manual':
            return False
        
        if not self.last_optimization_run:
            return True
        
        hours_since_last_run = (datetime.utcnow() - self.last_optimization_run).total_seconds() / 3600
        return hours_since_last_run >= self.update_frequency_hours


class Product(Base):
    """Store-specific product catalog"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), ForeignKey('stores.store_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String(50), nullable=False)
    
    # Product details
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(255))
    sku = Column(String(100))
    
    # Pricing
    current_price = Column(Decimal(10, 2), nullable=False)
    cost_price = Column(Decimal(10, 2))
    suggested_price = Column(Decimal(10, 2))
    
    # Status
    status = Column(String(50), default='active')
    is_tracked = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="products")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_product', 'store_id', 'product_id', unique=True),
        Index('idx_store_tracked', 'store_id', 'is_tracked'),
    )
    
    def __repr__(self):
        return f"<Product(id='{self.product_id}', name='{self.name}', price={self.current_price})>"


class Competitor(Base):
    """Competitor pricing data"""
    __tablename__ = 'competitors'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), ForeignKey('stores.store_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String(50), nullable=False)
    
    # Competitor details
    competitor_name = Column(String(255), nullable=False)
    competitor_url = Column(Text)
    competitor_price = Column(Decimal(10, 2), nullable=False)
    competitor_platform = Column(String(50), default='Salla')
    
    # Data quality
    confidence_score = Column(Decimal(3, 2), default=0.80)
    is_valid = Column(Boolean, default=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=func.now())
    last_checked = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    store = relationship("Store", back_populates="competitors")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_product_competitor', 'store_id', 'product_id'),
    )
    
    def __repr__(self):
        return f"<Competitor(name='{self.competitor_name}', price={self.competitor_price})>"


class PricingDecision(Base):
    """Audit trail of pricing decisions"""
    __tablename__ = 'pricing_decisions'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), ForeignKey('stores.store_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String(50), nullable=False)
    
    # Decision details
    old_price = Column(Decimal(10, 2), nullable=False)
    suggested_price = Column(Decimal(10, 2), nullable=False)
    final_price = Column(Decimal(10, 2))
    
    # Strategy
    strategy_used = Column(String(50))  # undercut, match, premium, hold
    risk_level = Column(String(20))  # low, medium, high
    profit_margin_percentage = Column(Decimal(5, 2))
    
    # Execution
    action_taken = Column(String(50), index=True)  # updated, skipped, failed, pending
    reasoning = Column(Text)
    
    # Timestamps
    decided_at = Column(DateTime, default=func.now(), index=True)
    executed_at = Column(DateTime)
    
    # Relationships
    store = relationship("Store", back_populates="pricing_decisions")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_decisions', 'store_id', 'decided_at'),
    )
    
    def __repr__(self):
        return f"<PricingDecision(product='{self.product_id}', action='{self.action_taken}')>"


class OptimizationRun(Base):
    """History of optimization job executions"""
    __tablename__ = 'optimization_runs'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), ForeignKey('stores.store_id', ondelete='CASCADE'), nullable=False)
    
    # Run details
    run_type = Column(String(50), default='scheduled')  # scheduled, manual, triggered
    status = Column(String(50), default='running', index=True)  # running, completed, failed
    
    # Statistics
    products_analyzed = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
    products_skipped = Column(Integer, default=0)
    competitors_found = Column(Integer, default=0)
    
    # Performance
    duration_seconds = Column(Integer)
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime)
    
    # Relationships
    store = relationship("Store", back_populates="optimization_runs")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_runs', 'store_id', 'started_at'),
    )
    
    def __repr__(self):
        return f"<OptimizationRun(store='{self.store_id}', status='{self.status}')>"


class ActivityLog(Base):
    """User activity and system event logs"""
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(String(50), ForeignKey('stores.store_id', ondelete='CASCADE'), nullable=False)
    
    # Activity details
    activity_type = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    metadata = Column(JSON)  # Flexible JSON storage
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    store = relationship("Store", back_populates="activity_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_activity', 'store_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ActivityLog(type='{self.activity_type}', store='{self.store_id}')>"


class SystemSetting(Base):
    """Global system configuration"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSetting(key='{self.setting_key}', value='{self.setting_value}')>"
