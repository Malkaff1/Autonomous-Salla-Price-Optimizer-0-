-- Multi-Tenant Salla Price Optimizer Database Schema
-- PostgreSQL 14+

-- 1. Users/Stores Table
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) UNIQUE NOT NULL,  -- Salla store ID
    store_name VARCHAR(255) NOT NULL,
    store_domain VARCHAR(255),
    owner_email VARCHAR(255),
    owner_name VARCHAR(255),
    
    -- OAuth Credentials
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    
    -- App Configuration
    client_id VARCHAR(100),
    client_secret VARCHAR(255),
    
    -- User Settings
    min_profit_margin DECIMAL(5,2) DEFAULT 10.00,  -- Minimum profit margin %
    automation_mode VARCHAR(20) DEFAULT 'manual',  -- 'manual', 'semi-auto', 'full-auto'
    update_frequency_hours INTEGER DEFAULT 12,     -- How often to run optimizer
    risk_tolerance VARCHAR(20) DEFAULT 'low',      -- 'low', 'medium', 'high'
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    subscription_plan VARCHAR(50) DEFAULT 'free',  -- 'free', 'basic', 'premium'
    last_optimization_run TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_store_id (store_id),
    INDEX idx_is_active (is_active),
    INDEX idx_last_run (last_optimization_run)
);

-- 2. Products Table (Store-specific)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,  -- Salla product ID
    
    -- Product Details
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    sku VARCHAR(100),
    
    -- Pricing
    current_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    suggested_price DECIMAL(10,2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',
    is_tracked BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE(store_id, product_id),
    
    -- Indexes
    INDEX idx_store_product (store_id, product_id),
    INDEX idx_is_tracked (is_tracked)
);

-- 3. Competitor Data Table
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    
    -- Competitor Details
    competitor_name VARCHAR(255) NOT NULL,
    competitor_url TEXT,
    competitor_price DECIMAL(10,2) NOT NULL,
    competitor_platform VARCHAR(50) DEFAULT 'Salla',
    
    -- Data Quality
    confidence_score DECIMAL(3,2) DEFAULT 0.80,
    is_valid BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_store_product_competitor (store_id, product_id),
    INDEX idx_discovered_at (discovered_at)
);

-- 4. Pricing Decisions Table (Audit Trail)
CREATE TABLE pricing_decisions (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    
    -- Decision Details
    old_price DECIMAL(10,2) NOT NULL,
    suggested_price DECIMAL(10,2) NOT NULL,
    final_price DECIMAL(10,2),
    
    -- Strategy
    strategy_used VARCHAR(50),  -- 'undercut', 'match', 'premium', 'hold'
    risk_level VARCHAR(20),     -- 'low', 'medium', 'high'
    profit_margin_percentage DECIMAL(5,2),
    
    -- Execution
    action_taken VARCHAR(50),   -- 'updated', 'skipped', 'failed', 'pending'
    reasoning TEXT,
    
    -- Timestamps
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_store_decisions (store_id, decided_at),
    INDEX idx_action_taken (action_taken)
);

-- 5. Optimization Runs Table (Job History)
CREATE TABLE optimization_runs (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    
    -- Run Details
    run_type VARCHAR(50) DEFAULT 'scheduled',  -- 'scheduled', 'manual', 'triggered'
    status VARCHAR(50) DEFAULT 'running',      -- 'running', 'completed', 'failed'
    
    -- Statistics
    products_analyzed INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_skipped INTEGER DEFAULT 0,
    competitors_found INTEGER DEFAULT 0,
    
    -- Performance
    duration_seconds INTEGER,
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_store_runs (store_id, started_at),
    INDEX idx_status (status)
);

-- 6. User Activity Logs
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    
    -- Activity Details
    activity_type VARCHAR(100) NOT NULL,  -- 'login', 'settings_changed', 'manual_override', etc.
    description TEXT,
    metadata JSONB,  -- Flexible JSON storage for additional data
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_store_activity (store_id, created_at),
    INDEX idx_activity_type (activity_type)
);

-- 7. System Settings (Global Configuration)
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('default_update_frequency', '12', 'Default hours between optimization runs'),
('max_concurrent_runs', '5', 'Maximum concurrent optimization jobs'),
('api_rate_limit_per_minute', '60', 'Salla API rate limit'),
('competitor_search_max_results', '10', 'Maximum competitor results per product');

-- 8. Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_stores_updated_at BEFORE UPDATE ON stores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. Create views for common queries
CREATE VIEW active_stores_summary AS
SELECT 
    s.store_id,
    s.store_name,
    s.automation_mode,
    s.last_optimization_run,
    COUNT(DISTINCT p.product_id) as total_products,
    COUNT(DISTINCT CASE WHEN p.is_tracked THEN p.product_id END) as tracked_products,
    MAX(or.completed_at) as last_successful_run
FROM stores s
LEFT JOIN products p ON s.store_id = p.store_id
LEFT JOIN optimization_runs or ON s.store_id = or.store_id AND or.status = 'completed'
WHERE s.is_active = TRUE
GROUP BY s.store_id, s.store_name, s.automation_mode, s.last_optimization_run;

-- 10. Create indexes for performance
CREATE INDEX idx_products_store_tracked ON products(store_id, is_tracked);
CREATE INDEX idx_competitors_recent ON competitors(store_id, last_checked DESC);
CREATE INDEX idx_decisions_recent ON pricing_decisions(store_id, decided_at DESC);
CREATE INDEX idx_runs_recent ON optimization_runs(store_id, started_at DESC);

-- Comments for documentation
COMMENT ON TABLE stores IS 'Main table storing Salla store credentials and settings';
COMMENT ON TABLE products IS 'Store-specific product catalog with pricing data';
COMMENT ON TABLE competitors IS 'Competitor pricing data discovered through market research';
COMMENT ON TABLE pricing_decisions IS 'Audit trail of all pricing decisions and actions';
COMMENT ON TABLE optimization_runs IS 'History of optimization job executions';
COMMENT ON TABLE activity_logs IS 'User activity and system event logs';
