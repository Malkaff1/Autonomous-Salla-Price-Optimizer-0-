"""
Multi-Tenant Price Optimizer
Runs the optimization workflow for individual stores with data isolation
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
import shutil

from database.db import get_db
from database.models import Store, Product, Competitor, PricingDecision
from crewai import Crew, Process, LLM
from agents.scout_agent import scout_agent, scout_task
from agents.analysis_agent import get_pricing_analyst
from agents.executor_agent import get_executor_agent

logger = logging.getLogger(__name__)


class MultiTenantOptimizer:
    """
    Handles price optimization for multiple stores with data isolation
    """
    
    def __init__(self):
        self.base_output_dir = "./store-data"
        os.makedirs(self.base_output_dir, exist_ok=True)
    
    def get_store_output_dir(self, store_id: str) -> str:
        """Get isolated output directory for a specific store"""
        store_dir = os.path.join(self.base_output_dir, store_id)
        os.makedirs(store_dir, exist_ok=True)
        return store_dir
    
    def cleanup_store_output(self, store_id: str):
        """Clean store's output directory for fresh data"""
        store_dir = self.get_store_output_dir(store_id)
        
        try:
            # Remove all JSON files
            for filename in os.listdir(store_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(store_dir, filename)
                    os.remove(file_path)
                    logger.info(f"🗑️  Removed old file: {filename}")
        except Exception as e:
            logger.error(f"Error cleaning store output: {e}")
    
    def set_store_environment(self, store: Store):
        """Set environment variables for specific store"""
        os.environ["SALLA_ACCESS_TOKEN"] = store.access_token
        os.environ["SALLA_REFRESH_TOKEN"] = store.refresh_token
        os.environ["SALLA_STORE_ID"] = store.store_id
        os.environ["SALLA_STORE_NAME"] = store.store_name
        
        # Set store-specific output directory
        store_output_dir = self.get_store_output_dir(store.store_id)
        os.environ["AI_AGENT_OUTPUT_DIR"] = store_output_dir
    
    def optimize_single_store(self, store_id: str) -> Dict[str, Any]:
        """
        Run complete optimization workflow for a single store
        
        Args:
            store_id: Salla store ID
            
        Returns:
            Dictionary with optimization results and statistics
        """
        logger.info(f"🚀 Starting optimization for store: {store_id}")
        
        start_time = datetime.utcnow()
        
        try:
            # Get store from database
            with get_db() as db:
                store = db.query(Store).filter(Store.store_id == store_id).first()
                
                if not store:
                    logger.error(f"Store {store_id} not found")
                    return {
                        "success": False,
                        "error_message": "Store not found"
                    }
                
                if not store.is_active:
                    logger.info(f"Store {store_id} is inactive")
                    return {
                        "success": False,
                        "error_message": "Store is inactive"
                    }
                
                # Set store-specific environment
                self.set_store_environment(store)
                
                # Clean previous output
                self.cleanup_store_output(store_id)
                
                logger.info(f"📊 Store: {store.store_name}")
                logger.info(f"⚙️  Automation Mode: {store.automation_mode}")
                logger.info(f"💰 Min Profit Margin: {store.min_profit_margin}%")
            
            # Initialize LLM
            llm = LLM(model="gpt-4o", temperature=0)
            
            # Create agents and tasks
            analyst_agent, analyst_task = get_pricing_analyst(llm, scout_task)
            executor_agent, executor_task = get_executor_agent(llm, analyst_task)
            
            # Create crew
            crew = Crew(
                agents=[scout_agent, analyst_agent, executor_agent],
                tasks=[scout_task, analyst_task, executor_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Run optimization
            logger.info("🤖 Running AI agents...")
            result = crew.kickoff()
            
            # Parse results from output files
            store_output_dir = self.get_store_output_dir(store_id)
            
            market_file = os.path.join(store_output_dir, "step_1_fashion_market_intelligence.json")
            pricing_file = os.path.join(store_output_dir, "step_2_pricing_decision.json")
            execution_file = os.path.join(store_output_dir, "step_3_execution_report.json")
            
            # Load results
            market_data = self._load_json(market_file)
            pricing_data = self._load_json(pricing_file)
            execution_data = self._load_json(execution_file)
            
            # Save results to database
            self._save_to_database(store_id, market_data, pricing_data, execution_data)
            
            # Calculate statistics
            stats = self._calculate_statistics(market_data, pricing_data, execution_data)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"✅ Optimization completed in {duration:.2f}s")
            logger.info(f"📊 Stats: {stats}")
            
            return {
                "success": True,
                "store_id": store_id,
                "duration_seconds": int(duration),
                **stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error optimizing store {store_id}: {str(e)}")
            return {
                "success": False,
                "store_id": store_id,
                "error_message": str(e),
                "products_analyzed": 0,
                "products_updated": 0,
                "products_skipped": 0,
                "competitors_found": 0
            }
    
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file safely"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
        return {}
    
    def _save_to_database(self, store_id: str, market_data: Dict, pricing_data: Dict, execution_data: Dict):
        """Save optimization results to database"""
        try:
            with get_db() as db:
                # Save/update products
                products = market_data.get('products', [])
                for product_data in products:
                    product_id = str(product_data.get('product_id', ''))
                    if not product_id:
                        continue
                    
                    # Check if product exists
                    product = db.query(Product).filter(
                        Product.store_id == store_id,
                        Product.product_id == product_id
                    ).first()
                    
                    if product:
                        # Update existing
                        product.name = product_data.get('name', product.name)
                        product.current_price = product_data.get('price', product.current_price)
                        product.cost_price = product_data.get('cost_price', product.cost_price)
                        product.category = product_data.get('category', product.category)
                        product.updated_at = datetime.utcnow()
                    else:
                        # Create new
                        product = Product(
                            store_id=store_id,
                            product_id=product_id,
                            name=product_data.get('name', 'Unknown'),
                            current_price=product_data.get('price', 0),
                            cost_price=product_data.get('cost_price', 0),
                            category=product_data.get('category', 'Fashion'),
                            sku=product_data.get('sku', ''),
                            description=product_data.get('description', '')
                        )
                        db.add(product)
                    
                    # Save competitors
                    competitors = product_data.get('competitors', [])
                    for comp_data in competitors:
                        competitor = Competitor(
                            store_id=store_id,
                            product_id=product_id,
                            competitor_name=comp_data.get('store_name', 'Unknown'),
                            competitor_url=comp_data.get('url', ''),
                            competitor_price=comp_data.get('price', 0),
                            competitor_platform=comp_data.get('platform', 'Salla'),
                            confidence_score=comp_data.get('confidence_score', 0.8),
                            is_valid=comp_data.get('is_valid', True)
                        )
                        db.add(competitor)
                
                # Save pricing decision
                if pricing_data:
                    decision = PricingDecision(
                        store_id=store_id,
                        product_id=str(pricing_data.get('product_id', '')),
                        old_price=pricing_data.get('current_price', 0),
                        suggested_price=pricing_data.get('suggested_price', 0),
                        final_price=pricing_data.get('suggested_price', 0),
                        strategy_used=pricing_data.get('strategy_used', 'hold'),
                        risk_level=pricing_data.get('risk_level', 'high'),
                        profit_margin_percentage=pricing_data.get('profit_margin_percentage', 0),
                        action_taken=execution_data.get('action_taken', 'skipped'),
                        reasoning=pricing_data.get('reasoning', ''),
                        decided_at=datetime.utcnow()
                    )
                    db.add(decision)
                
                db.commit()
                logger.info("💾 Results saved to database")
                
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def _calculate_statistics(self, market_data: Dict, pricing_data: Dict, execution_data: Dict) -> Dict:
        """Calculate optimization statistics"""
        products = market_data.get('products', [])
        
        total_competitors = 0
        for product in products:
            total_competitors += len(product.get('competitors', []))
        
        action_taken = execution_data.get('action_taken', 'skipped') if execution_data else 'skipped'
        
        return {
            "products_analyzed": len(products),
            "products_updated": 1 if action_taken == 'updated' else 0,
            "products_skipped": 1 if action_taken == 'skipped' else 0,
            "competitors_found": total_competitors
        }


if __name__ == "__main__":
    # Test optimizer
    optimizer = MultiTenantOptimizer()
    result = optimizer.optimize_single_store("test_store_id")
    print(json.dumps(result, indent=2))
