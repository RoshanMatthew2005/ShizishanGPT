# ShizishanGPT - Tavily Search Integration

## 📋 Quick Setup Guide

### 1. Get Your Tavily API Key

1. Visit https://tavily.com
2. Sign up for a free account
3. Get your API key from the dashboard
4. **Free tier**: 1000 searches/month
5. **Paid tier**: $0.001 per search (very affordable!)

### 2. Configure Environment

Add to your `.env` file:
```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Install Dependencies

```bash
pip install tavily-python==0.3.0
```

### 4. Test the Integration

#### Test Backend Directly:
```bash
# Make sure backend is running
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000

# In another terminal, test:
python test_tavily_integration.py
```

#### Test Through Middleware:
```bash
# Terminal 1: Start backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start middleware
cd middleware
npm start

# Terminal 3: Run tests
python test_tavily_integration.py
```

## 🔍 Available Endpoints

### 1. Regular Search
**POST** `/api/tavily_search`

```json
{
  "query": "best pesticide for whitefly in cotton India 2025",
  "search_depth": "basic",
  "max_results": 5,
  "include_domains": []
}
```

### 2. Agricultural-Optimized Search
**POST** `/api/tavily_search/agricultural`

Automatically prioritizes trusted agricultural domains:
- agritech.tnau.ac.in
- icar.org.in
- farmer.gov.in
- agricoop.nic.in
- fao.org

```json
{
  "query": "latest fertilizer subsidy scheme India",
  "max_results": 5
}
```

## 📊 Response Format

```json
{
  "success": true,
  "query": "best pesticide for whitefly in cotton",
  "results": [
    {
      "title": "Effective Whitefly Control in Cotton",
      "content": "Imidacloprid at 0.3ml/L is recommended for whitefly control...",
      "url": "https://example.com/article",
      "score": 0.95,
      "published_date": "2025-01-15"
    }
  ],
  "answer": "For whitefly control in cotton, neonicotinoids like imidacloprid...",
  "response_time": 1.23,
  "results_count": 5
}
```

## 🤖 Agent Integration

The ReAct agent (Gemma 2 9B) now automatically uses Tavily for:

✅ **Real-time queries:**
- "What's the latest fertilizer subsidy scheme?"
- "Best treatment for rust disease in wheat 2025"
- "Where to buy neem oil in Maharashtra"
- "Current urea prices in India"

✅ **Tool chaining:**
```
User: "How to treat aphids in tomato?"
→ Agent calls tavily_search("aphid treatment tomato 2025")
→ Gets latest products/chemicals
→ Agent calls query_rag("aphid application methods")
→ Gets application techniques
→ Combines both for complete answer
```

## 🧪 Test Queries

10 production-ready test cases in `test_tavily_integration.py`:

1. Pest Management: "best pesticide for whitefly in cotton crops India 2025"
2. Government Schemes: "latest fertilizer subsidy scheme for farmers India 2025"
3. Disease Treatment: "how to treat rust disease in wheat organic methods"
4. Product Availability: "where to buy neem oil pesticide near me Maharashtra"
5. Research: "latest research on biopesticides for tomato cultivation"
6. Chemical Info: "imidacloprid dosage for aphid control in potato"
7. Fertilizer: "NPK fertilizer ratio for rice paddy pre-monsoon application"
8. Market Data: "current urea fertilizer prices in India December 2025"
9. Alerts: "fall armyworm outbreak alert India 2025"
10. IPM: "integrated pest management protocol for brinjal fruit borer"

## 💡 Usage Tips

### When to Use Tavily:
- ANY query about current/latest information
- Product names, brands, chemicals
- Government policies, schemes
- Market prices, availability
- Disease outbreaks, alerts
- Recent research, news

### When to Use RAG Instead:
- General agricultural practices
- Soil science fundamentals
- Crop biology, plant physiology
- Historical data
- Textbook knowledge

### Best Practices:
1. **Be specific in queries**: "imidacloprid dosage for aphids" > "pest control"
2. **Include year for time-sensitive queries**: "...India 2025"
3. **Use agricultural endpoint** for domain-specific searches
4. **Cite sources** in final answers (Tavily provides URLs)

## 🚀 Performance

- **Basic search**: ~1-2 seconds
- **Advanced search**: ~3-4 seconds
- **Results quality**: AI-extracted, ready for LLM consumption
- **No HTML parsing needed**: Clean, structured data

## 📈 Cost Analysis

Free tier: **1000 searches/month FREE**

Paid usage examples:
- 10,000 searches = $10
- 100,000 searches = $100

**For agricultural use**: Extremely affordable compared to alternatives:
- Google Search API: $5/1000 queries
- SerpAPI: $50/month base

## 🔗 Integration Flow

```
User Query
    ↓
React Frontend
    ↓
Node.js Middleware (:5000)
  POST /api/tavily_search
    ↓
FastAPI Backend (:8000)
  /api/tavily_search
    ↓
Tavily Service
  tavily_service.search()
    ↓
Tavily API
    ↓
AI-Extracted Results
    ↓
← Response back through chain
```

## ✅ Files Created/Modified

**Backend:**
- ✅ `src/backend/services/tavily_service.py` (NEW)
- ✅ `src/backend/routers/router_tavily.py` (NEW)
- ✅ `src/backend/models/schemas.py` (NEW)
- ✅ `src/backend/main.py` (UPDATED - router registered)
- ✅ `src/orchestration/prompt_templates.py` (UPDATED - ReAct prompt)

**Middleware:**
- ✅ `middleware/controllers/tavilyController.js` (NEW)
- ✅ `middleware/routes/tavilyRouter.js` (NEW)
- ✅ `middleware/services/apiClient.js` (UPDATED - Tavily methods)
- ✅ `middleware/server.js` (UPDATED - router registered)

**Configuration:**
- ✅ `requirements.txt` (UPDATED - tavily-python added)
- ✅ `.env.example` (UPDATED - TAVILY_API_KEY placeholder)

**Testing:**
- ✅ `test_tavily_integration.py` (NEW - comprehensive test suite)

## 🎯 Next Steps

1. **Get API Key**: Sign up at https://tavily.com
2. **Add to .env**: `TAVILY_API_KEY=tvly-xxx...`
3. **Test Backend**: `python test_tavily_integration.py`
4. **Test Agent**: Try queries with real-time info needs
5. **Monitor Usage**: Check dashboard at https://tavily.com/dashboard

## 🆘 Troubleshooting

**Error: "Tavily API key not configured"**
- Solution: Add `TAVILY_API_KEY` to your `.env` file

**Error: "Failed to send telemetry event"**
- Ignore: This is a harmless ChromaDB warning, doesn't affect Tavily

**Slow responses:**
- Use `search_depth: "basic"` for faster results (default)
- Reduce `max_results` to 3-5

**No results:**
- Make query more specific
- Try agricultural endpoint for domain searches
- Check API key is valid

---

**Integration Complete!** 🎉

Tavily is now fully integrated into ShizishanGPT. Your agent can now access real-time web information for the most up-to-date agricultural advice.
