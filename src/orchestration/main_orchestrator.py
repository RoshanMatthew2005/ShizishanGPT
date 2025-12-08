"""
Main Orchestrator
Entry point that integrates all components of the Mini LangChain + ReAct Agent system.
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.orchestration.react_agent import ReActAgent
from src.orchestration.tool_registry import get_registry
from src.orchestration.tool_router import ToolRouter
from src.orchestration.mini_langchain import Pipeline, PipelineBuilder
from src.orchestration.history_manager import HistoryManager
from src.database.mongo_logger import MongoLogger


class ShizishanGPTOrchestrator:
    """Main orchestrator for the ShizishanGPT agricultural AI system."""
    
    def __init__(self, 
                 enable_logging: bool = True,
                 enable_mongo: bool = False,
                 verbose: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            enable_logging: Enable console logging
            enable_mongo: Enable MongoDB logging
            verbose: Verbose agent output
        """
        self.enable_logging = enable_logging
        self.enable_mongo = enable_mongo
        self.verbose = verbose
        
        # Initialize components
        print("\n" + "="*70)
        print("INITIALIZING SHIZISHANGPT ORCHESTRATOR")
        print("="*70)
        
        self.registry = get_registry()
        self.router = ToolRouter()
        self.agent = ReActAgent(max_iterations=5, verbose=verbose)
        self.history = HistoryManager(max_history=20)
        
        # Optional MongoDB logger
        self.logger = None
        if enable_mongo:
            self.logger = MongoLogger()
            self.logger.connect()
        
        print("✓ Orchestrator initialized")
        print("="*70 + "\n")
    
    def query(self, user_query: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Process a user query using the appropriate mode.
        
        Args:
            user_query: User's question or request
            mode: Processing mode:
                - "auto": Automatic tool selection (default)
                - "react": Force ReAct agent
                - "direct": Direct tool execution (no reasoning)
                - "pipeline": Use predefined pipeline
            
        Returns:
            Dictionary with response and metadata
        """
        if not user_query or not user_query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty"
            }
        
        print(f"\n{'='*70}")
        print(f"PROCESSING QUERY")
        print(f"{'='*70}")
        print(f"Mode: {mode}")
        print(f"Query: {user_query}")
        print(f"{'='*70}\n")
        
        result = None
        
        try:
            if mode == "react":
                # Use ReAct agent
                result = self.agent.run(user_query)
                
            elif mode == "direct":
                # Direct tool execution with router
                routing = self.router.route(user_query)
                if routing["success"]:
                    tool_name = routing["selected_tool"]
                    tool = self.registry.get_tool(tool_name)
                    
                    if tool_name == "rag_retrieval":
                        tool_result = tool.query(user_query)
                    elif tool_name == "llm_generation":
                        tool_result = tool.generate(user_query)
                    else:
                        tool_result = {"success": False, "error": "Direct mode only supports RAG and LLM"}
                    
                    result = {
                        "success": tool_result.get("success", False),
                        "query": user_query,
                        "final_answer": tool_result.get("context", tool_result.get("generated_text", "")),
                        "mode": "direct",
                        "tool_used": tool_name
                    }
            
            elif mode == "pipeline":
                # Use predefined RAG pipeline
                pipeline = PipelineBuilder.create_rag_pipeline()
                pipeline_result = pipeline.execute({"query": user_query})
                
                if pipeline_result["success"]:
                    final = pipeline_result["final_result"]
                    result = {
                        "success": True,
                        "query": user_query,
                        "final_answer": final.get("generated_text", ""),
                        "mode": "pipeline",
                        "pipeline_steps": len(pipeline.steps)
                    }
                else:
                    result = pipeline_result
            
            else:  # mode == "auto"
                # Let agent decide
                result = self.agent.run(user_query)
            
            # Log to history
            if result and result.get("success"):
                self.history.add_turn(
                    user_query,
                    result.get("final_answer", ""),
                    metadata=result
                )
                
                # Log to MongoDB if enabled
                if self.logger:
                    self.logger.log_query(
                        user_query,
                        result.get("final_answer", ""),
                        metadata={
                            "mode": mode,
                            "tools_used": result.get("tools_used", []),
                            "execution_time": result.get("execution_time")
                        }
                    )
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Query processing failed: {str(e)}",
                "query": user_query
            }
            print(f"\n❌ Error: {e}\n")
            return error_result
    
    def interactive_mode(self):
        """Run interactive chat mode."""
        print("\n" + "="*70)
        print("SHIZISHANGPT - INTERACTIVE MODE")
        print("="*70)
        print("Ask agricultural questions. Type 'quit', 'exit', or 'q' to exit.")
        print("Commands:")
        print("  /history - Show conversation history")
        print("  /stats - Show system statistics")
        print("  /tools - List available tools")
        print("  /clear - Clear history")
        print("="*70 + "\n")
        
        while True:
            try:
                user_input = input("\n🌾 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                # Handle special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Process query
                result = self.query(user_input, mode="auto")
                
                if result.get("success"):
                    answer = result.get("final_answer", "No answer generated")
                    print(f"\n🤖 ShizishanGPT: {answer}")
                    
                    if self.verbose and "tools_used" in result:
                        print(f"\n   📊 Tools used: {', '.join(result['tools_used'])}")
                        if "execution_time" in result:
                            print(f"   ⏱️ Time: {result['execution_time']:.2f}s")
                else:
                    print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _handle_command(self, command: str):
        """
        Handle special commands in interactive mode.
        
        Args:
            command: Command string
        """
        cmd = command.lower().strip()
        
        if cmd == '/history':
            print("\n" + "="*70)
            print("CONVERSATION HISTORY")
            print("="*70)
            print(self.history.format_history(n=5))
            print("="*70)
        
        elif cmd == '/stats':
            print("\n" + "="*70)
            print("SYSTEM STATISTICS")
            print("="*70)
            
            # History stats
            hist_stats = self.history.get_stats()
            print(f"\nConversation:")
            print(f"  Total turns: {hist_stats['total_turns']}")
            print(f"  Session duration: {hist_stats['session_duration_seconds']:.1f}s")
            
            # Tool registry stats
            print(f"\nTools:")
            print(f"  Total tools: {len(self.registry.list_tools())}")
            for category in ["prediction", "knowledge", "generation", "utility"]:
                tools = self.registry.list_tools(category=category)
                if tools:
                    print(f"  {category.capitalize()}: {len(tools)}")
            
            # MongoDB stats
            if self.logger:
                mongo_stats = self.logger.get_stats()
                print(f"\nDatabase:")
                print(f"  Connected: {mongo_stats.get('connected', False)}")
                print(f"  Total logs: {mongo_stats.get('total_logs', 0)}")
            
            print("="*70)
        
        elif cmd == '/tools':
            print("\n" + "="*70)
            print("AVAILABLE TOOLS")
            print("="*70)
            for tool_name in self.registry.list_tools():
                metadata = self.registry.get_metadata(tool_name)
                print(f"\n• {tool_name}")
                print(f"  {metadata['description']}")
                print(f"  Category: {metadata['category']}")
            print("="*70)
        
        elif cmd == '/clear':
            self.history.clear()
            print("\n✓ History cleared")
        
        else:
            print(f"\n❌ Unknown command: {command}")
            print("Available commands: /history, /stats, /tools, /clear")
    
    def batch_process(self, queries: list) -> list:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of query strings
            
        Returns:
            List of results
        """
        results = []
        
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING {len(queries)} QUERIES")
        print(f"{'='*70}\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Processing: {query[:60]}...")
            result = self.query(query, mode="auto")
            results.append(result)
        
        print(f"\n{'='*70}")
        print(f"BATCH COMPLETE: {sum(1 for r in results if r.get('success'))} / {len(queries)} successful")
        print(f"{'='*70}\n")
        
        return results
    
    def shutdown(self):
        """Shutdown the orchestrator and cleanup resources."""
        print("\n" + "="*70)
        print("SHUTTING DOWN ORCHESTRATOR")
        print("="*70)
        
        if self.logger:
            self.logger.close()
        
        print("✓ Shutdown complete")
        print("="*70 + "\n")


# CLI Entry Point
def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ShizishanGPT Agricultural AI System")
    parser.add_argument("query", nargs="*", help="Query to process (omit for interactive mode)")
    parser.add_argument("--mode", choices=["auto", "react", "direct", "pipeline"], 
                       default="auto", help="Processing mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--mongo", action="store_true", help="Enable MongoDB logging")
    parser.add_argument("--batch", type=str, help="Path to JSON file with batch queries")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = ShizishanGPTOrchestrator(
        enable_mongo=args.mongo,
        verbose=args.verbose
    )
    
    try:
        if args.batch:
            # Batch processing
            with open(args.batch, 'r') as f:
                queries = json.load(f)
            orchestrator.batch_process(queries)
        
        elif args.query:
            # Single query
            query = " ".join(args.query)
            result = orchestrator.query(query, mode=args.mode)
            
            if result.get("success"):
                print(f"\n{'='*70}")
                print("ANSWER")
                print(f"{'='*70}")
                print(result.get("final_answer", ""))
                print(f"{'='*70}\n")
            else:
                print(f"\n❌ Error: {result.get('error')}\n")
        
        else:
            # Interactive mode
            orchestrator.interactive_mode()
    
    finally:
        orchestrator.shutdown()


if __name__ == "__main__":
    main()
