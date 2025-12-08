"""
Test ReAct Agent with Improved Yield Prediction
"""
from src.orchestration.react_agent import ReActAgent

def test_react_yield():
    print("\n" + "="*70)
    print("TESTING REACT AGENT WITH IMPROVED YIELD PREDICTION")
    print("="*70)
    
    agent = ReActAgent(max_iterations=3, verbose=True)
    
    # Test query
    query = "Predict yield for wheat in Punjab with 800mm rainfall"
    
    print(f"\n📝 Query: {query}")
    print("="*70)
    
    result = agent.run(query)
    
    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(f"Query: {result['query']}")
    print(f"\nAnswer: {result['final_answer']}")
    print(f"\nTools Used: {', '.join(result['tools_used'])}")
    print(f"Iterations: {result['total_iterations']}")
    print(f"Time: {result['execution_time']:.2f}s")
    print("="*70)

if __name__ == "__main__":
    test_react_yield()
