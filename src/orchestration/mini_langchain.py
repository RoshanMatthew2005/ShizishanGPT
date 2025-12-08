"""
Mini LangChain Pipeline
Custom implementation of chainable operations without using LangChain library.
"""
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import json


class PipelineStep:
    """Represents a single step in a pipeline."""
    
    def __init__(self, 
                 name: str, 
                 function: Callable, 
                 description: str = ""):
        """
        Initialize a pipeline step.
        
        Args:
            name: Step name
            function: Function to execute (must accept **kwargs and return dict)
            description: Step description
        """
        self.name = name
        self.function = function
        self.description = description
        self.execution_time = None
        self.result = None
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the step.
        
        Args:
            **kwargs: Input parameters
            
        Returns:
            Step result dictionary
        """
        start_time = datetime.now()
        try:
            self.result = self.function(**kwargs)
            self.execution_time = (datetime.now() - start_time).total_seconds()
            return self.result
        except Exception as e:
            self.execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "success": False,
                "error": f"Step '{self.name}' failed: {str(e)}"
            }
    
    def __repr__(self) -> str:
        return f"<PipelineStep: {self.name}>"


class Pipeline:
    """Custom pipeline for chaining operations."""
    
    def __init__(self, name: str = "Pipeline"):
        """
        Initialize a pipeline.
        
        Args:
            name: Pipeline name
        """
        self.name = name
        self.steps: List[PipelineStep] = []
        self.results: List[Dict[str, Any]] = []
        self.total_execution_time = 0
        
    def add_step(self, 
                 name: str, 
                 function: Callable, 
                 description: str = "") -> 'Pipeline':
        """
        Add a step to the pipeline.
        
        Args:
            name: Step name
            function: Function to execute
            description: Step description
            
        Returns:
            Self for chaining
        """
        step = PipelineStep(name, function, description)
        self.steps.append(step)
        return self
    
    def execute(self, initial_input: Dict[str, Any] = None, 
                pass_results: bool = True) -> Dict[str, Any]:
        """
        Execute the entire pipeline.
        
        Args:
            initial_input: Initial input dictionary
            pass_results: Whether to pass previous step results to next step
            
        Returns:
            Dictionary with pipeline results
        """
        if initial_input is None:
            initial_input = {}
        
        self.results = []
        total_start = datetime.now()
        current_input = initial_input.copy()
        
        print(f"\n{'='*70}")
        print(f"EXECUTING PIPELINE: {self.name}")
        print(f"{'='*70}\n")
        
        for i, step in enumerate(self.steps, 1):
            print(f"Step {i}/{len(self.steps)}: {step.name}")
            if step.description:
                print(f"  → {step.description}")
            
            # Execute step
            result = step.execute(**current_input)
            self.results.append(result)
            
            print(f"  ✓ Completed in {step.execution_time:.2f}s")
            
            # Check if step failed
            if not result.get("success", True):
                print(f"  ❌ Step failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "pipeline": self.name,
                    "failed_at_step": i,
                    "step_name": step.name,
                    "error": result.get("error"),
                    "partial_results": self.results
                }
            
            # Pass results to next step if enabled
            if pass_results:
                current_input.update(result)
            
            print()
        
        self.total_execution_time = (datetime.now() - total_start).total_seconds()
        
        print(f"{'='*70}")
        print(f"PIPELINE COMPLETED")
        print(f"Total time: {self.total_execution_time:.2f}s")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "pipeline": self.name,
            "total_steps": len(self.steps),
            "total_execution_time": self.total_execution_time,
            "results": self.results,
            "final_result": self.results[-1] if self.results else None
        }
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all step results.
        
        Returns:
            List of result dictionaries
        """
        return self.results
    
    def get_step_result(self, step_name: str) -> Optional[Dict[str, Any]]:
        """
        Get result of a specific step by name.
        
        Args:
            step_name: Name of the step
            
        Returns:
            Result dictionary or None
        """
        for step, result in zip(self.steps, self.results):
            if step.name == step_name:
                return result
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pipeline to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "steps": [
                {
                    "name": step.name,
                    "description": step.description,
                    "execution_time": step.execution_time
                }
                for step in self.steps
            ],
            "total_execution_time": self.total_execution_time,
            "results": self.results
        }
    
    def __repr__(self) -> str:
        return f"<Pipeline: {self.name} ({len(self.steps)} steps)>"


class PipelineBuilder:
    """Builder for creating common pipeline patterns."""
    
    @staticmethod
    def create_rag_pipeline() -> Pipeline:
        """
        Create a RAG (Retrieve-Augment-Generate) pipeline.
        
        Returns:
            Configured pipeline
        """
        from orchestration.rag_engine import RAGEngine
        from orchestration.llm_engine import LLMEngine
        
        pipeline = Pipeline("RAG Pipeline")
        
        rag = RAGEngine()
        llm = LLMEngine()
        
        def retrieve_step(query: str, **kwargs):
            return rag.query(query, top_k=3)
        
        def generate_step(query: str, context: str = "", **kwargs):
            prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
            return llm.generate(prompt, max_length=200)
        
        pipeline.add_step(
            "retrieve",
            retrieve_step,
            "Retrieve relevant documents from knowledge base"
        )
        
        pipeline.add_step(
            "generate",
            generate_step,
            "Generate answer using LLM with retrieved context"
        )
        
        return pipeline
    
    @staticmethod
    def create_translation_pipeline() -> Pipeline:
        """
        Create a translation pipeline (retrieve, translate, respond).
        
        Returns:
            Configured pipeline
        """
        from model_tools.translation_tool import TranslationTool
        from orchestration.rag_engine import RAGEngine
        
        pipeline = Pipeline("Translation Pipeline")
        
        rag = RAGEngine()
        translator = TranslationTool()
        
        def retrieve_step(query: str, **kwargs):
            return rag.query(query, top_k=2)
        
        def translate_step(context: str, target_lang: str = "hi", **kwargs):
            return translator.run(context[:500], target_lang)  # Translate first 500 chars
        
        pipeline.add_step("retrieve", retrieve_step, "Retrieve information")
        pipeline.add_step("translate", translate_step, "Translate to target language")
        
        return pipeline


# Example usage
if __name__ == "__main__":
    # Test 1: Simple custom pipeline
    print("TEST 1: Custom Pipeline")
    
    def step1(value: int = 0, **kwargs):
        return {"success": True, "value": value + 10}
    
    def step2(value: int = 0, **kwargs):
        return {"success": True, "value": value * 2}
    
    def step3(value: int = 0, **kwargs):
        return {"success": True, "value": value - 5, "final": True}
    
    pipeline = Pipeline("Math Pipeline")
    pipeline.add_step("add_10", step1, "Add 10 to value")
    pipeline.add_step("multiply_2", step2, "Multiply by 2")
    pipeline.add_step("subtract_5", step3, "Subtract 5")
    
    result = pipeline.execute({"value": 5})
    print(f"\nFinal result: {result['final_result']}")
    
    # Test 2: RAG Pipeline
    print("\n\nTEST 2: RAG Pipeline")
    
    try:
        rag_pipeline = PipelineBuilder.create_rag_pipeline()
        print(f"Created {rag_pipeline}")
        print(f"Steps: {[step.name for step in rag_pipeline.steps]}")
    except Exception as e:
        print(f"Note: RAG pipeline requires models to be loaded: {e}")
