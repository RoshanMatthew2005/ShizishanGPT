# Milestone 4 - Mini LangChain + ReAct Agent

## Overview
Complete custom implementation of an orchestration system with ReAct (Reasoning + Acting) pattern for agricultural AI, built **without using the LangChain library**.

## Architecture

### 🏗️ Directory Structure
```
src/
├── model_tools/           # Tool wrappers for models
│   ├── yield_tool.py     # Crop yield prediction
│   ├── pest_tool.py      # Pest/disease detection
│   ├── weather_tool.py   # Weather analysis
│   └── translation_tool.py # Language translation
│
├── orchestration/         # Core orchestration system
│   ├── tool_registry.py  # Tool management
│   ├── tool_router.py    # Intelligent routing
│   ├── rag_engine.py     # RAG retrieval engine
│   ├── llm_engine.py     # LLM generation engine
│   ├── mini_langchain.py # Custom pipeline system
│   ├── react_agent.py    # ReAct reasoning agent
│   ├── prompt_templates.py # Prompt templates
│   ├── history_manager.py  # Conversation history
│   └── main_orchestrator.py # Main entry point
│
└── database/
    └── mongo_logger.py    # MongoDB logging
```

## Components

### 1. Model Tools
Each tool follows a standard interface:
- `run(**kwargs) → Dict[str, Any]`
- `validate_input()` for input validation
- Standardized error handling
- Consistent response format

**Available Tools:**
- ✅ **YieldTool**: Predicts crop yield from RandomForest model
- ✅ **PestTool**: Detects diseases from ResNet18 image classifier
- ✅ **WeatherTool**: Weather analysis (with fallback knowledge-based advice)
- ✅ **TranslationTool**: Multi-language translation support

### 2. Engines

#### RAG Engine (`rag_engine.py`)
- Loads ChromaDB vectorstore (23,083 vectors)
- Uses sentence-transformers for embeddings
- Retrieves top-k relevant documents
- Returns context with relevance scores

#### LLM Engine (`llm_engine.py`)
- Wraps fine-tuned DistilGPT-2 model
- Anti-repetition controls built-in
- Q&A and text generation modes
- GPU/CPU support

### 3. Tool Registry (`tool_registry.py`)
Central registry managing all tools:
```python
from orchestration.tool_registry import get_registry

registry = get_registry()
tool = registry.get_tool("yield_prediction")
metadata = registry.get_metadata("rag_retrieval")
all_tools = registry.list_tools(category="prediction")
```

### 4. Tool Router (`tool_router.py`)
Intelligent query routing based on:
- Pattern matching (regex)
- Keyword detection
- Query length analysis
- Confidence scoring
- Priority-based selection

**Example:**
```python
from orchestration.tool_router import ToolRouter

router = ToolRouter()
result = router.route("What fertilizers for rice?")
# → {selected_tool: "rag_retrieval", confidence: 0.85}
```

### 5. Mini LangChain (`mini_langchain.py`)
Custom pipeline implementation **without LangChain**:

```python
from orchestration.mini_langchain import Pipeline

pipeline = Pipeline("Custom Pipeline")
pipeline.add_step("step1", function1, "Description")
pipeline.add_step("step2", function2, "Description")

result = pipeline.execute({"input": "data"})
```

**Features:**
- Chainable operations
- Automatic result passing
- Error handling with partial results
- Execution time tracking
- Built-in RAG pipeline builder

### 6. ReAct Agent (`react_agent.py`)
Implements Thought → Action → Observation loop:

```python
from orchestration.react_agent import ReActAgent

agent = ReActAgent(max_iterations=5, verbose=True)
result = agent.run("Complex agricultural query")
```

**Flow:**
1. **Thought**: Reason about what to do
2. **Action**: Select and execute tool
3. **Observation**: Process tool result
4. **Repeat**: Until answer found or max iterations

**Features:**
- Automatic tool routing
- Multi-step reasoning
- Conversation history tracking
- Detailed execution logs

### 7. Supporting Modules

#### Prompt Templates (`prompt_templates.py`)
Reusable templates for different scenarios:
- ReAct prompts
- RAG context prompts
- Q&A templates
- Translation templates

#### History Manager (`history_manager.py`)
In-memory conversation tracking:
- Stores user queries and responses
- Metadata tracking (tools used, execution time)
- Context summarization
- Session statistics

### 8. MongoDB Logger (`mongo_logger.py`)
Persistent conversation logging:
- Logs queries and responses
- Optional metadata storage
- Search and retrieval
- Fallback to console if MongoDB unavailable

### 9. Main Orchestrator (`main_orchestrator.py`)
Central integration point:

```python
from orchestration.main_orchestrator import ShizishanGPTOrchestrator

orchestrator = ShizishanGPTOrchestrator(
    enable_mongo=True,
    verbose=True
)

result = orchestrator.query("Your question here", mode="auto")
```

**Processing Modes:**
- `auto`: Automatic tool selection (default)
- `react`: Force ReAct reasoning loop
- `direct`: Direct tool execution (no reasoning)
- `pipeline`: Use predefined RAG pipeline

## Usage

### 1. Interactive CLI Mode

```bash
python src/orchestration/main_orchestrator.py
```

**Commands:**
- `/history` - Show conversation history
- `/stats` - System statistics
- `/tools` - List available tools
- `/clear` - Clear history
- `quit` or `exit` - Exit

### 2. Single Query Mode

```bash
python src/orchestration/main_orchestrator.py "What fertilizers for rice?"
```

With options:
```bash
python src/orchestration/main_orchestrator.py \
    "Your question" \
    --mode react \
    --verbose \
    --mongo
```

### 3. Batch Processing

Create `queries.json`:
```json
[
    "What is the best fertilizer for maize?",
    "How to control pests in tomatoes?",
    "What weather conditions are ideal for wheat?"
]
```

Run batch:
```bash
python src/orchestration/main_orchestrator.py --batch queries.json
```

### 4. Programmatic Usage

```python
from orchestration.main_orchestrator import ShizishanGPTOrchestrator

# Initialize
orch = ShizishanGPTOrchestrator(verbose=True)

# Single query
result = orch.query("What are NPK ratios?")
print(result['final_answer'])

# Batch processing
queries = ["Query 1", "Query 2", "Query 3"]
results = orch.batch_process(queries)

# Cleanup
orch.shutdown()
```

## Testing

Run comprehensive test suite:

```bash
python test_milestone4.py
```

**Tests:**
1. Individual Tools - Verify each tool works independently
2. Tool Router - Test routing logic and confidence scoring
3. Pipeline System - Validate chainable operations
4. History Manager - Check conversation tracking
5. ReAct Agent - Test multi-step reasoning
6. Main Orchestrator - Integration testing

## Example Workflows

### Workflow 1: Simple Q&A
```
User: "What is nitrogen fertilizer?"
Router: → llm_generation (confidence: 80%)
LLM: Generates short explanation
Result: Direct answer in ~2s
```

### Workflow 2: Knowledge Retrieval
```
User: "What are best practices for rice cultivation?"
Router: → rag_retrieval (confidence: 85%)
RAG: Retrieves 3 relevant documents from 23K chunks
Result: Context-based answer with sources
```

### Workflow 3: Multi-Step Reasoning
```
User: "How should I prepare my field for wheat planting?"
Agent: ReAct loop
  Iteration 1:
    Thought: Need agricultural guidance
    Action: rag_retrieval
    Observation: Retrieved field preparation docs
  Iteration 2:
    Thought: Synthesize comprehensive answer
    Action: llm_generation (with RAG context)
    Observation: Generated detailed steps
Result: Multi-source comprehensive answer
```

### Workflow 4: Translation Pipeline
```
User: "Translate rice farming guide to Hindi"
Pipeline:
  Step 1: RAG retrieval → Get rice farming content
  Step 2: Translation → Translate to Hindi
Result: Translated agricultural content
```

## Configuration

### Environment Variables
Create `.env` file:
```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=shizishanGPT
MAX_ITERATIONS=5
VERBOSE=True
```

### Dependencies
Install required packages:
```bash
pip install torch transformers
pip install chromadb sentence-transformers
pip install pymongo  # Optional, for MongoDB logging
pip install googletrans==4.0.0-rc1  # Optional, for translation
```

## Performance

**Benchmarks (approximate):**
- RAG retrieval: 0.5-1.5s
- LLM generation: 1-3s
- Tool router: <0.1s
- ReAct agent (2 iterations): 2-5s
- Full pipeline: 3-7s

**Model Sizes:**
- Mini LLM: 328 MB (DistilGPT-2)
- Yield model: 41 MB (RandomForest)
- Pest model: ~100 MB (ResNet18)
- Embedding model: 90 MB (MiniLM)
- Vectorstore: ~200 MB (23K vectors)

## Key Features

✅ **No LangChain Dependency** - Fully custom implementation  
✅ **ReAct Reasoning** - Thought-Action-Observation loop  
✅ **Intelligent Routing** - Automatic tool selection  
✅ **Multi-Model Support** - RAG, LLM, Prediction, Translation  
✅ **Conversation History** - In-memory session tracking  
✅ **MongoDB Logging** - Optional persistent storage  
✅ **Pipeline Chaining** - Composable operations  
✅ **Error Handling** - Graceful degradation and fallbacks  
✅ **CLI Interface** - Interactive and batch modes  
✅ **Comprehensive Testing** - Full test suite included  

## Troubleshooting

**Issue: Models not found**
```
Solution: Train models first:
- python train_mini_llm.py
- python src/train_yield_model.py
- python src/train_pest_model.py
```

**Issue: ChromaDB not found**
```
Solution: Build knowledge base:
python src/build_knowledge_base.py
```

**Issue: MongoDB connection failed**
```
Solution: Either install MongoDB or run without --mongo flag
Fallback: System automatically uses console logging
```

**Issue: Translation fails**
```
Solution: Install googletrans:
pip install googletrans==4.0.0-rc1
Fallback: Returns original text with warning
```

## Next Steps

- [ ] Train weather LSTM model (`python src/train_weather_model.py`)
- [ ] Add more sophisticated prompt engineering
- [ ] Implement caching for expensive operations
- [ ] Add user authentication and sessions
- [ ] Create web API (FastAPI)
- [ ] Build frontend dashboard
- [ ] Add more agricultural domain tools
- [ ] Implement feedback loop for model improvement

## Files Created

**Model Tools (4 files):**
- `src/model_tools/yield_tool.py` - 286 lines
- `src/model_tools/pest_tool.py` - 243 lines
- `src/model_tools/weather_tool.py` - 216 lines
- `src/model_tools/translation_tool.py` - 221 lines

**Orchestration (8 files):**
- `src/orchestration/rag_engine.py` - 209 lines
- `src/orchestration/llm_engine.py` - 229 lines
- `src/orchestration/tool_registry.py` - 192 lines
- `src/orchestration/tool_router.py` - 279 lines
- `src/orchestration/mini_langchain.py` - 262 lines
- `src/orchestration/prompt_templates.py` - 102 lines
- `src/orchestration/history_manager.py` - 188 lines
- `src/orchestration/react_agent.py` - 371 lines
- `src/orchestration/main_orchestrator.py` - 379 lines

**Database (1 file):**
- `src/database/mongo_logger.py` - 211 lines

**Testing (1 file):**
- `test_milestone4.py` - 298 lines

**Total:** 14 files, ~3,686 lines of code

---

**Milestone 4 Status:** ✅ **COMPLETE**

All components implemented and ready for testing!
