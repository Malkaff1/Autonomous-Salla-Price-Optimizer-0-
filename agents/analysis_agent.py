from crewai import Agent, Task
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define a robust Pydantic Model for structured pricing output
class PricingDecision(BaseModel):
    product_name: str = Field(..., description="The name of the product being analyzed.")
    product_id: str = Field(..., description="Salla product ID for API updates.")
    current_price: float = Field(..., description="Our current selling price in Salla.")
    cost_price: float = Field(..., description="The cost price of the product.")
    competitor_lowest_price: float = Field(..., description="The lowest valid competitor price found.")
    competitor_average_price: float = Field(..., description="Average price among top competitors.")
    suggested_price: float = Field(..., description="The new recommended price for our store.")
    profit_margin_percentage: float = Field(..., description="Expected profit margin as percentage.")
    profit_margin_amount: float = Field(..., description="The expected net profit in SAR per unit.")
    strategy_used: str = Field(..., description="Strategy name (e.g., Price Match, Undercut, Premium, Hold).")
    reasoning: str = Field(..., description="A detailed technical justification for the decision.")
    risk_level: str = Field(..., description="Risk assessment: Low, Medium, or High.")
    market_position: str = Field(..., description="Our position relative to competitors: Leading, Competitive, or Following.")

def get_pricing_analyst(llm, scout_task):
    """
    Creates the Analyst Agent and its corresponding task.
    Requires an LLM instance and the scout_task to maintain context.
    """
    
    # 1. Define the Analyst Agent
    analyst_agent = Agent(
        role="Senior Fashion E-commerce Pricing Strategist",
        goal="Maximize profitability while maintaining competitive positioning in the Saudi women's fashion market.",
        backstory=(
            "You are a veteran fashion pricing strategist with 10+ years of experience in the Saudi women's fashion sector. "
            "You understand fashion market psychology, seasonal trends, consumer behavior, and the delicate balance between "
            "profitability and market share in the fashion industry. Your expertise includes dynamic pricing for fashion items, "
            "competitor analysis across fashion retailers like Namshi, Styli, H&M, and Zara, and risk assessment for fashion products. "
            "You understand that fashion items often have different pricing strategies than electronics - higher margins, "
            "seasonal considerations, and brand positioning are crucial. You never compromise on the 10% minimum profit margin "
            "rule for fashion items, and you excel at identifying fashion market opportunities while protecting brand value."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )

    # 2. Define the Analytical Task
    analyst_task = Task(
        description=(
            "Analyze the market intelligence data and create an optimal pricing strategy.\n\n"
            "ANALYTICAL FRAMEWORK:\n\n"
            "STEP 1 - Data Quality Assessment:\n"
            "• Review competitor data for validity and relevance\n"
            "• Filter out outliers, suspicious prices, and non-reputable sources\n"
            "• Calculate competitor price statistics (min, max, average, median)\n\n"
            "STEP 2 - Market Position Analysis:\n"
            "• Compare our current price against competitor landscape\n"
            "• Determine our market position: Leading (cheapest), Competitive (middle), Following (expensive)\n"
            "• Assess price gaps and market opportunities\n\n"
            "STEP 3 - Pricing Strategy Selection:\n"
            "• UNDERCUT Strategy: Price 2-5 SAR below lowest competitor (if margin allows)\n"
            "• MATCH Strategy: Match the lowest competitor price exactly\n"
            "• PREMIUM Strategy: Price 5-10% above average if we're market leader\n"
            "• HOLD Strategy: Maintain current price if market is too aggressive\n\n"
            "STEP 4 - Fashion-Specific Profit Margin Validation:\n"
            "• CRITICAL RULE FOR FASHION: (suggested_price - cost_price) / cost_price >= 0.10 (10% minimum for fashion)\n"
            "• Fashion items typically require higher margins due to seasonality and trends\n"
            "• If market prices violate this rule, use HOLD strategy and flag as High Risk\n"
            "• Consider category-specific margins: Dresses (15-25%), Accessories (20-30%), Basics (10-15%)\n"
            "• Calculate expected profit margin percentage and absolute amount\n\n"
            "STEP 5 - Fashion Market Risk Assessment:\n"
            "• Low Risk: Margin > 20%, price change < 10%, strong fashion competitor data, in-season items\n"
            "• Medium Risk: Margin 10-20%, price change 10-20%, moderate competitor data, seasonal items\n"
            "• High Risk: Margin < 10%, price change > 20%, weak competitor data, out-of-season items\n"
            "• Consider fashion-specific factors: seasonality, trends, brand positioning\n\n"
            "STEP 6 - Decision Documentation:\n"
            "• Provide clear reasoning for the chosen strategy\n"
            "• Include market context and competitive landscape insights\n"
            "• Document all assumptions and risk factors"
        ),
        expected_output="A comprehensive JSON pricing decision with strategy, risk assessment, and detailed reasoning.",
        output_json=PricingDecision,
        output_file=os.path.join("./ai-agent-output", "step_2_pricing_decision.json"),
        agent=analyst_agent,
        context=[scout_task]  # Critical for data flow between agents
    )
    
    return analyst_agent, analyst_task