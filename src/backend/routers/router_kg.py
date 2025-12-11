"""
AgriKG FastAPI Routes
API endpoints for querying the Agriculture Knowledge Graph.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge_graph.query_engine import AgriKGQueryEngine


router = APIRouter(prefix="/api/kg", tags=["Knowledge Graph"])

# Initialize query engine
kg_engine = AgriKGQueryEngine()


class CypherQueryRequest(BaseModel):
    """Request model for Cypher queries."""
    cypher: str
    parameters: Optional[Dict[str, Any]] = None


class NaturalQueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str


class CropQueryRequest(BaseModel):
    """Request model for crop-specific queries."""
    crop_name: str
    query_type: str  # diseases, pests, fertilizers, soil, complete


@router.get("/health")
async def health_check():
    """Check if knowledge graph is available."""
    is_connected = kg_engine.load()
    return {
        "status": "healthy" if is_connected else "unavailable",
        "service": "AgriKG",
        "connected": is_connected
    }


@router.post("/query/cypher")
async def query_cypher(request: CypherQueryRequest):
    """
    Execute a Cypher query.
    
    Example:
    ```json
    {
        "cypher": "MATCH (c:Crop {name: $crop_name})-[:AFFECTED_BY_DISEASE]->(d:Disease) RETURN d.name",
        "parameters": {"crop_name": "rice"}
    }
    ```
    """
    try:
        result = kg_engine.execute_cypher(request.cypher, request.parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/natural")
async def query_natural(request: NaturalQueryRequest):
    """
    Query using natural language.
    
    Example:
    ```json
    {
        "query": "What diseases affect rice?"
    }
    ```
    """
    try:
        result = kg_engine.natural_language_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop/diseases")
async def get_crop_diseases(request: CropQueryRequest):
    """Get diseases affecting a crop."""
    try:
        result = kg_engine.get_diseases_for_crop(request.crop_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop/pests")
async def get_crop_pests(request: CropQueryRequest):
    """Get pests affecting a crop."""
    try:
        result = kg_engine.get_pests_for_crop(request.crop_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop/fertilizers")
async def get_crop_fertilizers(request: CropQueryRequest):
    """Get fertilizers for a crop."""
    try:
        result = kg_engine.get_fertilizers_for_crop(request.crop_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop/soil")
async def get_crop_soil(request: CropQueryRequest):
    """Get ideal soil for a crop."""
    try:
        result = kg_engine.get_ideal_soil_for_crop(request.crop_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop/info")
async def get_crop_info(request: CropQueryRequest):
    """Get complete information about a crop."""
    try:
        result = kg_engine.get_complete_crop_info(request.crop_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get knowledge graph statistics."""
    try:
        if not kg_engine.is_loaded:
            kg_engine.load()
        
        # Get node counts
        stats = {}
        labels = ['Crop', 'Disease', 'Pest', 'Fertilizer', 'Pesticide', 
                 'Soil', 'Climate', 'Region', 'Nutrient', 'Treatment']
        
        for label in labels:
            result = kg_engine.execute_cypher(
                f"MATCH (n:{label}) RETURN count(n) as count"
            )
            if result['success'] and result['results']:
                stats[label] = result['results'][0]['count']
            else:
                stats[label] = 0
        
        # Get relationship count
        result = kg_engine.execute_cypher(
            "MATCH ()-[r]->() RETURN count(r) as count"
        )
        if result['success'] and result['results']:
            stats['total_relationships'] = result['results'][0]['count']
        else:
            stats['total_relationships'] = 0
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
