"""
Agent Router
Handles ReAct agent endpoint: /agent
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..utils.schema_validator import AgentRequest, LLMResponse
from ..utils.response_formatter import format_llm_response, format_error
from ..services.agent_service import agent_service
from ..services.history_service import history_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/agent", response_model=LLMResponse)
async def query_agent(request: AgentRequest) -> Dict[str, Any]:
    """
    Query the ReAct agent
    
    Uses Mini LangChain orchestration with tool selection:
    - Direct LLM query
    - RAG retrieval
    - Yield prediction
    - Pest detection
    - Translation
    
    Modes:
    - auto: Intelligent tool selection
    - react: Full ReAct reasoning loop
    - direct: Direct LLM only
    - pipeline: Sequential tool chain
    """
    try:
        logger.info(f"POST /agent - query: {request.query[:100]}, mode: {request.mode}")
        
        # Process query through agent
        result = await agent_service.process_query(
            query=request.query,
            mode=request.mode or "auto",
            max_iterations=request.max_iterations or 5,
            verbose=request.verbose or False
        )
        
        # Log to history
        await history_service.log_query(
            endpoint="/agent",
            query_data={
                "query": request.query,
                "mode": request.mode,
                "max_iterations": request.max_iterations
            },
            response_data=result,
            execution_time=result.get("execution_time", 0)
        )
        
        # Format response for LLM schema
        formatted_result = {
            "final_answer": result.get("final_answer", result.get("answer", "")),
            "tools_used": result.get("tools_used", []),
            "execution_time": result.get("execution_time", 0.0),
            "sources": result.get("sources"),
            "confidence": result.get("confidence")
        }
        
        return formatted_result
        
    except Exception as e:
        logger.error(f"Error in /agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
