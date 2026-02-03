"""
Utility functions for the Salla Price Optimizer system.
This file contains helper functions and utilities used across the project.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def ensure_output_directory(output_dir: str = "./ai-agent-output") -> str:
    """
    Ensure the output directory exists and return its path.
    
    Args:
        output_dir: Path to the output directory
        
    Returns:
        str: The absolute path to the output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return os.path.abspath(output_dir)

def save_json_report(data: Dict[Any, Any], filename: str, output_dir: str = "./ai-agent-output") -> str:
    """
    Save a dictionary as a JSON file with timestamp.
    
    Args:
        data: Dictionary to save
        filename: Name of the file (without extension)
        output_dir: Directory to save the file
        
    Returns:
        str: Path to the saved file
    """
    ensure_output_directory(output_dir)
    
    # Add timestamp to the data
    if isinstance(data, dict):
        data['timestamp'] = datetime.now().isoformat()
    
    filepath = os.path.join(output_dir, f"{filename}.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Report saved successfully: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save report {filepath}: {str(e)}")
        raise

def load_json_report(filename: str, output_dir: str = "./ai-agent-output") -> Dict[Any, Any]:
    """
    Load a JSON report from file.
    
    Args:
        filename: Name of the file (with or without .json extension)
        output_dir: Directory containing the file
        
    Returns:
        Dict: Loaded data
    """
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Report loaded successfully: {filepath}")
        return data
    except FileNotFoundError:
        logger.error(f"Report file not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Failed to load report {filepath}: {str(e)}")
        raise

def validate_environment_variables() -> Dict[str, bool]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Dict[str, bool]: Status of each required environment variable
    """
    required_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'SALLA_ACCESS_TOKEN': os.getenv('SALLA_ACCESS_TOKEN'),
        'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY')
    }
    
    status = {}
    for var_name, var_value in required_vars.items():
        status[var_name] = bool(var_value and var_value.strip())
        if not status[var_name]:
            logger.warning(f"Environment variable {var_name} is not set or empty")
    
    return status

def format_price(price: float, currency: str = "SAR") -> str:
    """
    Format a price value for display.
    
    Args:
        price: Price value
        currency: Currency code
        
    Returns:
        str: Formatted price string
    """
    return f"{price:.2f} {currency}"

def calculate_profit_margin(selling_price: float, cost_price: float) -> Dict[str, float]:
    """
    Calculate profit margin percentage and amount.
    
    Args:
        selling_price: The selling price
        cost_price: The cost price
        
    Returns:
        Dict containing margin_percentage and margin_amount
    """
    if cost_price <= 0:
        raise ValueError("Cost price must be greater than 0")
    
    margin_amount = selling_price - cost_price
    margin_percentage = (margin_amount / cost_price) * 100
    
    return {
        'margin_percentage': round(margin_percentage, 2),
        'margin_amount': round(margin_amount, 2)
    }

def is_price_reasonable(price: float, min_price: float = 1.0, max_price: float = 10000.0) -> bool:
    """
    Check if a price is within reasonable bounds.
    
    Args:
        price: Price to validate
        min_price: Minimum acceptable price
        max_price: Maximum acceptable price
        
    Returns:
        bool: True if price is reasonable
    """
    return min_price <= price <= max_price

def get_risk_level(margin_percentage: float, price_change_percentage: float) -> str:
    """
    Determine risk level based on margin and price change.
    
    Args:
        margin_percentage: Profit margin percentage
        price_change_percentage: Percentage change in price
        
    Returns:
        str: Risk level (Low, Medium, High)
    """
    if margin_percentage > 15 and abs(price_change_percentage) < 10:
        return "Low"
    elif margin_percentage >= 5 and abs(price_change_percentage) <= 20:
        return "Medium"
    else:
        return "High"

# Example usage and testing
if __name__ == "__main__":
    # Test the utility functions
    print("Testing Salla Price Optimizer utilities...")
    
    # Test environment validation
    env_status = validate_environment_variables()
    print(f"Environment variables status: {env_status}")
    
    # Test price formatting
    print(f"Formatted price: {format_price(99.99)}")
    
    # Test profit margin calculation
    try:
        margin = calculate_profit_margin(100, 80)
        print(f"Profit margin: {margin}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test risk assessment
    risk = get_risk_level(20, 5)
    print(f"Risk level: {risk}")
    
    print("Utility tests completed!")