import os
import requests
import time
import logging
from crewai import Agent, Task
from crewai.tools import tool
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

class ExecutionResult(BaseModel):
    product_id: str = Field(..., description="The Salla product ID")
    product_name: str = Field(..., description="Name of the product")
    action_taken: str = Field(..., description="Action performed: Updated, Skipped, or Failed")
    old_price: float = Field(..., description="Previous price")
    new_price: float = Field(..., description="New price (if updated)")
    reason: str = Field(..., description="Reason for the action taken")
    timestamp: str = Field(..., description="When the action was performed")

# 1. Enhanced tool to interact with Salla API for updating prices
@tool("update_salla_product_price")
def update_salla_product_price(product_id: str, new_price: float):
    """
    Updates the price of a specific product in the Salla store using the Salla API.
    Includes proper error handling and rate limiting.
    """
    token = os.getenv("SALLA_ACCESS_TOKEN")
    if not token:
        logger.error("SALLA_ACCESS_TOKEN not found in environment variables")
        return "Error: Missing Salla access token"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Salla API endpoint for updating a product
    url = f"https://api.salla.dev/admin/v2/products/{product_id}"
    payload = {
        "price": {
            "amount": new_price,
            "currency": "SAR"
        }
    }
    
    try:
        # Add rate limiting to respect API limits
        time.sleep(1)
        
        logger.info(f"Attempting to update product {product_id} to {new_price} SAR")
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Successfully updated product {product_id} price to {new_price} SAR")
            return f"Success: Product {product_id} price updated to {new_price} SAR."
        elif response.status_code == 404:
            logger.error(f"Product {product_id} not found")
            return f"Failed: Product {product_id} not found in Salla store."
        elif response.status_code == 401:
            logger.error("Unauthorized access to Salla API")
            return "Failed: Invalid or expired Salla access token."
        elif response.status_code == 429:
            logger.error("Rate limit exceeded")
            return "Failed: API rate limit exceeded. Please try again later."
        else:
            logger.error(f"API returned status {response.status_code}: {response.text}")
            return f"Failed: API returned status {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout while updating product price")
        return "Error: Request timeout - Salla API did not respond in time"
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while updating product price")
        return "Error: Unable to connect to Salla API"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: Unexpected issue - {str(e)}"

# 2. Enhanced Agent Definition
def get_executor_agent(llm, analyst_task):
    executor_agent = Agent(
        role="Store Operations Manager",
        goal="Execute approved pricing decisions with precision and safety controls.",
        backstory=(
            "You are a meticulous operations manager with extensive experience in e-commerce "
            "platform management. You understand the critical importance of accurate price updates "
            "and the potential business impact of pricing errors. Your approach is methodical, "
            "safety-first, and you always verify decisions before execution. You have deep knowledge "
            "of Salla platform operations and API best practices."
        ),
        llm=llm,
        verbose=True,
        tools=[update_salla_product_price],
        allow_delegation=False,
        max_iter=2
    )

    # 3. Enhanced Task Definition
    executor_task = Task(
        description=(
            "Execute the pricing decision with appropriate safety controls and validation.\n\n"
            "EXECUTION PROTOCOL:\n\n"
            "STEP 1 - Decision Validation:\n"
            "• Review the pricing decision from the Analyst Agent\n"
            "• Verify all required fields are present: product_id, suggested_price, risk_level\n"
            "• Validate that the suggested_price is reasonable (> 0, < 10000 SAR)\n\n"
            "STEP 2 - Risk-Based Execution:\n"
            "• LOW RISK: Execute price update immediately using update_salla_product_price tool\n"
            "• MEDIUM RISK: Execute price update with additional logging and monitoring\n"
            "• HIGH RISK: DO NOT execute - flag for manual review and create detailed report\n\n"
            "STEP 3 - Execution Monitoring:\n"
            "• Log all actions taken (updated, skipped, failed)\n"
            "• Record timestamps and reasons for each decision\n"
            "• Handle API errors gracefully and provide clear feedback\n\n"
            "STEP 4 - Result Documentation:\n"
            "• Create a comprehensive execution report\n"
            "• Include success/failure status, old/new prices, and any issues encountered\n"
            "• Provide actionable recommendations for failed or skipped items\n\n"
            "SAFETY RULES:\n"
            "• Never update prices for HIGH RISK items\n"
            "• Always validate product_id exists and is not empty\n"
            "• Ensure new price is within reasonable bounds (1-10000 SAR)\n"
            "• Log all actions for audit trail"
        ),
        expected_output="A detailed execution report with all actions taken and their outcomes.",
        output_file=os.path.join("./ai-agent-output", "step_3_execution_report.json"),
        agent=executor_agent,
        context=[analyst_task]  # Depends on the output of the Analyst Agent
    )
    
    return executor_agent, executor_task