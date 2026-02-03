#!/usr/bin/env python3
"""
Production runner for the Salla Price Optimizer.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging without Unicode characters for Windows compatibility
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('optimizer.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def run_price_optimizer(product_name: str = "بطاقة شحن سوا 100"):
    """Run the complete price optimization workflow."""
    try:
        logger.info("=== Starting Salla Price Optimizer ===")
        logger.info(f"Target product: {product_name}")
        
        # Import everything we need
        from crewai import Agent, Task, Crew, Process, LLM
        from agents.scout_agent import scout_agent, scout_task
        from agents.analysis_agent import get_pricing_analyst
        from agents.executor_agent import get_executor_agent
        
        logger.info("All modules imported successfully")
        
        # Initialize LLM
        logger.info("Initializing LLM...")
        llm = LLM(model="gpt-4o", temperature=0)
        logger.info("LLM initialized")
        
        # Create agents
        logger.info("Creating agents...")
        analyst_agent, analyst_task = get_pricing_analyst(llm, scout_task)
        executor_agent, executor_task = get_executor_agent(llm, analyst_task)
        logger.info("All agents created")
        
        # Create crew
        logger.info("Creating crew...")
        crew = Crew(
            agents=[scout_agent, analyst_agent, executor_agent],
            tasks=[scout_task, analyst_task, executor_task],
            process=Process.sequential,
            verbose=True
        )
        logger.info("Crew created successfully")
        
        # Run the workflow
        logger.info("Starting workflow execution...")
        logger.info("This may take a few minutes as agents analyze the market...")
        
        result = crew.kickoff(inputs={'product_name': product_name})
        
        logger.info("=== Workflow completed successfully! ===")
        logger.info("Check the ai-agent-output/ directory for detailed reports:")
        logger.info("- step_1_market_intelligence.json")
        logger.info("- step_2_pricing_decision.json") 
        logger.info("- step_3_execution_report.json")
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def main():
    """Main entry point."""
    print("Salla Price Optimizer - Production Runner")
    print("=" * 50)
    
    # Check environment
    required_vars = ['OPENAI_API_KEY', 'TAVILY_API_KEY', 'SALLA_ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("Environment: OK")
    print("Starting optimization workflow...")
    print()
    
    # Run the optimizer
    result = run_price_optimizer()
    
    if result:
        print()
        print("SUCCESS: Price optimization completed!")
        print("Check the ai-agent-output/ directory for detailed reports.")
        return True
    else:
        print()
        print("FAILED: Price optimization failed. Check optimizer.log for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)