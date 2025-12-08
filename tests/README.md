# ShizishanGPT Test Suite

Comprehensive automated testing for the Agricultural AI Assistant.

## 📦 Test Files

| File | Tests | Description |
|------|-------|-------------|
| `test_e2e.py` | 10 | End-to-end pipeline: React → Node → FastAPI → MongoDB |
| `test_rag.py` | 23 | RAG retrieval accuracy and performance |
| `test_llm.py` | 25 | Mini LLM generation quality and coherence |
| `test_models.py` | 30 | Yield and Weather model predictions |
| `test_performance.py` | 15 | Latency, load, throughput, resource usage |
| `test_security.py` | 20 | Security vulnerabilities and protections |
| `test_errors.py` | 30 | Error handling and recovery |

**Total: 153 automated tests**

## 🚀 Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install pytest requests psutil

# Ensure all services are running:
# - MongoDB (port 27017)
# - FastAPI backend (port 8000)
# - Node.js middleware (port 5000)
# - React frontend (port 3000)
```

### Run All Tests

```bash
# From project root
cd tests
pytest -v
```

### Run Specific Test Category

```bash
# E2E tests only
pytest test_e2e.py -v

# RAG tests only
pytest test_rag.py -v

# LLM tests only
pytest test_llm.py -v

# Models tests only
pytest test_models.py -v

# Performance tests
pytest test_performance.py -v

# Security tests
pytest test_security.py -v

# Error handling tests
pytest test_errors.py -v
```

### Run by Marker

```bash
# Critical tests only
pytest -m critical -v

# Skip slow tests
pytest -m "not slow" -v

# Performance tests only
pytest -m performance -v

# Security tests only
pytest -m security -v
```

## 📊 Test Coverage

### Functional Testing
- ✅ All API endpoints
- ✅ All AI models (LLM, RAG, Yield, Weather)
- ✅ User workflows
- ✅ Error scenarios
- ✅ Data persistence (MongoDB)

### Non-Functional Testing
- ✅ Performance benchmarks
- ✅ Security vulnerabilities
- ✅ Load handling
- ✅ Error recovery
- ✅ Resource usage

### Integration Testing
- ✅ Frontend ↔ Middleware
- ✅ Middleware ↔ Backend
- ✅ Backend ↔ MongoDB
- ✅ Backend ↔ AI Models

## 📈 Performance Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| LLM Response | < 5s | < 10s |
| RAG Retrieval | < 2s | < 4s |
| Model Inference | < 1s | < 2s |
| Health Check | < 0.1s | < 0.5s |
| Concurrent Users (10) | 100% | > 70% |

## 🔒 Security Testing

- API key exposure checks
- CORS configuration validation
- SQL/NoSQL injection prevention
- XSS attack prevention
- Command injection blocking
- Input validation
- File upload security

## 🎯 Success Criteria

**Required for Production:**
- [ ] 95%+ tests passing
- [ ] All critical tests passing
- [ ] Performance within targets
- [ ] No critical security issues
- [ ] All services operational

## 📝 Test Results

After running tests, generate a report:

```bash
# HTML report
pytest --html=report.html --self-contained-html

# Coverage report
pytest --cov=../src --cov-report=html
```

## 🐛 Reporting Issues

If tests fail:
1. Check that all services are running
2. Verify environment configuration
3. Review error messages
4. Check logs in backend/middleware
5. Use bug report template in `docs/testing/MILESTONE_8_TESTING_PLAN_PART7.md`

## 🔧 Troubleshooting

### Services Not Running
```bash
# Check health endpoints
curl http://localhost:3000
curl http://localhost:5000/health
curl http://localhost:8000/health
```

### Tests Timing Out
- Increase timeout values in test files
- Check system resources
- Verify models are loaded

### Import Errors
```bash
pip install -r ../requirements.txt
```

## 📚 Documentation

For detailed test documentation, see:
- [Testing Plan Overview](../docs/testing/README.md)
- [Quick Reference Guide](../docs/testing/QUICK_REFERENCE.md)
- [Complete Test Plans](../docs/testing/)

## ⚡ Quick Commands

```bash
# Run fast tests only
pytest -m "not slow" -v

# Run critical path tests
pytest -m critical -v

# Run with verbose output
pytest -vv

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific test
pytest test_e2e.py::TestE2EPipeline::test_e2e_001_services_health -v
```

## 🎓 Best Practices

1. **Run tests frequently** during development
2. **Fix failures immediately** to avoid accumulation
3. **Review performance metrics** regularly
4. **Update tests** when features change
5. **Document new tests** with clear descriptions

## 📞 Support

For questions or issues:
- Review test documentation
- Check service logs
- Verify environment setup
- Consult troubleshooting guide

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Test Suite for ShizishanGPT Agricultural AI Assistant**
