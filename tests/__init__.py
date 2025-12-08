"""
ShizishanGPT Test Suite
Comprehensive testing for the Agricultural AI Assistant
"""

__version__ = "1.0.0"
__author__ = "ShizishanGPT Development Team"

# Test categories
TEST_CATEGORIES = [
    "e2e",          # End-to-end integration tests
    "rag",          # RAG retrieval tests
    "llm",          # Mini LLM quality tests
    "models",       # Yield and Weather model tests
    "performance",  # Performance and load tests
    "security",     # Security vulnerability tests
    "errors",       # Error handling tests
]

# Test markers for selective execution
MARKERS = {
    "critical": "Critical path tests that must pass",
    "slow": "Tests that take longer to execute",
    "requires_services": "Tests requiring all services to be running"
}
