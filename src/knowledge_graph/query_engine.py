"""
AgriKG Query Engine
Query the Agriculture Knowledge Graph using Cypher queries.
"""

from typing import Dict, Any, List, Optional
from py2neo import Graph
import os
from dotenv import load_dotenv
from .ontology import SAMPLE_QUERIES

load_dotenv()


class AgriKGQueryEngine:
    """Query engine for Agriculture Knowledge Graph."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize query engine.
        
        Args:
            uri: Neo4j URI
            user: Neo4j username
            password: Neo4j password
        """
        self.name = "agri_kg_query"
        self.description = "Query the Agriculture Knowledge Graph for relationships between crops, diseases, pests, fertilizers, etc."
        
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        
        self.graph = None
        self.is_loaded = False
    
    def load(self) -> bool:
        """Load/connect to Neo4j database."""
        try:
            self.graph = Graph(self.uri, auth=(self.user, self.password))
            self.is_loaded = True
            print(f"✓ AgriKG Query Engine connected to Neo4j")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            return False
    
    def execute_cypher(self, query: str, parameters: Dict = None) -> Dict[str, Any]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            Query results
        """
        try:
            if not self.is_loaded:
                if not self.load():
                    return {
                        "success": False,
                        "error": "Failed to connect to knowledge graph",
                        "tool": self.name
                    }
            
            # Execute query
            result = self.graph.run(query, parameters or {})
            data = result.data()
            
            return {
                "success": True,
                "tool": self.name,
                "query": query,
                "results": data,
                "count": len(data)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "tool": self.name,
                "query": query
            }
    
    def get_diseases_for_crop(self, crop_name: str) -> Dict[str, Any]:
        """Get all diseases affecting a crop."""
        query = SAMPLE_QUERIES['diseases_for_crop']
        return self.execute_cypher(query, {"crop_name": crop_name})
    
    def get_pests_for_crop(self, crop_name: str) -> Dict[str, Any]:
        """Get all pests affecting a crop."""
        query = SAMPLE_QUERIES['pests_for_crop']
        return self.execute_cypher(query, {"crop_name": crop_name})
    
    def get_fertilizers_for_crop(self, crop_name: str) -> Dict[str, Any]:
        """Get fertilizers required for a crop."""
        query = SAMPLE_QUERIES['fertilizers_for_crop']
        return self.execute_cypher(query, {"crop_name": crop_name})
    
    def get_ideal_soil_for_crop(self, crop_name: str) -> Dict[str, Any]:
        """Get ideal soil types for a crop."""
        query = SAMPLE_QUERIES['ideal_soil_for_crop']
        return self.execute_cypher(query, {"crop_name": crop_name})
    
    def get_crops_for_region(self, region_name: str) -> Dict[str, Any]:
        """Get crops suitable for a region."""
        query = SAMPLE_QUERIES['crops_for_region']
        return self.execute_cypher(query, {"region_name": region_name})
    
    def get_treatment_for_disease(self, disease_name: str) -> Dict[str, Any]:
        """Get treatments for a disease."""
        query = SAMPLE_QUERIES['treatment_for_disease']
        return self.execute_cypher(query, {"disease_name": disease_name})
    
    def get_pesticides_for_pest(self, pest_name: str) -> Dict[str, Any]:
        """Get pesticides for a pest."""
        query = SAMPLE_QUERIES['pesticides_for_pest']
        return self.execute_cypher(query, {"pest_name": pest_name})
    
    def get_complete_crop_info(self, crop_name: str) -> Dict[str, Any]:
        """Get complete information about a crop."""
        query = SAMPLE_QUERIES['crop_complete_info']
        return self.execute_cypher(query, {"crop_name": crop_name})
    
    def natural_language_query(self, question: str) -> Dict[str, Any]:
        """
        Process natural language question and route to appropriate query.
        
        Args:
            question: Natural language question
            
        Returns:
            Query results
        """
        question_lower = question.lower()
        
        # Extract crop name
        crops = ['rice', 'wheat', 'maize', 'paddy', 'corn']
        crop_name = None
        for crop in crops:
            if crop in question_lower:
                crop_name = 'rice' if crop == 'paddy' else crop
                crop_name = 'maize' if crop == 'corn' else crop_name
                break
        
        if not crop_name:
            return {
                "success": False,
                "error": "Could not identify crop from question",
                "tool": self.name
            }
        
        # Route to appropriate query
        if any(word in question_lower for word in ['disease', 'diseases', 'infection', 'pathogen']):
            return self.get_diseases_for_crop(crop_name)
        
        elif any(word in question_lower for word in ['pest', 'pests', 'insect', 'insects']):
            return self.get_pests_for_crop(crop_name)
        
        elif any(word in question_lower for word in ['fertilizer', 'fertilizers', 'nutrient', 'nutrients']):
            return self.get_fertilizers_for_crop(crop_name)
        
        elif any(word in question_lower for word in ['soil', 'soils']):
            return self.get_ideal_soil_for_crop(crop_name)
        
        elif any(word in question_lower for word in ['treatment', 'cure', 'control', 'manage']):
            # Extract disease name
            disease = None
            diseases = ['blight', 'rot', 'rust', 'smut', 'blast', 'wilt']
            for d in diseases:
                if d in question_lower:
                    disease = d
                    break
            
            if disease:
                return self.get_treatment_for_disease(disease)
            else:
                return self.get_diseases_for_crop(crop_name)
        
        else:
            # Default: get complete info
            return self.get_complete_crop_info(crop_name)
    
    def run(self, query: str = None, cypher: str = None, parameters: Dict = None) -> Dict[str, Any]:
        """
        Run a query (natural language or Cypher).
        
        Args:
            query: Natural language query
            cypher: Cypher query
            parameters: Query parameters
            
        Returns:
            Query results
        """
        if cypher:
            return self.execute_cypher(cypher, parameters)
        elif query:
            return self.natural_language_query(query)
        else:
            return {
                "success": False,
                "error": "Either 'query' or 'cypher' must be provided",
                "tool": self.name
            }
    
    def __call__(self, query: str = None, cypher: str = None, **kwargs) -> Dict[str, Any]:
        """Allow engine to be called directly."""
        return self.run(query=query, cypher=cypher, parameters=kwargs)
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """
        Format query results for display.
        
        Args:
            results: Query results
            
        Returns:
            Formatted string
        """
        if not results.get("success"):
            return f"Error: {results.get('error', 'Unknown error')}"
        
        if results.get("count", 0) == 0:
            return "No results found."
        
        formatted = []
        for item in results.get("results", []):
            parts = []
            for key, value in item.items():
                if value:
                    parts.append(f"{key}: {value}")
            if parts:
                formatted.append(" | ".join(parts))
        
        return "\n".join(formatted)


if __name__ == "__main__":
    # Test queries
    engine = AgriKGQueryEngine()
    
    print("\n" + "="*70)
    print("🌾 AgriKG Query Engine Test")
    print("="*70 + "\n")
    
    # Test 1: Get diseases for rice
    print("Query 1: Diseases affecting rice")
    result = engine.get_diseases_for_crop("rice")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Results: {result['count']}")
        print(engine.format_results(result))
    print()
    
    # Test 2: Natural language query
    print("Query 2: Natural language - 'What diseases affect wheat?'")
    result = engine.natural_language_query("What diseases affect wheat?")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Results: {result['count']}")
        print(engine.format_results(result))
    print()
    
    print("="*70)
