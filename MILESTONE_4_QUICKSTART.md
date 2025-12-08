# Milestone 4 - Quick Start Guide

## 🚀 Quick Start

### Prerequisites
Ensure you have completed previous milestones:
- ✅ Milestone 1: Environment setup
- ✅ Milestone 2: RAG knowledge base built
- ✅ Milestone 3: Mini LLM trained
- ✅ Yield and Pest models trained

### Installation
All dependencies should already be installed from previous milestones. Optional:
```bash
# For MongoDB logging (optional)
pip install pymongo

# For translation (optional)
pip install googletrans==4.0.0-rc1
```

## 🎯 Usage

### 1. Interactive Mode (Recommended for First Try)

```bash
python src/orchestration/main_orchestrator.py
```

**Try these queries:**
```
🌾 You: What are the best fertilizers for rice cultivation?
🌾 You: How to control pests in tomatoes?
🌾 You: What is nitrogen fertilizer?
```

**Commands:**
- `/history` - View conversation history
- `/stats` - Show system statistics
- `/tools` - List all available tools
- `/clear` - Clear conversation history
- `quit` or `exit` - Exit interactive mode

### 2. Single Query Mode

```bash
python src/orchestration/main_orchestrator.py "What fertilizers should I use for maize?"
```

With verbose output:
```bash
python src/orchestration/main_orchestrator.py "Your question here" --verbose
```

### 3. Test the System

```bash
python test_milestone4.py
```

Expected output:
```
Total Tests: 6
✅ Passed: 6
❌ Failed: 0
Success Rate: 100.0%
```

## 📋 Available Tools

The system has 6 integrated tools:

1. **yield_prediction** - Predicts crop yield based on parameters
2. **pest_detection** - Identifies plant diseases from images
3. **weather_prediction** - Weather analysis and advice
4. **translation** - Multi-language translation
5. **rag_retrieval** - Retrieves knowledge from 23K document chunks
6. **llm_generation** - Generates text using fine-tuned GPT-2

## 🔄 Processing Modes

### Auto Mode (Default)
```python
result = orchestrator.query("Your question", mode="auto")
```
Automatically selects the best tool and reasoning strategy.

### ReAct Mode
```python
result = orchestrator.query("Your question", mode="react")
```
Forces multi-step reasoning loop (Thought → Action → Observation).

### Direct Mode
```python
result = orchestrator.query("Your question", mode="direct")
```
Directly executes the selected tool without reasoning.

### Pipeline Mode
```python
result = orchestrator.query("Your question", mode="pipeline")
```
Uses predefined RAG pipeline (Retrieve → Generate).

## 🧪 Example Workflows

### Simple Question
```
Query: "What is nitrogen fertilizer?"
→ Auto-routes to llm_generation
→ Generates concise answer
→ Response in ~1-2s
```

### Knowledge Retrieval
```
Query: "What are best practices for rice cultivation?"
→ Auto-routes to rag_retrieval
→ Searches 23,083 document chunks
→ Returns relevant context
→ Response in ~0.5-1.5s
```

### Multi-Step Reasoning
```
Query: "How should I prepare my field for wheat?"
→ ReAct agent activates
→ Iteration 1: Retrieves preparation guidelines (RAG)
→ Iteration 2: Synthesizes comprehensive answer (LLM + RAG context)
→ Response in ~3-5s
```

## 📊 System Architecture

```
User Query
    ↓
Tool Router (selects best tool based on query analysis)
    ↓
┌───────────────────────────────────────┐
│ Direct Execution  │  ReAct Agent      │
│ (High confidence) │  (Complex query)  │
└───────────────────────────────────────┘
    ↓                       ↓
Tool Execution      Thought → Action → Observation Loop
    ↓                       ↓
Response            Multi-step Response
    ↓                       ↓
History Logging + Optional MongoDB Storage
```

## 🔧 Programmatic Usage

```python
from orchestration.main_orchestrator import ShizishanGPTOrchestrator

# Initialize
orch = ShizishanGPTOrchestrator(
    enable_mongo=False,  # Set True if MongoDB running
    verbose=True         # Show detailed logs
)

# Single query
result = orch.query("What are NPK ratios for corn?")
print(result['final_answer'])
print(f"Tools used: {result['tools_used']}")
print(f"Time: {result['execution_time']:.2f}s")

# Batch processing
queries = [
    "Best fertilizer for wheat?",
    "How to control aphids?",
    "Ideal rainfall for rice?"
]
results = orch.batch_process(queries)

# Access conversation history
print(orch.history.format_history(n=5))

# Cleanup
orch.shutdown()
```

## 🐛 Troubleshooting

### Issue: "Model not found"
```bash
# Train the models:
python train_mini_llm.py
python src/train_yield_model.py
python src/train_pest_model.py
```

### Issue: "Vectorstore not found"
```bash
# Build knowledge base:
python src/build_knowledge_base.py
```

### Issue: Translation not working
```bash
# Install optional dependency:
pip install googletrans==4.0.0-rc1
# Or use without translation - system gracefully degrades
```

### Issue: MongoDB connection failed
```
# Either:
1. Install and start MongoDB
2. Or run without --mongo flag (uses console logging instead)
```

## 📈 Performance Tips

1. **First query is slower** - Models load on first use (~5-10s), subsequent queries are fast
2. **Use direct mode for simple queries** - Skips reasoning overhead
3. **RAG is fastest for factual queries** - No generation needed, just retrieval
4. **GPU speeds up LLM** - 2-3x faster if CUDA available

## 🎓 Example Session

```
$ python src/orchestration/main_orchestrator.py

======================================================================
SHIZISHANGPT - INTERACTIVE MODE
======================================================================
Ask agricultural questions. Type 'quit', 'exit', or 'q' to exit.
Commands:
  /history - Show conversation history
  /stats - Show system statistics
  /tools - List available tools
  /clear - Clear history
======================================================================

🌾 You: What is the recommended NPK ratio for maize?

ℹ️ ======================================================================
ℹ️ REACT AGENT STARTED
ℹ️ Query: What is the recommended NPK ratio for maize?
ℹ️ ======================================================================

⚡ Selected Tool: rag_retrieval
ℹ️ Confidence: 85%

🤖 ShizishanGPT: The recommended NPK ratio for maize is typically 4:2:1, 
which means 4 parts nitrogen, 2 parts phosphorus, and 1 part potassium. 
For optimal growth, apply 100-125 kg nitrogen per hectare...

   📊 Tools used: rag_retrieval
   ⏱️ Time: 1.23s

🌾 You: /stats

======================================================================
SYSTEM STATISTICS
======================================================================

Conversation:
  Total turns: 1
  Session duration: 12.5s

Tools:
  Total tools: 6
  Prediction: 3
  Knowledge: 1
  Generation: 1
  Utility: 1
======================================================================

🌾 You: quit

👋 Goodbye!
```

## 📝 What's Next?

Now that Milestone 4 is complete, you can:

1. **Explore the system** - Try different types of queries
2. **Train weather model** - `python src/train_weather_model.py`
3. **Add MongoDB** - For persistent conversation logging
4. **Build a web API** - Create FastAPI endpoints
5. **Develop frontend** - React/Vue dashboard for farmers
6. **Fine-tune models** - Improve with more agricultural data

## 🎉 Success Criteria

✅ All 6 tools registered and working  
✅ Tool router selects appropriate tools  
✅ ReAct agent performs multi-step reasoning  
✅ Pipeline system chains operations  
✅ History manager tracks conversations  
✅ MongoDB logger (optional) persists data  
✅ CLI interface is interactive and responsive  
✅ Test suite passes 100% (6/6 tests)  

**Milestone 4 is complete!** 🚀

---

For detailed documentation, see: `docs/MILESTONE_4_COMPLETE.md`  
For issues, check the Troubleshooting section above.
