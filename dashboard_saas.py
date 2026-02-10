"""
Professional Multi-Tenant SaaS Dashboard
Salla Price Optimizer - Production Grade UI
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from sqlalchemy import desc
import plotly.express as px
import plotly.graph_objects as go

# Database imports
from database.db import get_db
from database.models import Store, Product, Competitor, PricingDecision, OptimizationRun, ActivityLog

# Celery imports for live logs
from scheduler.celery_app import celery_app

# Page configuration
st.set_page_config(
    page_title="Salla Price Optimizer - SaaS Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        color: #333;
        font-size: 2rem;
        margin: 0;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-active {
        background: #d4edda;
        color: #155724;
    }
    
    .status-inactive {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-running {
        background: #cce5ff;
        color: #004085;
    }
    
    /* Product table */
    .product-image {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Log viewer */
    .log-viewer {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .log-entry {
        margin-bottom: 0.5rem;
        padding: 0.25rem;
    }
    
    .log-info { color: #4ec9b0; }
    .log-warning { color: #dcdcaa; }
    .log-error { color: #f48771; }
    .log-success { color: #b5cea8; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_store_id' not in st.session_state:
    st.session_state.selected_store_id = None

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False


def get_all_stores():
    """Get all stores from database"""
    with get_db() as db:
        stores = db.query(Store).all()
        return stores


def get_store_by_id(store_id):
    """Get specific store"""
    with get_db() as db:
        return db.query(Store).filter(Store.store_id == store_id).first()


def get_store_products(store_id):
    """Get products for a store"""
    with get_db() as db:
        return db.query(Product).filter(
            Product.store_id == store_id,
            Product.is_tracked == True
        ).all()


def get_store_competitors(store_id):
    """Get competitors for a store"""
    with get_db() as db:
        return db.query(Competitor).filter(
            Competitor.store_id == store_id
        ).all()


def get_recent_decisions(store_id, limit=10):
    """Get recent pricing decisions"""
    with get_db() as db:
        return db.query(PricingDecision).filter(
            PricingDecision.store_id == store_id
        ).order_by(desc(PricingDecision.decided_at)).limit(limit).all()


def get_recent_runs(store_id, limit=5):
    """Get recent optimization runs"""
    with get_db() as db:
        return db.query(OptimizationRun).filter(
            OptimizationRun.store_id == store_id
        ).order_by(desc(OptimizationRun.started_at)).limit(limit).all()


def get_recent_activity(store_id, limit=20):
    """Get recent activity logs"""
    with get_db() as db:
        return db.query(ActivityLog).filter(
            ActivityLog.store_id == store_id
        ).order_by(desc(ActivityLog.created_at)).limit(limit).all()


def update_store_settings(store_id, min_margin, automation_mode, update_frequency):
    """Update store settings"""
    with get_db() as db:
        store = db.query(Store).filter(Store.store_id == store_id).first()
        if store:
            store.min_profit_margin = min_margin
            store.automation_mode = automation_mode
            store.update_frequency_hours = update_frequency
            db.commit()
            return True
    return False


def trigger_manual_optimization(store_id):
    """Trigger manual optimization for a store"""
    from scheduler.tasks import manual_optimize
    task = manual_optimize.delay(store_id)
    return task.id


def approve_price_update(store_id, product_id, new_price):
    """Approve and execute price update"""
    # This would call the Salla API to update the price
    # For now, we'll just log it
    with get_db() as db:
        activity = ActivityLog(
            store_id=store_id,
            activity_type='manual_price_update',
            description=f'Manual price update approved for product {product_id}',
            metadata={'product_id': product_id, 'new_price': float(new_price)}
        )
        db.add(activity)
        db.commit()
    return True


# ============================================
# SIDEBAR - Store Selection & Settings
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="color: white;">🛍️ Salla Optimizer</h1>
        <p style="color: rgba(255,255,255,0.8);">Multi-Tenant SaaS Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Store Selection
    st.subheader("📊 Select Store")
    
    stores = get_all_stores()
    
    if not stores:
        st.warning("⚠️ No stores found. Please onboard a store first.")
        st.info("Visit: http://localhost:8000/oauth/authorize")
        st.stop()
    
    # Create store options
    store_options = {
        f"{store.store_name} ({store.store_id})": store.store_id 
        for store in stores
    }
    
    selected_store_name = st.selectbox(
        "Choose Store",
        options=list(store_options.keys()),
        key="store_selector"
    )
    
    selected_store_id = store_options[selected_store_name]
    st.session_state.selected_store_id = selected_store_id
    
    # Get selected store details
    current_store = get_store_by_id(selected_store_id)
    
    if current_store:
        # Store status
        status_color = "🟢" if current_store.is_active else "🔴"
        st.markdown(f"""
        **Status:** {status_color} {'Active' if current_store.is_active else 'Inactive'}  
        **Plan:** {current_store.subscription_plan.title()}  
        **Mode:** {current_store.automation_mode.replace('_', ' ').title()}
        """)
        
        st.markdown("---")
        
        # Store Settings
        st.subheader("⚙️ Store Settings")
        
        with st.expander("📋 Configuration", expanded=False):
            # Minimum Profit Margin
            min_margin = st.number_input(
                "Minimum Profit Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_store.min_profit_margin),
                step=0.5,
                help="Minimum profit margin to maintain"
            )
            
            # Automation Mode
            automation_mode = st.selectbox(
                "Automation Mode",
                options=['manual', 'semi-auto', 'full-auto'],
                index=['manual', 'semi-auto', 'full-auto'].index(current_store.automation_mode),
                help="Manual: You approve all changes\nSemi-Auto: Low risk auto-approved\nFull-Auto: All changes auto-approved"
            )
            
            # Update Frequency
            update_frequency = st.slider(
                "Update Frequency (hours)",
                min_value=1,
                max_value=24,
                value=current_store.update_frequency_hours,
                help="How often to run optimization"
            )
            
            # Risk Tolerance
            risk_tolerance = st.selectbox(
                "Risk Tolerance",
                options=['low', 'medium', 'high'],
                index=['low', 'medium', 'high'].index(current_store.risk_tolerance),
                help="How aggressive to be with pricing"
            )
            
            # Save button
            if st.button("💾 Save Settings", type="primary"):
                if update_store_settings(selected_store_id, min_margin, automation_mode, update_frequency):
                    st.success("✅ Settings saved!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save settings")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Run Now", use_container_width=True):
                task_id = trigger_manual_optimization(selected_store_id)
                st.success(f"✅ Optimization started!\nTask ID: {task_id[:8]}...")
        
        with col2:
            if st.button("📊 Refresh", use_container_width=True):
                st.rerun()
        
        # Auto-refresh toggle
        st.session_state.auto_refresh = st.checkbox(
            "🔄 Auto-refresh (30s)",
            value=st.session_state.auto_refresh
        )
        
        st.markdown("---")
        
        # Store Info
        with st.expander("ℹ️ Store Information"):
            st.markdown(f"""
            **Store ID:** {current_store.store_id}  
            **Domain:** {current_store.store_domain or 'N/A'}  
            **Owner:** {current_store.owner_name}  
            **Email:** {current_store.owner_email}  
            **Created:** {current_store.created_at.strftime('%Y-%m-%d')}  
            **Last Run:** {current_store.last_optimization_run.strftime('%Y-%m-%d %H:%M') if current_store.last_optimization_run else 'Never'}
            """)

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🛍️ {current_store.store_name}</h1>
    <p>Real-time Price Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

products = get_store_products(selected_store_id)
competitors = get_store_competitors(selected_store_id)
recent_decisions = get_recent_decisions(selected_store_id, limit=100)
recent_runs = get_recent_runs(selected_store_id, limit=1)

with col1:
    st.metric(
        label="📦 Products Tracked",
        value=len(products),
        delta=None
    )

with col2:
    st.metric(
        label="🏪 Competitors Found",
        value=len(competitors),
        delta=None
    )

with col3:
    approved_count = len([d for d in recent_decisions if d.action_taken == 'updated'])
    st.metric(
        label="✅ Prices Updated",
        value=approved_count,
        delta=None
    )

with col4:
    if recent_runs and recent_runs[0].completed_at:
        last_run = recent_runs[0]
        hours_ago = int((datetime.utcnow() - last_run.completed_at).total_seconds() / 3600)
        st.metric(
            label="⏱️ Last Run",
            value=f"{hours_ago}h ago",
            delta=None
        )
    else:
        st.metric(
            label="⏱️ Last Run",
            value="Never",
            delta=None
        )

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Products", 
    "📊 Analytics", 
    "🔍 Decisions", 
    "📜 Activity Logs",
    "🔴 Live Tasks"
])

# ============================================
# TAB 1: PRODUCTS
# ============================================

with tab1:
    st.subheader("📦 Product Catalog with AI Suggestions")
    
    if not products:
        st.info("No products found. Run optimization to discover products.")
    else:
        # Get latest decisions for each product
        product_decisions = {}
        for decision in recent_decisions:
            if decision.product_id not in product_decisions:
                product_decisions[decision.product_id] = decision
        
        # Create product table
        for product in products:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                
                with col1:
                    # Product image placeholder
                    st.markdown(f"""
                    <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">
                        🛍️
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{product.name}**")
                    st.caption(f"ID: {product.product_id} | SKU: {product.sku or 'N/A'}")
                
                with col3:
                    st.markdown(f"**Cost:** {product.cost_price or 0:.2f} SAR")
                    st.markdown(f"**Current:** {product.current_price:.2f} SAR")
                
                with col4:
                    # AI Suggestion
                    if product.product_id in product_decisions:
                        decision = product_decisions[product.product_id]
                        suggested = decision.suggested_price
                        delta = suggested - product.current_price
                        
                        if decision.risk_level == 'Low':
                            risk_color = "🟢"
                        elif decision.risk_level == 'Medium':
                            risk_color = "🟡"
                        else:
                            risk_color = "🔴"
                        
                        st.markdown(f"**AI Suggests:** {suggested:.2f} SAR")
                        st.caption(f"{risk_color} {decision.risk_level} Risk | {delta:+.2f} SAR")
                    else:
                        st.markdown("**AI Suggests:** Pending...")
                        st.caption("⏳ Awaiting analysis")
                
                with col5:
                    if product.product_id in product_decisions:
                        decision = product_decisions[product.product_id]
                        
                        if decision.action_taken == 'updated':
                            st.success("✅ Updated")
                        elif decision.action_taken == 'skipped':
                            st.warning("⏭️ Skipped")
                        elif decision.risk_level != 'High':
                            if st.button("✅ Approve", key=f"approve_{product.product_id}"):
                                if approve_price_update(selected_store_id, product.product_id, decision.suggested_price):
                                    st.success("Price update approved!")
                                    st.rerun()
                        else:
                            st.error("⛔ High Risk")
                    else:
                        st.info("⏳ Pending")
                
                st.markdown("---")

# ============================================
# TAB 2: ANALYTICS
# ============================================

with tab2:
    st.subheader("📊 Performance Analytics")
    
    # Get optimization runs for charts
    all_runs = get_recent_runs(selected_store_id, limit=30)
    
    if all_runs:
        # Prepare data
        run_dates = [run.started_at.strftime('%Y-%m-%d %H:%M') for run in reversed(all_runs)]
        products_analyzed = [run.products_analyzed for run in reversed(all_runs)]
        products_updated = [run.products_updated for run in reversed(all_runs)]
        competitors_found = [run.competitors_found for run in reversed(all_runs)]
        
        # Chart 1: Products Analyzed vs Updated
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=run_dates, y=products_analyzed,
                name='Analyzed', mode='lines+markers',
                line=dict(color='#667eea', width=2)
            ))
            fig1.add_trace(go.Scatter(
                x=run_dates, y=products_updated,
                name='Updated', mode='lines+markers',
                line=dict(color='#28a745', width=2)
            ))
            fig1.update_layout(
                title="Products Analyzed vs Updated",
                xaxis_title="Date",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=run_dates, y=competitors_found,
                marker_color='#764ba2'
            ))
            fig2.update_layout(
                title="Competitors Found Per Run",
                xaxis_title="Date",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recent runs table
        st.subheader("📋 Recent Optimization Runs")
        
        runs_data = []
        for run in all_runs[:10]:
            duration = run.duration_seconds if run.duration_seconds else 0
            runs_data.append({
                'Date': run.started_at.strftime('%Y-%m-%d %H:%M'),
                'Type': run.run_type.title(),
                'Status': run.status.title(),
                'Products': run.products_analyzed,
                'Updated': run.products_updated,
                'Skipped': run.products_skipped,
                'Competitors': run.competitors_found,
                'Duration': f"{duration}s"
            })
        
        if runs_data:
            df = pd.DataFrame(runs_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No optimization runs yet. Click 'Run Now' to start!")

# ============================================
# TAB 3: PRICING DECISIONS
# ============================================

with tab3:
    st.subheader("🔍 Pricing Decisions History")
    
    if recent_decisions:
        decisions_data = []
        for decision in recent_decisions[:20]:
            decisions_data.append({
                'Date': decision.decided_at.strftime('%Y-%m-%d %H:%M'),
                'Product ID': decision.product_id,
                'Old Price': f"{decision.old_price:.2f} SAR",
                'Suggested': f"{decision.suggested_price:.2f} SAR",
                'Change': f"{(decision.suggested_price - decision.old_price):+.2f} SAR",
                'Strategy': decision.strategy_used or 'N/A',
                'Risk': decision.risk_level or 'N/A',
                'Action': decision.action_taken.title(),
                'Margin': f"{decision.profit_margin_percentage:.1f}%" if decision.profit_margin_percentage else 'N/A'
            })
        
        df = pd.DataFrame(decisions_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Decision breakdown
        col1, col2, col3 = st.columns(3)
        
        with col1:
            updated = len([d for d in recent_decisions if d.action_taken == 'updated'])
            st.metric("✅ Updated", updated)
        
        with col2:
            skipped = len([d for d in recent_decisions if d.action_taken == 'skipped'])
            st.metric("⏭️ Skipped", skipped)
        
        with col3:
            pending = len([d for d in recent_decisions if d.action_taken == 'pending'])
            st.metric("⏳ Pending", pending)
    else:
        st.info("No pricing decisions yet.")

# ============================================
# TAB 4: ACTIVITY LOGS
# ============================================

with tab4:
    st.subheader("📜 Activity Logs")
    
    activity_logs = get_recent_activity(selected_store_id, limit=50)
    
    if activity_logs:
        for log in activity_logs:
            # Color code by activity type
            if 'error' in log.activity_type.lower() or 'failed' in log.activity_type.lower():
                icon = "🔴"
                color = "#f8d7da"
            elif 'success' in log.activity_type.lower() or 'completed' in log.activity_type.lower():
                icon = "🟢"
                color = "#d4edda"
            elif 'warning' in log.activity_type.lower():
                icon = "🟡"
                color = "#fff3cd"
            else:
                icon = "🔵"
                color = "#d1ecf1"
            
            with st.container():
                st.markdown(f"""
                <div style="background: {color}; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <strong>{icon} {log.activity_type.replace('_', ' ').title()}</strong><br>
                    <small>{log.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                    {log.description}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No activity logs yet.")

# ============================================
# TAB 5: LIVE CELERY TASKS
# ============================================

with tab5:
    st.subheader("🔴 Live Background Tasks")
    
    st.markdown("""
    <div class="log-viewer">
        <div class="log-entry log-info">📡 Connecting to Celery...</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Get active tasks
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        
        if active_tasks:
            st.markdown("### 🔄 Active Tasks")
            for worker, tasks in active_tasks.items():
                st.markdown(f"**Worker:** `{worker}`")
                for task in tasks:
                    with st.expander(f"📋 {task['name']}", expanded=True):
                        st.json({
                            'Task ID': task['id'],
                            'Name': task['name'],
                            'Args': task['args'],
                            'Started': task.get('time_start', 'N/A')
                        })
        else:
            st.info("No active tasks at the moment.")
        
        if scheduled_tasks:
            st.markdown("### ⏰ Scheduled Tasks")
            for worker, tasks in scheduled_tasks.items():
                st.markdown(f"**Worker:** `{worker}`")
                for task in tasks:
                    st.markdown(f"- {task['request']['name']} (ETA: {task['eta']})")
        
        # Recent completed tasks from database
        st.markdown("### ✅ Recent Completed Tasks")
        recent_runs_all = get_recent_runs(selected_store_id, limit=10)
        
        for run in recent_runs_all:
            status_icon = "✅" if run.status == 'completed' else "❌" if run.status == 'failed' else "⏳"
            
            with st.expander(f"{status_icon} {run.run_type.title()} - {run.started_at.strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Products Analyzed", run.products_analyzed)
                    st.metric("Products Updated", run.products_updated)
                
                with col2:
                    st.metric("Products Skipped", run.products_skipped)
                    st.metric("Competitors Found", run.competitors_found)
                
                with col3:
                    st.metric("Duration", f"{run.duration_seconds or 0}s")
                    st.metric("Status", run.status.title())
                
                if run.error_message:
                    st.error(f"Error: {run.error_message}")
        
    except Exception as e:
        st.error(f"❌ Could not connect to Celery: {str(e)}")
        st.info("Make sure Celery worker is running: `celery -A scheduler.celery_app worker`")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🛍️ <strong>Salla Price Optimizer</strong> | Professional SaaS Dashboard<br>
    <small>Multi-Tenant Edition | Real-time AI-Powered Pricing</small>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if st.session_state.auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
