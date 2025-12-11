# Agriculture Knowledge Graph (AgriKG) Setup Guide

## Overview
AgriKG is a comprehensive knowledge graph for agricultural data, designed to answer relationship-based questions about crops, diseases, pests, fertilizers, soil types, and treatments.

## Architecture

### Components
1. **Extractor** (`src/knowledge_graph/extractor.py`) - Extracts triples from Word documents
2. **Ontology** (`src/knowledge_graph/ontology.py`) - Defines graph schema
3. **Builder** (`src/knowledge_graph/builder.py`) - Builds graph in Neo4j
4. **Query Engine** (`src/knowledge_graph/query_engine.py`) - Queries the graph
5. **Tool Wrapper** (`src/knowledge_graph/agri_kg_tool.py`) - Integration with ReAct agent
6. **API Routes** (`src/backend/routers/router_kg.py`) - FastAPI endpoints

### Knowledge Graph Schema

**Node Types:**
- `Crop` - Agricultural crops (rice, wheat, maize, etc.)
- `Disease` - Plant diseases
- `Pest` - Insects and pests
- `Fertilizer` - Fertilizers and nutrients
- `Pesticide` - Pesticides, fungicides, herbicides
- `Soil` - Soil types
- `Climate` - Climate zones
- `Region` - Geographic regions
- `Nutrient` - Plant nutrients
- `Treatment` - Treatment methods

**Relationship Types:**
- `AFFECTED_BY_DISEASE` - Crop ← Disease
- `AFFECTED_BY_PEST` - Crop ← Pest
- `REQUIRES_FERTILIZER` - Crop → Fertilizer
- `GROWS_IN_SOIL` - Crop → Soil
- `GROWS_IN_CLIMATE` - Crop → Climate
- `TREATED_BY` - Disease → Treatment
- `CONTROLLED_BY_PESTICIDE` - Disease/Pest → Pesticide

## Installation

### 1. Install Neo4j

**Windows:**
```powershell
# Download Neo4j Desktop from https://neo4j.com/download/
# Or use Docker:
docker run -d --name neo4j `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/password `
  neo4j:latest
```

**Access Neo4j Browser:** http://localhost:7474

### 2. Install Python Dependencies

```bash
pip install py2neo spacy python-docx
python -m spacy download en_core_web_sm
```

### 3. Configure Environment

Add to `.env`:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Building the Knowledge Graph

### Step 1: Extract Triples from Documents

```bash
python build_agri_kg.py
```

This will:
1. Read Word documents from `Data/AgriKF_Data/`
2. Extract triples (subject, relation, object)
3. Save to `data/agri_triples.csv`
4. Build the graph in Neo4j

### Step 2: Verify the Build

```bash
python test_agri_kg.py
```

## Usage

### 1. API Endpoints

**Health Check:**
```http
GET /api/kg/health
```

**Natural Language Query:**
```http
POST /api/kg/query/natural
Content-Type: application/json

{
  "query": "What diseases affect rice?"
}
```

**Cypher Query:**
```http
POST /api/kg/query/cypher
Content-Type: application/json

{
  "cypher": "MATCH (c:Crop {name: $crop_name})-[:AFFECTED_BY_DISEASE]->(d:Disease) RETURN d.name",
  "parameters": {"crop_name": "rice"}
}
```

**Crop Diseases:**
```http
POST /api/kg/crop/diseases
Content-Type: application/json

{
  "crop_name": "rice"
}
```

### 2. Python API

```python
from src.knowledge_graph.query_engine import AgriKGQueryEngine

# Initialize engine
engine = AgriKGQueryEngine()
engine.load()

# Get diseases for a crop
result = engine.get_diseases_for_crop("rice")
print(result)

# Natural language query
result = engine.natural_language_query("What pests attack wheat?")
print(result)

# Custom Cypher query
result = engine.execute_cypher(
    "MATCH (c:Crop)-[r:REQUIRES_FERTILIZER]->(f:Fertilizer) RETURN c.name, f.name",
    {}
)
print(result)
```

### 3. ReAct Agent Tool

The AgriKG is integrated as a tool in the ReAct agent:

```python
from src.knowledge_graph.agri_kg_tool import AgriKGTool

# Initialize tool
kg_tool = AgriKGTool()

# Query
result = kg_tool.run(query="What diseases affect rice?")
print(result['formatted_result'])
```

## Sample Cypher Queries

### Get diseases for a crop
```cypher
MATCH (c:Crop {name: 'rice'})-[r:AFFECTED_BY_DISEASE]->(d:Disease)
RETURN d.name as disease, r.severity as severity, r.symptoms as symptoms
ORDER BY r.severity DESC
```

### Get pests for a crop
```cypher
MATCH (c:Crop {name: 'wheat'})-[r:AFFECTED_BY_PEST]->(p:Pest)
RETURN p.name as pest, p.type as pest_type, r.damage_level as damage
ORDER BY r.damage_level DESC
```

### Get fertilizers for a crop
```cypher
MATCH (c:Crop {name: 'maize'})-[r:REQUIRES_FERTILIZER]->(f:Fertilizer)
RETURN f.name as fertilizer, f.type as type, f.npk_ratio as npk, 
       r.stage as application_stage, r.quantity as quantity
ORDER BY r.stage
```

### Get ideal soil for a crop
```cypher
MATCH (c:Crop {name: 'rice'})-[r:GROWS_IN_SOIL]->(s:Soil)
WHERE r.suitability = 'high' OR r.suitability = 'ideal'
RETURN s.type as soil_type, s.ph_range as ph, s.texture as texture,
       r.yield_impact as impact
ORDER BY r.suitability DESC
```

### Get complete crop information
```cypher
MATCH (c:Crop {name: 'rice'})
OPTIONAL MATCH (c)-[rd:AFFECTED_BY_DISEASE]->(d:Disease)
OPTIONAL MATCH (c)-[rp:AFFECTED_BY_PEST]->(p:Pest)
OPTIONAL MATCH (c)-[rf:REQUIRES_FERTILIZER]->(f:Fertilizer)
OPTIONAL MATCH (c)-[rs:GROWS_IN_SOIL]->(s:Soil)
RETURN c, 
       collect(DISTINCT {disease: d.name, severity: rd.severity}) as diseases,
       collect(DISTINCT {pest: p.name, damage: rp.damage_level}) as pests,
       collect(DISTINCT {fertilizer: f.name, stage: rf.stage}) as fertilizers,
       collect(DISTINCT {soil: s.type, suitability: rs.suitability}) as soils
```

## Integration with ShizishanGPT

### Add to Tool Registry

Edit `src/orchestration/tool_registry.py`:

```python
from src.knowledge_graph.agri_kg_tool import AgriKGTool

# In initialize() method:
self._register_tool(
    name="agri_kg_query",
    tool=AgriKGTool(),
    description="Query Agriculture Knowledge Graph for structured relationships",
    category="knowledge",
    input_type="text",
    keywords=["disease", "pest", "fertilizer", "soil", "crop", "relationship", "affect"]
)
```

### Add to API Router

Edit `src/backend/main.py`:

```python
from src.backend.routers.router_kg import router as kg_router

# Add router
app.include_router(kg_router)
```

### Update ReAct Agent Priority

Edit `src/orchestration/react_agent.py` - add priority:

```
**PRIORITY 3: Knowledge Graph (Structured Relationships)**

Use agri_kg_query when the query asks about relationships:
   - "What diseases affect [crop]?" → agri_kg_query
   - "Which pests attack [crop]?" → agri_kg_query
   - "What fertilizers does [crop] need?" → agri_kg_query
   - "What is the ideal soil for [crop]?" → agri_kg_query
   
AgriKG provides instant, structured answers for relationship queries.
```

## Troubleshooting

### Neo4j Connection Failed
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Verify credentials in .env file
```

### No Triples Extracted
```bash
# Check data directory
ls Data/AgriKF_Data/

# Verify .docx files exist
# Check extractor.py patterns match your document format
```

### Empty Query Results
```bash
# Verify graph has data
# Open Neo4j Browser: http://localhost:7474
# Run: MATCH (n) RETURN count(n)
# Should return > 0
```

## Performance Tips

1. **Indexes**: Automatically created by builder for fast lookups
2. **Batch Queries**: Use UNWIND for multiple items
3. **Connection Pooling**: Reuse `AgriKGQueryEngine` instance
4. **Caching**: Cache common query results in Redis

## Next Steps

1. **Enrich Data**: Add more Word documents to `Data/AgriKF_Data/`
2. **Custom Queries**: Create domain-specific Cypher queries
3. **UI Integration**: Add KG query interface to frontend
4. **Export**: Export subgraphs for offline use
5. **Analytics**: Add graph analytics (PageRank, communities)

## Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [py2neo Documentation](https://py2neo.org/)
