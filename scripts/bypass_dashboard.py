import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🛍️ Salla Price Optimizer", 
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2d5aa0);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
    }
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
    .error-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🛍️ Salla Price Optimizer Dashboard</h1>
    <p>Fashion Store Edition | Bypass Mode - No Authentication Required</p>
</div>
""", unsafe_allow_html=True)

# Load existing data
def load_data():
    """Load data from existing files or create sample data."""
    
    # Try to load real data first
    output_dir = "ai-agent-output"
    market_file = os.path.join(output_dir, "step_1_fashion_market_intelligence.json")
    pricing_file = os.path.join(output_dir, "step_2_pricing_decision.json")
    
    market_data = None
    pricing_data = None
    
    if os.path.exists(market_file):
        try:
            with open(market_file, 'r', encoding='utf-8') as f:
                market_data = json.load(f)
        except:
            pass
    
    if os.path.exists(pricing_file):
        try:
            with open(pricing_file, 'r', encoding='utf-8') as f:
                pricing_data = json.load(f)
        except:
            pass
    
    return market_data, pricing_data

# Load data
market_data, pricing_data = load_data()

# Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Status
    if market_data:
        st.success("✅ Market Data Available")
    else:
        st.warning("⚠️ No Market Data")
    
    if pricing_data:
        st.success("✅ Pricing Data Available")
    else:
        st.warning("⚠️ No Pricing Data")
    
    st.markdown("---")
    
    # Bypass mode info
    st.info("🔄 **Bypass Mode Active**\nNo authentication required")
    
    st.markdown("---")
    
    # Actions
    if st.button("🚀 Generate Sample Data", type="primary"):
        st.success("Sample data generated!")
        st.info("Refresh page to see sample data")
    
    if st.button("🔄 Refresh Dashboard"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Instructions
    st.subheader("📋 Quick Actions")
    st.markdown("""
    **To get real data:**
    1. Run: `python main.py`
    2. Refresh this dashboard
    
    **To fix authentication:**
    1. Check Salla app settings
    2. Verify callback URL
    3. Update app permissions
    """)

# Main content
if market_data and market_data.get('products'):
    products = market_data['products']
    
    # Overview section
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Products</h3>
            <h2>{len(products)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_competitors = sum(len(p.get('competitors', [])) for p in products)
        st.markdown(f"""
        <div class="metric-card">
            <h3>Competitors</h3>
            <h2>{total_competitors}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_price = sum(p.get('price', 0) for p in products) / len(products) if products else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Price</h3>
            <h2>{avg_price:.0f} SAR</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if pricing_data:
            margin = pricing_data.get('profit_margin_percentage', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Profit Margin</h3>
                <h2>{margin:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>Profit Margin</h3>
                <h2>N/A</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Products table
    st.header("🛍️ Fashion Products")
    
    products_data = []
    for i, product in enumerate(products, 1):
        products_data.append({
            '#': i,
            'Product Name': product.get('name', 'Unknown'),
            'Product ID': product.get('product_id', 'N/A'),
            'Current Price (SAR)': f"{product.get('price', 0):.2f}",
            'Cost Price (SAR)': f"{product.get('cost_price', 0):.2f}",
            'Category': product.get('category', 'Fashion'),
            'Competitors Found': len(product.get('competitors', [])),
            'Status': product.get('status', 'Active')
        })
    
    df = pd.DataFrame(products_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Detailed analysis
    st.header("🔍 Market Intelligence Analysis")
    
    # Product selector
    product_options = []
    for i, product in enumerate(products):
        name = product.get('name', f'Product {i+1}')
        price = product.get('price', 0)
        product_options.append(f"{name} - {price} SAR")
    
    selected_idx = st.selectbox("Select Product for Analysis:", range(len(products)), format_func=lambda x: product_options[x])
    
    selected_product = products[selected_idx]
    competitors = selected_product.get('competitors', [])
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📦 Product Information")
        
        product_info = f"""
        **Name:** {selected_product.get('name', 'Unknown')}  
        **ID:** {selected_product.get('product_id', 'N/A')}  
        **Current Price:** {selected_product.get('price', 0)} SAR  
        **Cost Price:** {selected_product.get('cost_price', 0)} SAR  
        **Category:** {selected_product.get('category', 'Fashion')}  
        **SKU:** {selected_product.get('sku', 'N/A')}  
        **Status:** {selected_product.get('status', 'Active')}
        """
        
        st.markdown(product_info)
        
        # Admin link if available
        admin_url = selected_product.get('admin_url')
        if admin_url:
            st.markdown(f"[🔗 View in Salla Admin]({admin_url})")
    
    with col2:
        st.subheader("🏪 Competitor Analysis")
        
        if competitors:
            # Competitor comparison chart
            comp_names = [comp.get('store_name', f'Store {i}') for i, comp in enumerate(competitors, 1)]
            comp_prices = [comp.get('price', 0) for comp in competitors]
            
            chart_data = pd.DataFrame({
                'Store': comp_names,
                'Price (SAR)': comp_prices
            })
            
            st.bar_chart(chart_data.set_index('Store'))
            
            # Competitor table
            st.subheader("Detailed Competitor Data")
            
            comp_data = []
            our_price = selected_product.get('price', 0)
            
            for comp in competitors:
                comp_price = comp.get('price', 0)
                difference = comp_price - our_price
                difference_pct = (difference / our_price * 100) if our_price > 0 else 0
                
                comp_data.append({
                    'Store Name': comp.get('store_name', 'Unknown'),
                    'Price (SAR)': f"{comp_price:.2f}",
                    'Difference': f"{difference:+.2f} SAR",
                    'Difference %': f"{difference_pct:+.1f}%",
                    'Platform': comp.get('platform', 'Salla'),
                    'Confidence': f"{comp.get('confidence_score', 0)*100:.0f}%"
                })
            
            comp_df = pd.DataFrame(comp_data)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)
        else:
            st.info("No competitor data available for this product")
    
    # Pricing decision section
    if pricing_data:
        st.header("⚖️ Pricing Strategy & Decision")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current = pricing_data.get('current_price', 0)
            suggested = pricing_data.get('suggested_price', 0)
            delta = suggested - current
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>Recommended Price</h4>
                <h2>{suggested:.2f} SAR</h2>
                <p>Change: {delta:+.2f} SAR</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            strategy = pricing_data.get('strategy_used', 'Unknown')
            st.markdown(f"""
            <div class="metric-card">
                <h4>Strategy</h4>
                <h2>{strategy}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            risk = pricing_data.get('risk_level', 'High')
            margin = pricing_data.get('profit_margin_percentage', 0)
            
            if risk == "Low":
                card_class = "success-card"
                risk_icon = "🟢"
            elif risk == "Medium":
                card_class = "warning-card"
                risk_icon = "🟡"
            else:
                card_class = "error-card"
                risk_icon = "🔴"
            
            st.markdown(f"""
            <div class="{card_class}">
                <h4>Risk Level</h4>
                <h2>{risk_icon} {risk}</h2>
                <p>Margin: {margin:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Reasoning
        st.subheader("📋 Analysis & Reasoning")
        reasoning = pricing_data.get('reasoning', 'No reasoning provided.')
        
        if risk == "Low":
            st.success(f"**Recommendation:** {reasoning}")
        elif risk == "Medium":
            st.warning(f"**Recommendation:** {reasoning}")
        else:
            st.error(f"**Recommendation:** {reasoning}")
        
        # Action buttons
        st.subheader("🎯 Available Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if risk != "High":
                if st.button("✅ Approve Price Update", type="primary"):
                    st.balloons()
                    st.success("✅ Price update approved!")
                    st.info("💡 **Note:** In bypass mode, this is a simulation. To actually update prices, fix the authentication and run the full system.")
            else:
                st.button("⛔ High Risk - Blocked", disabled=True)
        
        with col2:
            if st.button("❌ Reject Decision"):
                st.warning("❌ Decision rejected")
        
        with col3:
            if st.button("📊 Reanalyze Market"):
                st.info("💡 Run `python main.py` to perform new market analysis")

else:
    # No data available - show getting started
    st.header("🚀 Getting Started")
    
    st.markdown("""
    <div class="warning-card">
        <h3>⚠️ No Market Data Found</h3>
        <p>The system needs to analyze your products and competitors first.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Instructions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Option 1: Fix Authentication")
        st.markdown("""
        1. **Check your Salla app configuration**
        2. **Verify callback URL:** `http://localhost:8000/callback`
        3. **Update app permissions** (see screenshots)
        4. **Run:** `python fix_token.py`
        5. **Test:** `python test_current_token.py`
        6. **Run optimizer:** `python main.py`
        """)
    
    with col2:
        st.subheader("🎯 Option 2: Generate Sample Data")
        st.markdown("""
        1. **Click "Generate Sample Data" in sidebar**
        2. **Refresh this page**
        3. **Explore the dashboard features**
        4. **Later fix authentication for real data**
        """)
        
        if st.button("🎲 Generate Sample Data Now", type="primary"):
            # Create sample data
            sample_market_data = {
                "timestamp": datetime.now().isoformat(),
                "products_discovered": 3,
                "store_connected": False,
                "data_source": "sample_data",
                "products": [
                    {
                        "product_id": "SAMPLE_001",
                        "name": "فستان سهرة أنيق",
                        "price": 174.0,
                        "cost_price": 120.0,
                        "category": "Fashion",
                        "status": "sale",
                        "sku": "SAMPLE-001",
                        "description": "فستان سهرة أنيق للمناسبات الخاصة",
                        "admin_url": "#",
                        "competitors": [
                            {"store_name": "متجر الأناقة", "price": 165.0, "platform": "Salla", "confidence_score": 0.85},
                            {"store_name": "متجر الموضة", "price": 180.0, "platform": "Salla", "confidence_score": 0.78},
                            {"store_name": "متجر النجوم", "price": 159.0, "platform": "Salla", "confidence_score": 0.92}
                        ]
                    },
                    {
                        "product_id": "SAMPLE_002",
                        "name": "بنطلون جينز نسائي",
                        "price": 149.0,
                        "cost_price": 95.0,
                        "category": "Fashion",
                        "status": "sale",
                        "sku": "SAMPLE-002",
                        "description": "بنطلون جينز عصري للاستخدام اليومي",
                        "admin_url": "#",
                        "competitors": [
                            {"store_name": "متجر الجينز", "price": 145.0, "platform": "Salla", "confidence_score": 0.88},
                            {"store_name": "متجر الكاجوال", "price": 155.0, "platform": "Salla", "confidence_score": 0.75}
                        ]
                    }
                ]
            }
            
            sample_pricing_data = {
                "timestamp": datetime.now().isoformat(),
                "product_name": "فستان سهرة أنيق",
                "product_id": "SAMPLE_001",
                "current_price": 174.0,
                "cost_price": 120.0,
                "suggested_price": 157.0,
                "profit_margin_percentage": 30.8,
                "strategy_used": "Undercut",
                "reasoning": "Sample analysis shows opportunity to undercut competitors while maintaining healthy profit margin.",
                "risk_level": "Low",
                "market_position": "Competitive"
            }
            
            # Save sample data
            os.makedirs("ai-agent-output", exist_ok=True)
            
            with open("ai-agent-output/step_1_fashion_market_intelligence.json", 'w', encoding='utf-8') as f:
                json.dump(sample_market_data, f, ensure_ascii=False, indent=2)
            
            with open("ai-agent-output/step_2_pricing_decision.json", 'w', encoding='utf-8') as f:
                json.dump(sample_pricing_data, f, ensure_ascii=False, indent=2)
            
            st.success("✅ Sample data generated!")
            st.info("🔄 Refresh the page to see the sample data in action")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    🛍️ <strong>Salla Price Optimizer</strong> | Bypass Dashboard | Fashion Edition<br>
    <small>This dashboard works without authentication for testing purposes</small>
</div>
""", unsafe_allow_html=True)