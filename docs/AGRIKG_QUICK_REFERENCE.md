# AgriKG Quick Reference

## Installation & Setup

### 1. Install Dependencies
```bash
pip install py2neo spacy python-docx
python -m spacy download en_core_web_sm
```

### 2. Install Neo4j (Docker)
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 3. Configure .env
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 4. Build Knowledge Graph
```bash
python build_agri_kg.py
```

### 5. Test Queries
```bash
python test_agri_kg.py
```

## Quick Usage Examples

### Python API
```python
from src.knowledge_graph.query_engine import AgriKGQueryEngine

engine = AgriKGQueryEngine()
engine.load()

# Get diseases
result = engine.get_diseases_for_crop("rice")

# Natural language
result = engine.natural_language_query("What pests attack wheat?")

# Custom Cypher
result = engine.execute_cypher(
    "MATCH (c:Crop {name: $name})-[:AFFECTED_BY_DISEASE]->(d) RETURN d.name",
    {"name": "rice"}
)
```

### HTTP API
```bash
# Health check
curl http://localhost:8000/api/kg/health

# Natural language query
curl -X POST http://localhost:8000/api/kg/query/natural \
  -H "Content-Type: application/json" \
  -d '{"query": "What diseases affect rice?"}'

# Get crop diseases
curl -X POST http://localhost:8000/api/kg/crop/diseases \
  -H "Content-Type: application/json" \
  -d '{"crop_name": "rice"}'
```

### ReAct Agent Integration
```python
from src.knowledge_graph.agri_kg_tool import AgriKGTool

tool = AgriKGTool()
result = tool.run(query="What diseases affect rice?")
print(result['formatted_result'])
```

## Common Cypher Queries

### Diseases for Crop
```cypher
MATCH (c:Crop {name: 'rice'})-[:AFFECTED_BY_DISEASE]->(d:Disease)
RETURN d.name, d.symptoms
```

### Pests for Crop
```cypher
MATCH (c:Crop {name: 'wheat'})-[:AFFECTED_BY_PEST]->(p:Pest)
RETURN p.name, p.type
```

### Fertilizers for Crop
```cypher
MATCH (c:Crop {name: 'maize'})-[r:REQUIRES_FERTILIZER]->(f:Fertilizer)
RETURN f.name, r.stage, r.quantity
```

### Ideal Soil
```cypher
MATCH (c:Crop {name: 'rice'})-[r:GROWS_IN_SOIL]->(s:Soil)
WHERE r.suitability = 'high'
RETURN s.type, s.texture, s.ph_range
```

### Treatment for Disease
```cypher
MATCH (d:Disease {name: 'blight'})-[:TREATED_BY]->(t:Treatment)
RETURN t.name, t.method, t.dosage
```

## File Structure
```
src/knowledge_graph/
├── __init__.py              # Module init
├── ontology.py              # Schema definition
├── extractor.py             # Triple extraction from docs
├── builder.py               # Neo4j graph builder
├── query_engine.py          # Query interface
└── agri_kg_tool.py          # ReAct agent tool wrapper

src/backend/routers/
└── router_kg.py             # FastAPI endpoints

build_agri_kg.py             # Main build script
test_agri_kg.py              # Test script
docs/AGRIKG_SETUP_GUIDE.md   # Detailed guide
```

## Troubleshooting

### Neo4j not connecting
```bash
# Check if running
docker ps | grep neo4j

# Start if stopped
docker start neo4j

# View logs
docker logs neo4j
```

### No data extracted
```bash
# Check documents exist
ls Data/AgriKF_Data/*.docx

# Rebuild with verbose output
python build_agri_kg.py
```

### Query returns empty
```bash
# Verify data in Neo4j Browser
# Visit: http://localhost:7474
# Run: MATCH (n) RETURN count(n)
```

## Integration Checklist

- [x] Extract triples from Word docs
- [x] Build Neo4j knowledge graph
- [x] Create query engine
- [x] Add FastAPI endpoints
- [x] Create ReAct agent tool
- [ ] Add to tool registry
- [ ] Update ReAct agent priorities
- [ ] Test end-to-end integration
- [ ] Add to frontend UI

## Quick Commands

```bash
# Build KG
python build_agri_kg.py

# Test queries
python test_agri_kg.py

# Start Neo4j Browser
open http://localhost:7474

# Check API health
curl http://localhost:8000/api/kg/health

# Get stats
curl http://localhost:8000/api/kg/stats
```
