"""
Premium Dark Mode SaaS Dashboard - Maritime Logistics Aesthetic
Salla Price Optimizer - Multi-Tenant Platform
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
    page_title="Salla Price Optimizer - Premium Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Mode CSS - Maritime Logistics Aesthetic
st.markdown("""
<style>
    /* Global Dark Theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Premium Header */
    .premium-header {
        background: linear-gradient(135deg, #0E1117 0%, #1A1D24 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #00FF00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .premium-header h1 {
        color: #00FF00;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }

    
    .premium-header p {
        color: #FAFAFA;
        font-size: 1rem;
        margin-top: 0.5rem;
        opacity: 0.8;
    }
    
    /* Product Cards - Premium Style */
    .product-card {
        background: linear-gradient(135deg, #1A1D24 0%, #0E1117 100%);
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        border-color: #00FF00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        transform: translateY(-2px);
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #00FF00 0%, transparent 100%);
    }

    
    /* Risk Badges */
    .risk-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .risk-low {
        background: rgba(0, 255, 0, 0.1);
        color: #00FF00;
        border: 1px solid #00FF00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
    }
    
    .risk-medium {
        background: rgba(255, 193, 7, 0.1);
        color: #FFC107;
        border: 1px solid #FFC107;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.2);
    }
    
    .risk-high {
        background: rgba(255, 75, 75, 0.1);
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2);
    }

    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1A1D24 0%, #0E1117 100%);
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #FAFAFA;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }

    
    /* Price Display */
    .price-current {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FAFAFA;
    }
    
    .price-suggested {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    .price-change-positive {
        color: #00FF00;
        font-weight: 600;
    }
    
    .price-change-negative {
        color: #FF4B4B;
        font-weight: 600;
    }
    
    /* Action Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }

    
    /* Sidebar Drawer */
    .css-1d391kg {
        background-color: #0E1117;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #1A1D24 100%);
        border-right: 1px solid #00FF00;
    }
    
    /* Competitor Card in Drawer */
    .competitor-card {
        background: #1A1D24;
        border: 1px solid #2D3139;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .competitor-card:hover {
        border-color: #00FF00;
    }
    
    /* AI Recommendation Box */
    .ai-recommendation {
        background: linear-gradient(135deg, #1A1D24 0%, #0E1117 100%);
        border: 2px solid #00FF00;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
    }

    
    .ai-recommendation h3 {
        color: #00FF00;
        margin-top: 0;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    /* Donut Chart Container */
    .chart-container {
        background: #1A1D24;
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Status Indicators */
    .status-active {
        color: #00FF00;
        font-weight: 600;
    }
    
    .status-inactive {
        color: #FF4B4B;
        font-weight: 600;
    }
    
    /* Product Image Placeholder */
    .product-image {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #00FF00 0%, #00CC00 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
    }

    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0E1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00FF00;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00CC00;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1A1D24;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #FAFAFA;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00FF00 !important;
        color: #0E1117 !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'selected_store_id' not in st.session_state:
    st.session_state.selected_store_id = None

if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False


# Database helper functions
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



def get_product_competitors(store_id, product_id):
    """Get competitors for a specific product"""
    with get_db() as db:
        return db.query(Competitor).filter(
            Competitor.store_id == store_id,
            Competitor.product_id == product_id
        ).order_by(Competitor.competitor_price.asc()).all()


def get_recent_decisions(store_id, limit=100):
    """Get recent pricing decisions"""
    with get_db() as db:
        return db.query(PricingDecision).filter(
            PricingDecision.store_id == store_id
        ).order_by(desc(PricingDecision.decided_at)).limit(limit).all()


def get_recent_runs(store_id, limit=10):
    """Get recent optimization runs"""
    with get_db() as db:
        return db.query(OptimizationRun).filter(
            OptimizationRun.store_id == store_id
        ).order_by(desc(OptimizationRun.started_at)).limit(limit).all()


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
    with get_db() as db:
        # Update pricing decision
        decision = db.query(PricingDecision).filter(
            PricingDecision.store_id == store_id,
            PricingDecision.product_id == product_id
        ).order_by(desc(PricingDecision.decided_at)).first()
        
        if decision:
            decision.action_taken = 'approved'
            decision.final_price = new_price
            decision.executed_at = datetime.utcnow()
        
        # Log activity
        activity = ActivityLog(
            store_id=store_id,
            activity_type='manual_price_approval',
            description=f'Manual price approval for product {product_id}',
            activity_metadata={'product_id': product_id, 'new_price': float(new_price)}
        )
        db.add(activity)
        db.commit()
    return True


def reject_price_update(store_id, product_id):
    """Reject price update"""
    with get_db() as db:
        decision = db.query(PricingDecision).filter(
            PricingDecision.store_id == store_id,
            PricingDecision.product_id == product_id
        ).order_by(desc(PricingDecision.decided_at)).first()
        
        if decision:
            decision.action_taken = 'rejected'
            decision.executed_at = datetime.utcnow()
        
        activity = ActivityLog(
            store_id=store_id,
            activity_type='manual_price_rejection',
            description=f'Manual price rejection for product {product_id}',
            activity_metadata={'product_id': product_id}
        )
        db.add(activity)
        db.commit()
    return True



# ============================================
# SIDEBAR - Store Selection & Settings
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="color: #00FF00; font-size: 2rem; margin: 0; text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);">
            🛍️ SALLA OPTIMIZER
        </h1>
        <p style="color: #FAFAFA; opacity: 0.7; font-size: 0.85rem; margin-top: 0.5rem;">
            PREMIUM MULTI-TENANT PLATFORM
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Store Selection
    st.markdown("### 📊 SELECT STORE")
    
    stores = get_all_stores()
    
    if not stores:
        st.error("⚠️ NO STORES FOUND")
        st.info("Visit: http://localhost:8000/oauth/authorize")
        st.stop()
    
    # Create store options
    store_options = {
        f"{store.store_name}": store.store_id 
        for store in stores
    }
    
    selected_store_name = st.selectbox(
        "Choose Store",
        options=list(store_options.keys()),
        key="store_selector",
        label_visibility="collapsed"
    )
    
    selected_store_id = store_options[selected_store_name]
    st.session_state.selected_store_id = selected_store_id
    
    # Get selected store details
    current_store = get_store_by_id(selected_store_id)

    
    if current_store:
        # Store status
        status_icon = "🟢" if current_store.is_active else "🔴"
        status_class = "status-active" if current_store.is_active else "status-inactive"
        
        st.markdown(f"""
        <div style="background: #1A1D24; padding: 1rem; border-radius: 8px; border: 1px solid #2D3139; margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: #FAFAFA; opacity: 0.7;">STATUS</span>
                <span class="{status_class}">{status_icon} {'ACTIVE' if current_store.is_active else 'INACTIVE'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: #FAFAFA; opacity: 0.7;">PLAN</span>
                <span style="color: #00FF00;">{current_store.subscription_plan.upper()}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #FAFAFA; opacity: 0.7;">MODE</span>
                <span style="color: #FAFAFA;">{current_store.automation_mode.replace('_', ' ').upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Store Settings
        st.markdown("### ⚙️ SETTINGS")
        
        with st.expander("📋 CONFIGURATION", expanded=False):
            min_margin = st.number_input(
                "Min Profit Margin (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_store.min_profit_margin),
                step=0.5
            )
            
            automation_mode = st.selectbox(
                "Automation Mode",
                options=['manual', 'semi-auto', 'full-auto'],
                index=['manual', 'semi-auto', 'full-auto'].index(current_store.automation_mode)
            )
            
            update_frequency = st.slider(
                "Update Frequency (hours)",
                min_value=1,
                max_value=24,
                value=current_store.update_frequency_hours
            )
            
            if st.button("💾 SAVE SETTINGS", type="primary", use_container_width=True):
                if update_store_settings(selected_store_id, min_margin, automation_mode, update_frequency):
                    st.success("✅ SETTINGS SAVED")
                    st.rerun()
                else:
                    st.error("❌ FAILED TO SAVE")

        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### 🚀 QUICK ACTIONS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 RUN NOW", use_container_width=True):
                task_id = trigger_manual_optimization(selected_store_id)
                st.success(f"✅ STARTED\n{task_id[:8]}...")
        
        with col2:
            if st.button("📊 REFRESH", use_container_width=True):
                st.rerun()
        
        st.session_state.auto_refresh = st.checkbox(
            "🔄 Auto-refresh (30s)",
            value=st.session_state.auto_refresh
        )


# ============================================
# MAIN CONTENT
# ============================================

# Premium Header
st.markdown(f"""
<div class="premium-header">
    <h1>🛍️ {current_store.store_name}</h1>
    <p>REAL-TIME PRICE OPTIMIZATION COMMAND CENTER</p>
</div>
""", unsafe_allow_html=True)

# Get data
products = get_store_products(selected_store_id)
recent_decisions = get_recent_decisions(selected_store_id, limit=100)
recent_runs = get_recent_runs(selected_store_id, limit=1)

# Create decision lookup
product_decisions = {}
for decision in recent_decisions:
    if decision.product_id not in product_decisions:
        product_decisions[decision.product_id] = decision


# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(products)}</div>
        <div class="metric-label">Products Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    competitors_count = sum(len(get_product_competitors(selected_store_id, p.product_id)) for p in products)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{competitors_count}</div>
        <div class="metric-label">Competitors Found</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    approved_count = len([d for d in recent_decisions if d.action_taken in ['updated', 'approved']])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{approved_count}</div>
        <div class="metric-label">Prices Updated</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if recent_runs and recent_runs[0].completed_at:
        last_run = recent_runs[0]
        hours_ago = int((datetime.utcnow() - last_run.completed_at).total_seconds() / 3600)
        time_display = f"{hours_ago}h"
    else:
        time_display = "Never"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{time_display}</div>
        <div class="metric-label">Last Run</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# Tabs
tab1, tab2, tab3 = st.tabs(["📦 PRODUCTS", "📊 ANALYTICS", "📜 ACTIVITY"])

# ============================================
# TAB 1: PRODUCTS WITH PREMIUM CARDS
# ============================================

with tab1:
    st.markdown("### 📦 PRODUCT CATALOG")
    
    if not products:
        st.info("No products found. Run optimization to discover products.")
    else:
        for product in products:
            # Get decision for this product
            decision = product_decisions.get(product.product_id)
            
            # Determine risk level and badge
            if decision:
                risk_level = decision.risk_level or "Unknown"
                risk_class = f"risk-{risk_level.lower()}"
                suggested_price = decision.suggested_price
                price_change = suggested_price - product.current_price
                action_status = decision.action_taken
            else:
                risk_level = "Pending"
                risk_class = "risk-medium"
                suggested_price = product.current_price
                price_change = 0
                action_status = "pending"
            
            # Price change indicator
            if price_change > 0:
                change_class = "price-change-positive"
                change_icon = "↑"
            elif price_change < 0:
                change_class = "price-change-negative"
                change_icon = "↓"
            else:
                change_class = ""
                change_icon = "="

            
            # Product Card
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
            
            with col1:
                st.markdown(f"""
                <div class="product-image">
                    🛍️
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <div style="color: #FAFAFA; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.3rem;">
                        {product.name}
                    </div>
                    <div style="color: #FAFAFA; opacity: 0.6; font-size: 0.85rem;">
                        ID: {product.product_id} | SKU: {product.sku or 'N/A'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <div style="color: #FAFAFA; opacity: 0.7; font-size: 0.85rem;">CURRENT PRICE</div>
                    <div class="price-current">{product.current_price:.2f} SAR</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <div style="color: #FAFAFA; opacity: 0.7; font-size: 0.85rem;">AI SUGGESTS</div>
                    <div class="price-suggested">{suggested_price:.2f} SAR</div>
                    <div class="{change_class}" style="font-size: 0.9rem;">
                        {change_icon} {abs(price_change):.2f} SAR
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <div class="risk-badge {risk_class}">
                        {risk_level}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📋 DETAILS", key=f"details_{product.product_id}", use_container_width=True):
                    st.session_state.selected_product_id = product.product_id
                    st.rerun()
            
            st.markdown("<hr style='border: 1px solid #2D3139; margin: 1rem 0;'>", unsafe_allow_html=True)


# ============================================
# PRODUCT DETAIL DRAWER (SIDEBAR)
# ============================================

if st.session_state.selected_product_id:
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📋 PRODUCT DETAILS")
        
        # Get product details
        selected_product = next((p for p in products if p.product_id == st.session_state.selected_product_id), None)
        
        if selected_product:
            decision = product_decisions.get(selected_product.product_id)
            competitors = get_product_competitors(selected_store_id, selected_product.product_id)
            
            # Product Info
            st.markdown(f"""
            <div style="background: #1A1D24; padding: 1rem; border-radius: 8px; border: 1px solid #2D3139; margin-bottom: 1rem;">
                <div style="color: #00FF00; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                    {selected_product.name}
                </div>
                <div style="color: #FAFAFA; opacity: 0.7; font-size: 0.85rem;">
                    ID: {selected_product.product_id}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Current vs Suggested
            if decision:
                st.markdown(f"""
                <div style="background: #1A1D24; padding: 1rem; border-radius: 8px; border: 1px solid #2D3139; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #FAFAFA; opacity: 0.7;">Current Price</span>
                        <span style="color: #FAFAFA; font-weight: 600;">{selected_product.current_price:.2f} SAR</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #FAFAFA; opacity: 0.7;">Suggested Price</span>
                        <span style="color: #00FF00; font-weight: 600;">{decision.suggested_price:.2f} SAR</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            
            # Competitors
            if competitors:
                st.markdown("#### 🏪 COMPETITORS")
                for comp in competitors[:5]:
                    st.markdown(f"""
                    <div class="competitor-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="color: #FAFAFA; font-weight: 600; margin-bottom: 0.3rem;">
                                    {comp.competitor_name}
                                </div>
                                <div style="color: #FAFAFA; opacity: 0.6; font-size: 0.85rem;">
                                    Confidence: {comp.confidence_score:.0%}
                                </div>
                            </div>
                            <div style="color: #00FF00; font-size: 1.3rem; font-weight: 700;">
                                {comp.competitor_price:.2f} SAR
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # AI Recommendation
            if decision:
                st.markdown(f"""
                <div class="ai-recommendation">
                    <h3>🤖 AI RECOMMENDATION</h3>
                    <div style="color: #FAFAFA; margin-bottom: 1rem;">
                        {decision.reasoning or 'AI analysis in progress...'}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #FAFAFA; opacity: 0.7;">Strategy</span>
                        <span style="color: #00FF00; font-weight: 600;">{decision.strategy_used or 'N/A'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #FAFAFA; opacity: 0.7;">Profit Margin</span>
                        <span style="color: #00FF00; font-weight: 600;">{decision.profit_margin_percentage:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                
                # Action Buttons
                if decision.action_taken in ['pending', 'skipped']:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ APPROVE", key="approve_btn", type="primary", use_container_width=True):
                            if approve_price_update(selected_store_id, selected_product.product_id, decision.suggested_price):
                                st.success("✅ APPROVED!")
                                st.session_state.selected_product_id = None
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ REJECT", key="reject_btn", use_container_width=True):
                            if reject_price_update(selected_store_id, selected_product.product_id):
                                st.warning("❌ REJECTED")
                                st.session_state.selected_product_id = None
                                st.rerun()
                else:
                    status_text = decision.action_taken.upper()
                    status_color = "#00FF00" if decision.action_taken in ['updated', 'approved'] else "#FF4B4B"
                    st.markdown(f"""
                    <div style="background: {status_color}20; border: 1px solid {status_color}; border-radius: 8px; padding: 1rem; text-align: center;">
                        <div style="color: {status_color}; font-weight: 600; font-size: 1.1rem;">
                            {status_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Close button
            if st.button("✖️ CLOSE", key="close_drawer", use_container_width=True):
                st.session_state.selected_product_id = None
                st.rerun()


# ============================================
# TAB 2: ANALYTICS WITH DONUT CHARTS
# ============================================

with tab2:
    st.markdown("### 📊 PERFORMANCE ANALYTICS")
    
    # Calculate competitive pricing percentage
    total_products = len(products)
    competitive_products = len([d for d in recent_decisions if d.action_taken in ['updated', 'approved']])
    competitive_percentage = (competitive_products / total_products * 100) if total_products > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Competitive Pricing Donut Chart
        fig1 = go.Figure(data=[go.Pie(
            labels=['Competitive', 'Not Optimized'],
            values=[competitive_products, total_products - competitive_products],
            hole=0.6,
            marker=dict(colors=['#00FF00', '#2D3139']),
            textfont=dict(color='#FAFAFA', size=14),
            hovertemplate='<b>%{label}</b><br>%{value} products<br>%{percent}<extra></extra>'
        )])
        
        fig1.update_layout(
            title=dict(
                text='Competitive Pricing',
                font=dict(color='#FAFAFA', size=18),
                x=0.5,
                xanchor='center'
            ),
            annotations=[dict(
                text=f'{competitive_percentage:.0f}%',
                x=0.5, y=0.5,
                font=dict(size=32, color='#00FF00'),
                showarrow=False
            )],
            paper_bgcolor='#1A1D24',
            plot_bgcolor='#1A1D24',
            showlegend=True,
            legend=dict(font=dict(color='#FAFAFA')),
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)

    
    with col2:
        # Risk Distribution Donut Chart
        low_risk = len([d for d in recent_decisions if d.risk_level == 'Low'])
        medium_risk = len([d for d in recent_decisions if d.risk_level == 'Medium'])
        high_risk = len([d for d in recent_decisions if d.risk_level == 'High'])
        
        fig2 = go.Figure(data=[go.Pie(
            labels=['Low Risk', 'Medium Risk', 'High Risk'],
            values=[low_risk, medium_risk, high_risk],
            hole=0.6,
            marker=dict(colors=['#00FF00', '#FFC107', '#FF4B4B']),
            textfont=dict(color='#FAFAFA', size=14),
            hovertemplate='<b>%{label}</b><br>%{value} decisions<br>%{percent}<extra></extra>'
        )])
        
        fig2.update_layout(
            title=dict(
                text='Risk Distribution',
                font=dict(color='#FAFAFA', size=18),
                x=0.5,
                xanchor='center'
            ),
            annotations=[dict(
                text=f'{len(recent_decisions)}',
                x=0.5, y=0.5,
                font=dict(size=32, color='#00FF00'),
                showarrow=False
            )],
            paper_bgcolor='#1A1D24',
            plot_bgcolor='#1A1D24',
            showlegend=True,
            legend=dict(font=dict(color='#FAFAFA')),
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)

    
    # Recent Optimization Runs
    st.markdown("### 📋 RECENT OPTIMIZATION RUNS")
    
    all_runs = get_recent_runs(selected_store_id, limit=10)
    
    if all_runs:
        runs_data = []
        for run in all_runs:
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
        
        df = pd.DataFrame(runs_data)
        
        # Style the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.info("No optimization runs yet. Click 'RUN NOW' to start!")


# ============================================
# TAB 3: ACTIVITY LOGS
# ============================================

with tab3:
    st.markdown("### 📜 ACTIVITY LOGS")
    
    from database.models import ActivityLog
    
    with get_db() as db:
        activity_logs = db.query(ActivityLog).filter(
            ActivityLog.store_id == selected_store_id
        ).order_by(desc(ActivityLog.created_at)).limit(50).all()
    
    if activity_logs:
        for log in activity_logs:
            # Color code by activity type
            if 'error' in log.activity_type.lower() or 'failed' in log.activity_type.lower():
                icon = "🔴"
                border_color = "#FF4B4B"
            elif 'success' in log.activity_type.lower() or 'completed' in log.activity_type.lower() or 'approval' in log.activity_type.lower():
                icon = "🟢"
                border_color = "#00FF00"
            elif 'warning' in log.activity_type.lower():
                icon = "🟡"
                border_color = "#FFC107"
            else:
                icon = "🔵"
                border_color = "#2D3139"
            
            st.markdown(f"""
            <div style="background: #1A1D24; border-left: 4px solid {border_color}; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="color: #FAFAFA; font-weight: 600;">
                        {icon} {log.activity_type.replace('_', ' ').title()}
                    </div>
                    <div style="color: #FAFAFA; opacity: 0.6; font-size: 0.85rem;">
                        {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                <div style="color: #FAFAFA; opacity: 0.8;">
                    {log.description}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity logs yet.")


# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #FAFAFA; opacity: 0.5; padding: 1rem;">
    🛍️ <strong style="color: #00FF00;">SALLA PRICE OPTIMIZER</strong> | Premium Multi-Tenant Platform<br>
    <small>AI-Powered Dynamic Pricing | Real-Time Market Intelligence</small>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if st.session_state.auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
