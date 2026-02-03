import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Salla Price Optimizer Dashboard", 
    page_icon="🛍️",
    layout="wide"
)

# Test if Streamlit is working
st.title("🛍️ Salla Price Optimizer Dashboard")
st.write("Dashboard is loading...")

# Simple data loading function
def load_json_data(file_path):
    """Load JSON data with basic error handling."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            st.warning(f"File not found: {file_path}")
            return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return None

# Check if output directory exists
output_dir = "ai-agent-output"
st.write(f"Checking output directory: {output_dir}")

if os.path.exists(output_dir):
    st.success(f"✅ Output directory found: {output_dir}")
    
    # List files in directory
    files = os.listdir(output_dir)
    st.write(f"Files found: {files}")
    
    # Try to load each file
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(output_dir, file)
            st.write(f"Loading: {file}")
            data = load_json_data(file_path)
            if data:
                st.json(data)
            else:
                st.error(f"Failed to load {file}")
else:
    st.warning(f"❌ Output directory not found: {output_dir}")
    st.info("Please run the optimizer first to generate data files.")

# Basic system info
st.subheader("System Information")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Python version: {st.__version__}")
st.write(f"Current time: {datetime.now()}")

# Test button
if st.button("Test Button"):
    st.success("Button works!")
    st.balloons()