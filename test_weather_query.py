"""Quick test of weather tool with location extraction"""
from src.orchestration.react_agent import ReActAgent

agent = ReActAgent(verbose=False)
result = agent.run('What is the weather in Punjab?')

print("="*70)
print("WEATHER QUERY TEST: Punjab")
print("="*70)
print("\nFinal Answer:")
print(result['final_answer'][:500])
print("\n" + "="*70)
print("Tools Used:", result['tools_used'])
print("="*70)
