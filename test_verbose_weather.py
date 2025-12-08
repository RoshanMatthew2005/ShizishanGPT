"""Test with verbose output"""
from src.orchestration.react_agent import ReActAgent

agent = ReActAgent(verbose=True)
result = agent.run('What is the weather in Punjab?')

print("\n" + "="*70)
print("RESULT")
print("="*70)
print(result['final_answer'][:300])
print("\nTools:", result['tools_used'])
