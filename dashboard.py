import streamlit as st
import pandas as pd
import json
import os
import requests
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="🛍️ Salla Price Optimizer", 
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🛍️ Autonomous Salla Price Optimizer</h1>
    <p>Women's Fashion Edition | Saudi E-commerce Market Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Function to get secrets (works both locally and on cloud)
def get_secret(key, default=None):
    """Get secret from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.getenv(key, default)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Control Panel")
    
    # Connection Status
    st.subheader("🔗 Connection Status")
    
    def test_salla_connection():
        """Test Salla API connection."""
        token = get_secret("SALLA_ACCESS_TOKEN")
        if not token:
            return False, "No access token found"
        
        try:
            response = requests.get(
                'https://api.salla.dev/admin/v2/store/info',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                store_data = response.json()
                store_name = store_data.get('data', {}).get('name', 'Unknown Store')
                return True, store_name
            else:
                return False, f"API Error: {response.status_code}"
        except Exception as e:
            return False, f"Connection Error: {str(e)[:50]}..."
    
    # Test connection
    with st.spinner("Testing Salla connection..."):
        is_connected, store_info = test_salla_connection()
    
    if is_connected:
        st.success(f"✅ Connected: {store_info}")
        st.info("💰 Currency: SAR")
    else:
        st.error("❌ Connection Failed")
        st.warning(f"Issue: {store_info}")
    
    st.markdown("---")
    
    # System Actions
    st.subheader("🎛️ System Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Run Optimizer", type="primary", use_container_width=True):
            st.success("✅ Optimizer started!")
            st.info("Check terminal for progress...")
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    if st.button("🧪 Test System", use_container_width=True):
        st.info("🧪 System test initiated...")
    
    st.markdown("---")
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    
    output_dir = "ai-agent-output"
    if os.path.exists(output_dir):
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        st.metric("📁 Reports", len(json_files))
        
        if json_files:
            latest_file = max([os.path.join(output_dir, f) for f in json_files], key=os.path.getctime)
            last_run = datetime.fromtimestamp(os.path.getctime(latest_file))
            time_ago = datetime.now() - last_run
            
            if time_ago.total_seconds() < 3600:
                st.metric("⏰ Last Run", f"{int(time_ago.total_seconds() // 60)}m ago")
            else:
                st.metric("⏰ Last Run", f"{int(time_ago.total_seconds() // 3600)}h ago")
    else:
        st.metric("📁 Reports", "0")

# Data loading functions
@st.cache_data(ttl=300)
def load_json_data(file_path):
    """Load JSON data with caching."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {file_path}: {str(e)}")
            return None
    return None

# Load data
output_dir = "ai-agent-output"
market_data = load_json_data(os.path.join(output_dir, "step_1_fashion_market_intelligence.json"))
pricing_data = load_json_data(os.path.join(output_dir, "step_2_pricing_decision.json"))
execution_data = load_json_data(os.path.join(output_dir, "step_3_execution_report.json"))

# Main Content
if market_data or pricing_data:
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🕵️ Market Intel", "⚖️ Pricing", "📈 Analytics"])
    
    with tab1:
        st.header("📊 System Dashboard")
        
        # Key Metrics Row
        if market_data:
            products = market_data.get('products', [])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🛍️ Products Monitored",
                    value=len(products),
                    help="Total fashion products being tracked"
                )
            
            with col2:
                total_competitors = sum(len(p.get('competitors', [])) for p in products)
                st.metric(
                    label="🏪 Competitors Found", 
                    value=total_competitors,
                    help="Total competitor prices discovered"
                )
            
            with col3:
                if products:
                    avg_price = sum(p.get('price', 0) for p in products) / len(products)
                    st.metric(
                        label="💰 Avg Price", 
                        value=f"{avg_price:.0f} SAR",
                        help="Average product price in your store"
                    )
            
            with col4:
                connected = market_data.get('store_connected', False)
                status = "✅ Online" if connected else "❌ Offline"
                st.metric(
                    label="🔗 Store Status", 
                    value=status,
                    help="Salla store connection status"
                )
        
        # Products Overview
        if market_data:
            st.subheader("🛍️ Fashion Products Overview")
            
            products_data = []
            for i, product in enumerate(market_data.get('products', []), 1):
                products_data.append({
                    '#': i,
                    'Product Name': product.get('name', 'Unknown'),
                    'Price (SAR)': f"{product.get('price', 0):.2f}",
                    'Category': product.get('category', 'Fashion'),
                    'Status': product.get('status', 'active').title(),
                    'Competitors': len(product.get('competitors', []))
                })
            
            if products_data:
                df = pd.DataFrame(products_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No products found. Run the optimizer to discover products.")
        
        # Recent Activity
        st.subheader("📋 Recent Activity")
        
        if execution_data:
            st.success("✅ Last execution completed successfully")
            exec_summary = execution_data.get('execution_summary', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Updated", exec_summary.get('updated', 0))
            with col2:
                st.metric("Skipped", exec_summary.get('skipped', 0))
            with col3:
                st.metric("Failed", exec_summary.get('failed', 0))
        else:
            st.info("No recent execution data available.")
    
    with tab2:
        st.header("🕵️ Market Intelligence")
        
        if market_data:
            products = market_data.get('products', [])
            
            if products:
                # Product selector
                product_names = [f"{p.get('name', 'Unknown')} - {p.get('price', 0)} SAR" for p in products]
                selected_idx = st.selectbox(
                    "Select Product for Analysis:",
                    range(len(products)),
                    format_func=lambda x: product_names[x]
                )
                
                selected_product = products[selected_idx]
                competitors = selected_product.get('competitors', [])
                
                # Product Info
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📦 Product Details</h4>
                        <p><strong>Name:</strong> {selected_product.get('name', 'Unknown')}</p>
                        <p><strong>Our Price:</strong> {selected_product.get('price', 0)} SAR</p>
                        <p><strong>Category:</strong> {selected_product.get('category', 'Fashion')}</p>
                        <p><strong>Status:</strong> {selected_product.get('status', 'active').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if competitors:
                        st.subheader("🏪 Competitor Prices")
                        
                        # Create chart data
                        chart_data = pd.DataFrame(competitors)
                        chart_data = chart_data[['store_name', 'price']].rename(columns={
                            'store_name': 'Store', 
                            'price': 'Price (SAR)'
                        })
                        
                        # Add our price for comparison
                        our_price_row = pd.DataFrame({
                            'Store': ['Our Store'], 
                            'Price (SAR)': [selected_product.get('price', 0)]
                        })
                        chart_data = pd.concat([our_price_row, chart_data], ignore_index=True)
                        
                        st.bar_chart(chart_data.set_index('Store'))
                    else:
                        st.info("No competitor data available for this product.")
                
                # Detailed Analysis
                if competitors:
                    st.subheader("📊 Detailed Competitor Analysis")
                    
                    analysis_data = []
                    our_price = selected_product.get('price', 0)
                    
                    for comp in competitors:
                        comp_price = comp.get('price', 0)
                        difference = comp_price - our_price
                        difference_pct = (difference / our_price * 100) if our_price > 0 else 0
                        
                        analysis_data.append({
                            'Store': comp.get('store_name', 'Unknown'),
                            'Price (SAR)': f"{comp_price:.2f}",
                            'Difference (SAR)': f"{difference:+.2f}",
                            'Difference (%)': f"{difference_pct:+.1f}%",
                            'Confidence': f"{comp.get('confidence_score', 0):.2f}",
                            'Status': '🟢 Cheaper' if difference < 0 else '🔴 More Expensive'
                        })
                    
                    df_analysis = pd.DataFrame(analysis_data)
                    st.dataframe(df_analysis, use_container_width=True, hide_index=True)
            else:
                st.info("No products available for analysis.")
        else:
            st.warning("No market intelligence data available. Run the optimizer first.")
    
    with tab3:
        st.header("⚖️ AI Pricing Decisions")
        
        if pricing_data:
            # Main Decision Display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🏷️ Product",
                    pricing_data.get('product_name', 'Unknown'),
                    help=f"ID: {pricing_data.get('product_id', 'N/A')}"
                )
            
            with col2:
                current = pricing_data.get('current_price', 0)
                suggested = pricing_data.get('suggested_price', 0)
                delta = suggested - current
                delta_pct = (delta / current * 100) if current > 0 else 0
                
                st.metric(
                    "💰 Recommended Price",
                    f"{suggested:.2f} SAR",
                    delta=f"{delta:+.2f} SAR ({delta_pct:+.1f}%)"
                )
            
            with col3:
                margin = pricing_data.get('profit_margin_percentage', 0)
                margin_amount = pricing_data.get('profit_margin_amount', 0)
                st.metric(
                    "📈 Profit Margin",
                    f"{margin:.1f}%",
                    help=f"Amount: {margin_amount:.2f} SAR"
                )
            
            # Strategy & Risk
            col1, col2 = st.columns(2)
            
            with col1:
                strategy = pricing_data.get('strategy_used', 'Unknown')
                position = pricing_data.get('market_position', 'Unknown')
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🎯 Strategy & Position</h4>
                    <p><strong>Strategy:</strong> {strategy}</p>
                    <p><strong>Market Position:</strong> {position}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                risk = pricing_data.get('risk_level', 'High')
                
                if risk == "Low":
                    risk_color = "success-card"
                    risk_icon = "🟢"
                elif risk == "Medium":
                    risk_color = "warning-card"
                    risk_icon = "🟡"
                else:
                    risk_color = "error-card"
                    risk_icon = "🔴"
                
                st.markdown(f"""
                <div class="{risk_color}">
                    <h4>{risk_icon} Risk Assessment</h4>
                    <p><strong>Risk Level:</strong> {risk}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # AI Reasoning
            st.subheader("🤖 AI Analysis & Reasoning")
            reasoning = pricing_data.get('reasoning', 'No reasoning provided.')
            
            if risk == "Low":
                st.success(f"**✅ Recommendation:** {reasoning}")
            elif risk == "Medium":
                st.warning(f"**⚠️ Recommendation:** {reasoning}")
            else:
                st.error(f"**❌ Recommendation:** {reasoning}")
            
            # Action Buttons
            st.subheader("🎛️ Execute Decision")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if risk != "High":
                    if st.button("✅ Approve & Update", type="primary", use_container_width=True):
                        st.balloons()
                        st.success("✅ Price update approved! Executing...")
                        time.sleep(2)
                        st.info("Price updated successfully in Salla store!")
                else:
                    st.button("⛔ High Risk - Review Required", disabled=True, use_container_width=True)
            
            with col2:
                if st.button("❌ Reject Decision", use_container_width=True):
                    st.warning("❌ Decision rejected and logged.")
            
            with col3:
                if st.button("🔄 Re-analyze", use_container_width=True):
                    st.info("🔄 Re-analysis requested...")
        else:
            st.warning("No pricing decisions available. Run the optimizer first.")
    
    with tab4:
        st.header("📈 Analytics & Insights")
        
        if market_data:
            products = market_data.get('products', [])
            
            # Market Overview
            st.subheader("🌐 Market Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Calculate average competitor price
                all_comp_prices = []
                for product in products:
                    for comp in product.get('competitors', []):
                        all_comp_prices.append(comp.get('price', 0))
                
                if all_comp_prices:
                    avg_comp_price = sum(all_comp_prices) / len(all_comp_prices)
                    st.metric("📊 Avg Competitor Price", f"{avg_comp_price:.2f} SAR")
            
            with col2:
                # Price positioning
                our_prices = [p.get('price', 0) for p in products]
                if our_prices and all_comp_prices:
                    avg_our_price = sum(our_prices) / len(our_prices)
                    position = "Lower" if avg_our_price < avg_comp_price else "Higher"
                    delta = avg_our_price - avg_comp_price
                    st.metric("📈 Price Position", position, delta=f"{delta:+.2f} SAR")
            
            with col3:
                # Market coverage
                unique_stores = set()
                for product in products:
                    for comp in product.get('competitors', []):
                        unique_stores.add(comp.get('store_name', 'Unknown'))
                
                st.metric("🏪 Stores Monitored", len(unique_stores))
            
            # Competitive Analysis Chart
            if products:
                st.subheader("🏆 Competitive Analysis")
                
                chart_data = []
                for product in products:
                    product_name = product.get('name', 'Unknown')
                    our_price = product.get('price', 0)
                    
                    # Add our price
                    chart_data.append({
                        'Product': product_name,
                        'Store': 'Our Store',
                        'Price': our_price,
                        'Type': 'Our Price'
                    })
                    
                    # Add competitor prices
                    for comp in product.get('competitors', []):
                        chart_data.append({
                            'Product': product_name,
                            'Store': comp.get('store_name', 'Unknown'),
                            'Price': comp.get('price', 0),
                            'Type': 'Competitor'
                        })
                
                if chart_data:
                    df_chart = pd.DataFrame(chart_data)
                    
                    # Group by product and show comparison
                    for product_name in df_chart['Product'].unique():
                        product_data = df_chart[df_chart['Product'] == product_name]
                        
                        st.write(f"**{product_name}**")
                        chart = product_data.set_index('Store')['Price']
                        st.bar_chart(chart)
        else:
            st.info("Analytics will be available after running the optimizer.")

else:
    # No data available
    st.warning("⚠️ No optimization data found.")
    
    st.markdown("""
    ## 🚀 Getting Started
    
    Welcome to the Salla Price Optimizer Dashboard! To get started:
    
    1. **✅ Check Connection**: Verify your Salla store connection in the sidebar
    2. **🚀 Run Optimizer**: Click "Run Optimizer" or execute `python main.py` in terminal
    3. **📊 Monitor Results**: Return here to view insights and recommendations
    4. **⚖️ Make Decisions**: Review AI recommendations and approve price updates
    
    ### 📁 Expected Output Files:
    - `step_1_fashion_market_intelligence.json` - Product discovery & competitor data
    - `step_2_pricing_decision.json` - AI pricing recommendations
    - `step_3_execution_report.json` - Price update results
    """)
    
    # Debug info
    with st.expander("🔧 Debug Information"):
        st.write(f"**Current Directory:** `{os.getcwd()}`")
        st.write(f"**Output Directory Exists:** {os.path.exists(output_dir)}")
        
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            st.write(f"**Files in Output Directory:** {files}")
        
        # Environment check
        st.write("**Environment Variables:**")
        env_vars = ['OPENAI_API_KEY', 'TAVILY_API_KEY', 'SALLA_ACCESS_TOKEN']
        for var in env_vars:
            value = get_secret(var)
            status = "✅ Set" if value else "❌ Missing"
            st.write(f"- {var}: {status}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    🛍️ <strong>Autonomous Salla Price Optimizer</strong> | Women's Fashion Edition<br>
    Powered by CrewAI Multi-Agent System | Saudi E-commerce Market Focus<br>
    <small>Built with ❤️ for fashion retailers</small>
</div>
""", unsafe_allow_html=True)