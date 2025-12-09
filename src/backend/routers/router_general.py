"""
General Router
Handles general AI endpoints: /ask, /rag, /translate
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..utils.schema_validator import (
    QueryRequest, LLMResponse,
    RAGRequest, RAGResponse,
    TranslationRequest, TranslationResponse
)
from ..utils.response_formatter import (
    format_llm_response,
    format_rag_response,
    format_translation_response,
    format_error,
    format_success
)
from ..services.llm_service import llm_service
from ..services.rag_service import rag_service
from ..services.translate_service import translate_service
from ..services.history_service import history_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["general"])


@router.post("/ask", response_model=LLMResponse)
async def ask_llm(request: QueryRequest) -> Dict[str, Any]:
    """
    Ask a question to the Mini LLM
    
    Query the fine-tuned DistilGPT-2 model with agricultural context
    """
    try:
        logger.info(f"POST /ask - query: {request.query[:100]}")
        
        # Process query
        result = await llm_service.query(
            query=request.query,
            mode=request.mode or "auto"
        )
        
        # Log to history
        await history_service.log_query(
            endpoint="/ask",
            query_data={"query": request.query, "mode": request.mode},
            response_data=result,
            execution_time=result.get("execution_time", 0)
        )
        
        # Format response
        formatted_response = format_llm_response(
            answer=result.get("final_answer", ""),
            tools_used=result.get("tools_used", []),
            execution_time=result.get("execution_time", 0.0),
            sources=result.get("sources", None)
        )
        
        # Return only the data part to match LLMResponse schema
        return formatted_response["data"]
        
    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag", response_model=RAGResponse)
async def query_rag(request: RAGRequest) -> Dict[str, Any]:
    """
    Query the RAG vectorstore
    
    Retrieve relevant agricultural knowledge from ChromaDB
    """
    try:
        logger.info(f"POST /rag - query: {request.query[:100]}")
        
        # Retrieve documents
        result = await rag_service.retrieve(
            query=request.query,
            top_k=request.top_k or 5
        )
        
        logger.info(f"RAG result keys: {list(result.keys())}")
        logger.info(f"RAG result: {result}")
        
        # Log to history (temporarily disabled for debugging)
        # await history_service.log_query(
        #     endpoint="/rag",
        #     query_data={"query": request.query, "top_k": request.top_k},
        #     response_data=result,
        #     execution_time=result.get("execution_time", 0)
        # )
        
        # Return data directly (RAGResponse expects direct fields)
        return {
            "documents": result["documents"],
            "num_results": result["num_results"],
            "context": result["context"],
            "avg_relevance": result["avg_relevance"]
        }
        
    except Exception as e:
        logger.error(f"Error in /rag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_text(request: TranslationRequest) -> Dict[str, Any]:
    """
    Translate text between languages
    
    Supported languages: en, hi, es, fr, zh, ar, pt, bn, ru
    """
    try:
        logger.info(f"POST /translate - {request.source_lang} -> {request.target_lang}")
        
        # Translate
        result = await translate_service.translate(
            text=request.text,
            source_lang=request.source_lang or "auto",
            target_lang=request.target_lang
        )
        
        # Log to history
        await history_service.log_query(
            endpoint="/translate",
            query_data={
                "text": request.text[:100],
                "source_lang": request.source_lang,
                "target_lang": request.target_lang
            },
            response_data=result,
            execution_time=result.get("execution_time", 0)
        )
        
        # Format response
        response_data = format_success({
            "translated_text": result.get("translated_text", request.text),
            "original_text": request.text,
            "source_lang": request.source_lang or "auto",
            "target_lang": request.target_lang,
            "detected_language": result.get("detected_language", request.source_lang),
            "execution_time": result.get("execution_time", 0)
        }, "Translation complete")
        
        logger.info(f"🟡 Returning translation response: {len(response_data.get('data', {}).get('translated_text', ''))} chars")
        return response_data
        
    except Exception as e:
        logger.error(f"Error in /translate: {e}")
        raise HTTPException(status_code=500, detail=str(e))
