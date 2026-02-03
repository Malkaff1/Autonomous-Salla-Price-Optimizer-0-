import os
import shutil
import logging
from crewai import Crew, Process, LLM
from agents.scout_agent import scout_agent, scout_task
from agents.analysis_agent import get_pricing_analyst
from agents.executor_agent import get_executor_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure output directory exists
output_dir = "./ai-agent-output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def cleanup_output_directory():
    """Clean the ai-agent-output directory to ensure fresh data."""
    try:
        if os.path.exists(output_dir):
            # Remove all files in the directory
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"🗑️ Removed old file: {filename}")
            logger.info("✅ Output directory cleaned successfully")
        else:
            os.makedirs(output_dir)
            logger.info("📁 Created fresh output directory")
    except Exception as e:
        logger.error(f"Failed to clean output directory: {str(e)}")

def main():
    """Main orchestrator for the Salla Fashion Price Optimizer system."""
    try:
        logger.info("🚀 Initializing Salla Fashion Price Optimizer...")
        
        # Clean output directory for fresh data
        cleanup_output_directory()
        
        # Initialize LLM
        llm = LLM(model="gpt-4o", temperature=0)
        logger.info("🤖 LLM initialized successfully")
        
        # Create agents and tasks
        logger.info("👥 Creating fashion-focused agents and tasks...")
        analyst_agent, analyst_task = get_pricing_analyst(llm, scout_task)
        executor_agent, executor_task = get_executor_agent(llm, analyst_task)
        logger.info("✅ All agents created successfully")
        
        # Create the Crew
        logger.info("🎯 Creating fashion optimization crew...")
        salla_fashion_crew = Crew(
            agents=[scout_agent, analyst_agent, executor_agent],
            tasks=[scout_task, analyst_task, executor_task],
            process=Process.sequential,  # Steps: 1. Scout -> 2. Analyze -> 3. Execute
            verbose=True
        )
        logger.info("✅ Crew created successfully")
        
        # Kickoff the project with dynamic discovery (no hardcoded product names)
        logger.info("🔍 Starting Dynamic Fashion Product Discovery & Price Optimization...")
        logger.info("📊 System will automatically discover products from your Salla store")
        logger.info("🎯 Targeting Saudi fashion retailers: Namshi, Styli, H&M, Zara, Centrepoint")
        
        result = salla_fashion_crew.kickoff(inputs={})  # No hardcoded inputs - dynamic discovery
        
        logger.info("🎉 Fashion Price Optimization workflow completed successfully!")
        logger.info("📁 Check ./ai-agent-output/ for detailed reports")
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()