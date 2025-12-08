from src.orchestration.react_agent import ReActAgent

agent = ReActAgent(verbose=False)
result = agent.run('Predict yield for wheat in Punjab with 800mm rainfall')
print(f'\n✅ Final Answer:\n{result["final_answer"]}')
print(f'\n📊 Details:')
print(f'  - Tools used: {", ".join(result["tools_used"])}')
print(f'  - Iterations: {result["total_iterations"]}')
print(f'  - Time: {result["execution_time"]:.2f}s')
