# Tavily Integration - Quick Reference

## 🚀 Setup (3 Steps)

1. **Get API Key**: https://tavily.com → Sign up → Copy API key
2. **Configure**: Create `.env` file: `TAVILY_API_KEY=tvly-xxxxxxxxxx`
3. **Test**: `python test_tavily_quick.py`

## 📡 API Endpoints

### Regular Search
```bash
POST http://localhost:8000/api/tavily_search
```
```json
{
  "query": "best pesticide for whitefly in cotton 2025",
  "search_depth": "basic",
  "max_results": 5
}
```

### Agricultural Search (Auto-optimized)
```bash
POST http://localhost:8000/api/tavily_search/agricultural
```
```json
{
  "query": "latest fertilizer subsidy India",
  "max_results": 5
}
```

## 🤖 When Agent Uses Tavily

✅ **Triggers Tavily Search:**
- Queries with: "latest", "current", "new", "2024", "2025"
- Product/chemical names, brands
- "where to buy", "price", "availability"
- Government schemes, subsidies
- Disease outbreaks, alerts
- Market information

❌ **Uses RAG Instead:**
- General practices, techniques
- Soil science, plant biology
- Historical data
- Textbook knowledge

## 💬 Example Queries

```python
# Tavily queries (real-time info)
"What's the latest fertilizer subsidy in India?"
"Best treatment for rust disease in wheat 2025"
"Where can I buy neem oil in Maharashtra?"
"Current urea prices"
"Imidacloprid dosage for aphids"

# RAG queries (established knowledge)
"What is nitrogen fixation?"
"Cotton cultivation practices"
"Explain photosynthesis"
```

## 🧪 Testing

```bash
# Quick check
python test_tavily_quick.py

# Full test suite
python test_tavily_integration.py

# Manual test with curl
curl -X POST http://localhost:8000/api/tavily_search \
  -H "Content-Type: application/json" \
  -d '{"query":"organic farming","max_results":3}'
```

## 📊 Cost

- **Free**: 1000 searches/month
- **Paid**: $0.001 per search
- **Example**: 10,000 searches = $10

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "API key not configured" | Add `TAVILY_API_KEY` to `.env` |
| Backend not responding | Start: `uvicorn src.backend.main:app --port 8000` |
| Middleware not responding | Start: `cd middleware && npm start` |
| Slow responses | Use `search_depth: "basic"` |

## 📂 Key Files

```
src/backend/
  ├── services/tavily_service.py       # Core search logic
  ├── routers/router_tavily.py         # API endpoints
  └── models/schemas.py                # Request/response models

middleware/
  ├── controllers/tavilyController.js  # Request handling
  └── routes/tavilyRouter.js          # Route definitions

src/orchestration/
  └── prompt_templates.py              # Agent tool selection rules
```

## 🎯 Response Format

```json
{
  "success": true,
  "query": "your search query",
  "results": [
    {
      "title": "Page title",
      "content": "AI-extracted relevant content...",
      "url": "https://source.com",
      "score": 0.95,
      "published_date": "2025-01-15"
    }
  ],
  "answer": "AI-generated summary answer",
  "response_time": 1.2,
  "results_count": 5
}
```

## 🌟 Why Tavily?

- ✅ **AI-optimized**: Clean, structured output for LLMs
- ✅ **Agriculture-friendly**: Great for niche domains
- ✅ **Cost-effective**: $0.001/search vs $0.005 for Google
- ✅ **Fast**: 1-2 seconds avg response
- ✅ **No parsing**: Ready-to-use content

## 📖 Full Documentation

See `TAVILY_INTEGRATION_COMPLETE.md` for complete guide.

---

**Integration Status**: ✅ Complete and Ready to Use!
