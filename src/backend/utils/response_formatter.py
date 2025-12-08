"""
Response Formatter
Standardizes API responses
"""

from typing import Any, Optional, Dict
from datetime import datetime
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Any
    timestamp: str = datetime.utcnow().isoformat()


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    status_code: int
    details: Optional[Dict] = None
    timestamp: str = datetime.utcnow().isoformat()


def format_success(data: Any, message: str = "Success") -> Dict:
    """
    Format successful response
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


def format_error(error: str, status_code: int = 500, details: Optional[Dict] = None) -> Dict:
    """
    Format error response
    """
    return {
        "success": False,
        "error": error,
        "status_code": status_code,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }


def format_llm_response(answer: str, tools_used: list = None, execution_time: float = 0.0, sources: list = None) -> Dict:
    """
    Format LLM/Agent response
    """
    return format_success({
        "final_answer": answer,
        "answer": answer,  # Alias for compatibility
        "tools_used": tools_used or [],
        "execution_time": execution_time,
        "sources": sources,
        "confidence": None
    }, "Query processed successfully")


def format_rag_response(documents: list, context: str = "", avg_relevance: float = 0.0) -> Dict:
    """
    Format RAG retrieval response
    """
    return format_success({
        "documents": documents,
        "num_results": len(documents),
        "context": context,
        "avg_relevance": avg_relevance
    }, "Documents retrieved successfully")


def format_prediction_response(prediction: Any, model_type: str, confidence: float = None, inputs: Dict = None) -> Dict:
    """
    Format model prediction response
    """
    if model_type == "yield":
        return format_success({
            "prediction": prediction,
            "predicted_yield": prediction,
            "unit": "tonnes per hectare",
            "confidence": confidence,
            "inputs": inputs
        }, "Yield predicted successfully")
    
    elif model_type == "pest":
        return format_success({
            "top_prediction": prediction.get("disease", "Unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "all_predictions": prediction.get("all_predictions", []),
            "recommendations": prediction.get("recommendations", [])
        }, "Pest detection complete")
    
    else:
        return format_success({
            "prediction": prediction,
            "model_type": model_type
        }, "Prediction complete")


def format_translation_response(translated_text: str, source_lang: str, target_lang: str, original_text: str) -> Dict:
    """
    Format translation response
    """
    return format_success({
        "translated_text": translated_text,
        "source_language": source_lang,
        "target_language": target_lang,
        "original_text": original_text
    }, "Translation complete")
