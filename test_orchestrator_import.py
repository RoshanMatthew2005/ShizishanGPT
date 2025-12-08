"""Test orchestrator import"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    from src.orchestration.main_orchestrator import ShizishanGPTOrchestrator
    print("✅ Import successful!")
    
    # Try to create orchestrator
    orch = ShizishanGPTOrchestrator(verbose=False)
    print("✅ Orchestrator created successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
