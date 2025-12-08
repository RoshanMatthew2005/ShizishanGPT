"""
Agent Service
Handles ReAct agent orchestration using Mini LangChain
"""

import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Add project root to path to import orchestration modules
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.orchestration.main_orchestrator import ShizishanGPTOrchestrator
    ORCHESTRATOR_AVAILABLE = True
    logger.info("✓ Orchestrator module imported successfully")
except ImportError as e:
    logger.error(f"Failed to import orchestrator: {e}")
    logger.error(f"Python path: {sys.path[:5]}")
    logger.error(f"Project root: {project_root}")
    ORCHESTRATOR_AVAILABLE = False


class AgentService:
    """
    Service for ReAct agent operations using Mini LangChain
    """
    
    def __init__(self):
        self.orchestrator = None
        self.initialized = False
    
    def initialize(self):
        """Initialize the orchestrator"""
        if not ORCHESTRATOR_AVAILABLE:
            logger.error("Orchestrator not available")
            return False
        
        try:
            if self.orchestrator is None:
                self.orchestrator = ShizishanGPTOrchestrator()
                logger.info("✓ Agent orchestrator initialized")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            self.initialized = False
            return False
    
    async def process_query(self, 
                           query: str, 
                           mode: str = "auto",
                           max_iterations: int = 5,
                           verbose: bool = False) -> Dict[str, Any]:
        """
        Process query using ReAct agent
        
        Args:
            query: User query
            mode: Processing mode (auto, react, direct, pipeline)
            max_iterations: Maximum agent iterations
            verbose: Enable verbose logging
        
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                self.initialize()
            
            if not self.initialized:
                # Return error if orchestrator not available - don't use Mini LLM
                logger.error("Orchestrator not available - cannot process query")
                return {
                    "final_answer": "I apologize, but the system is currently unavailable. Please try again in a moment.",
                    "answer": "I apologize, but the system is currently unavailable. Please try again in a moment.",
                    "tools_used": [],
                    "execution_time": time.time() - start_time,
                    "sources": None,
                    "confidence": None,
                    "error": "Orchestrator initialization failed"
                }
            
            logger.info(f"Processing agent query (mode={mode}): {query[:100]}...")
            
            # Process using orchestrator
            result = self.orchestrator.query(query, mode=mode)
            
            execution_time = time.time() - start_time
            
            # Check if result is already properly formatted
            if isinstance(result, dict) and "final_answer" in result:
                # Result is already properly formatted, just update execution time
                result["execution_time"] = execution_time
                response = result
            else:
                # Format basic result
                response = {
                    "final_answer": result.get("final_answer", result.get("answer", "")),
                    "answer": result.get("final_answer", result.get("answer", "")),
                    "tools_used": result.get("tools_used", []),
                    "execution_time": execution_time,
                    "sources": result.get("sources"),
                    "confidence": result.get("confidence"),
                    "metadata": {
                        "mode": mode,
                        "max_iterations": max_iterations,
                        "iterations_used": result.get("iterations", 0)
                    }
                }
            
            logger.info(f"Agent query completed in {execution_time:.2f}s")
            logger.info(f"Tools used: {response.get('tools_used', [])}")
            
            return response
            
        except Exception as e:
            logger.error(f"Agent query failed: {e}")
            
            # Return error - don't use Mini LLM fallback
            return {
                "final_answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "tools_used": [],
                "execution_time": time.time() - start_time,
                "sources": None,
                "confidence": None,
                "error": str(e)
            }


# Global service instance
agent_service = AgentService()
