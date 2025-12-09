"""
ReAct Agent
Implements the Reasoning + Acting (ReAct) pattern for agricultural AI using Gemma 2.
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.orchestration.tool_registry import get_registry
from src.orchestration.tool_router import ToolRouter
from src.orchestration.history_manager import HistoryManager
from src.orchestration.llm_engine import LLMEngine


class ReActAgent:
    """ReAct (Reasoning + Acting) Agent for multi-step problem solving using Gemma 2."""
    
    def __init__(self, max_iterations: int = 5, verbose: bool = True):
        """
        Initialize the ReAct Agent.
        
        Args:
            max_iterations: Maximum reasoning iterations (default: 5)
            verbose: Whether to print detailed execution logs
        """
        self.registry = get_registry()
        self.router = ToolRouter()
        self.history = HistoryManager()
        self.llm = LLMEngine()  # Initialize Gemma 2 LLM engine
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # ReAct prompt template
        self.react_prompt = """You are the ShizishanGPT Orchestration LLM.
You must act as a ReAct-style intelligent controller that decides which TOOL to use.

Your job is:
1. Understand the user question.
2. Decide which TOOL is required.
3. Call the correct TOOL using the exact JSON format.
4. After receiving the tool output, generate a final, clean answer.

You MUST obey the following rules:

------------------ TOOL SELECTION RULES ------------------

**PRIORITY 1: Tavily Search (Real-Time Web Information)**

ALWAYS use tavily_search when the query contains ANY of these:
   - Product names: "pesticide", "fungicide", "insecticide", "herbicide", "fertilizer", "chemical"
   - Recommendations: "best", "recommended", "top", "which", "what to use", "suggest"
   - Current info: "2025", "2024", "latest", "current", "new", "recent", "now"
   - Availability: "where to buy", "available", "purchase", "market", "suppliers"
   - Pricing: "cost", "price", "rate"
   - Schemes: "subsidy", "scheme", "government", "policy"
   - Brands: ANY brand/company name
   - Treatment: "how to treat", "cure", "control", "manage" + disease/pest name
   
   Examples that MUST use tavily_search:
   - "What is the best pesticide for whitefly in cotton in 2025?" → tavily_search
   - "Where can I buy neem oil?" → tavily_search
   - "Latest fertilizer subsidy scheme" → tavily_search
   - "How to treat rust disease in wheat?" → tavily_search
   - "Recommended fungicide for tomato blight" → tavily_search

**PRIORITY 2: Yield Prediction Tool**

If the question contains rainfall, crop yield, production, state, irrigation + numbers → call yield_prediction.

**PRIORITY 3: Pest Detection Tool**

If the question describes crop symptoms, diseases, pests, insects, leaf color 
changes, or damage → call pest_detection.

**PRIORITY 4: Weather Realtime Tool**

If the question asks about current weather, today's temperature, rainfall today,
weather forecast, soil moisture, humidity, wind speed, or "what is the weather" 
→ call weather_realtime.

For weather impact questions (will weather affect crops?):
   a. First call weather_realtime to get current/forecast data
   b. Then call weather_prediction to analyze agricultural impacts
   c. Finally call llm_generation to synthesize the answer

**PRIORITY 5: Weather Prediction Tool**

If the question asks about weather impacts on crops, drought risks, flood risks,
or agricultural weather patterns → call weather_prediction.

**PRIORITY 6: RAG Retrieval Tool (Static Knowledge)**

ONLY use rag_retrieval for general concepts, basic biology, historical facts:
   - "What is photosynthesis?"
   - "Explain nitrogen cycle"
   - "Wheat growth stages"
   - "What are aphids?" (NOT treatment - use tavily_search for treatment)

**PRIORITY 7: LLM Generation Tool**

If the user asks for summaries, rewriting, simple explanations, or general wording → call llm_generation.

**PRIORITY 8: Translation**

If the user asks in any non-English language (Tamil, Hindi, Telugu, etc.):
   a. First call translation
   b. Then run tool selection again on the translated text
   c. After generating final answer, call translation back to user language

**CRITICAL RULE:**
If you see BOTH real-time keywords AND static knowledge needs:
1. CALL tavily_search FIRST (get current products/treatments)
2. THEN call rag_retrieval if needed (get application methods/background)
3. COMBINE both in final answer with source citations

------------------------------------------------------------

------------------ TOOL CALL FORMAT ------------------------

Always call tools using this exact format:

<tool_call name="TOOL_NAME">
{{"key": "value", "key2": "value2"}}
</tool_call>

Important:
- Never add extra text inside the tool_call block.
- Never add explanations near the JSON.
- Never produce more than one tool call at a time.

------------------------------------------------------------

------------------ AFTER TOOL RESPONSE ---------------------

After you receive the tool's JSON output:
- DO NOT repeat the JSON to the user.
- DO NOT reveal internal reasoning.
- DO NOT mention tools or backend.
- Produce a clean, final user-friendly answer.

------------------------------------------------------------

------------------ HARD RULES (MUST FOLLOW) -----------------

- You are NOT allowed to refuse yield predictions. The yield_prediction tool handles it.
- You are NOT allowed to say "I am a language model".
- You are NOT allowed to generate predictions yourself—only tools predict.
- You MUST call a tool whenever the rules require it.
- If you are unsure, prefer calling a tool instead of answering directly.

------------------------------------------------------------

Your final answer to the user must be friendly, agricultural, and simplified.

Begin your reasoning.
Do not show thoughts to the user.

User Query: {query}

Available Tools: {tools}

{context}"""
        
        # Track agent state
        self.current_iteration = 0
        self.thoughts = []
        self.actions = []
        self.observations = []
        
    def reset_state(self) -> None:
        """Reset agent state for new query."""
        self.current_iteration = 0
        self.thoughts.clear()
        self.actions.clear()
        self.observations.clear()
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message if verbose mode is enabled.
        
        Args:
            message: Message to log
            level: Log level (INFO, THOUGHT, ACTION, OBSERVATION)
        """
        if self.verbose:
            prefix = {
                "INFO": "ℹ️",
                "THOUGHT": "💭",
                "ACTION": "⚡",
                "OBSERVATION": "👁️",
                "SUCCESS": "✅",
                "ERROR": "❌"
            }.get(level, "•")
            
            print(f"{prefix} {message}")
    
    def _format_tools_description(self) -> str:
        """
        Format available tools for prompt.
        
        Returns:
            Formatted tools description
        """
        tools_desc = []
        for tool_name in self.registry.list_tools():
            metadata = self.registry.get_metadata(tool_name)
            tools_desc.append(f"- {tool_name}: {metadata['description']}")
        
        return "\n".join(tools_desc)
    
    def _reason_with_gemma(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Use Gemma 2 to reason about the query and decide on actions.
        
        Args:
            query: User query
            context: Additional context (e.g., previous tool results)
            
        Returns:
            Dictionary with reasoning result
        """
        try:
            # If we have Tavily results in context, use LLM to synthesize
            if "Tavily search results:" in context:
                self._log(f"📝 Tavily results available, routing to LLM for synthesis", "INFO")
                return {
                    "success": True,
                    "selected_tool": "llm_generation",
                    "reasoning": "Synthesizing Tavily search results",
                    "model": "router"
                }
            
            # ALWAYS use router for reliable tool selection
            # Router has better pattern matching than LLM reasoning
            routing = self.router.route(query)
            
            if routing.get("success"):
                selected_tool = routing.get("selected_tool", "llm_generation")
                confidence = routing.get("confidence", 0)
                
                self._log(f"🎯 Router selected: {selected_tool} (confidence: {confidence:.2f})", "INFO")
                
                return {
                    "success": True,
                    "selected_tool": selected_tool,
                    "reasoning": f"Router confidence: {confidence:.2f}",
                    "model": "router"
                }
            else:
                # Fallback to LLM reasoning only if router fails
                tools_desc = self._format_tools_description()
                
                reasoning_prompt = f"""You are ShizishanGPT's reasoning engine. Analyze this agricultural query and decide which tool to use.

Available Tools:
{tools_desc}

Query: {query}
{context}

Based on the query, which single tool should be used first? Respond with just the tool name (e.g., "rag_retrieval", "yield_prediction", etc.).

Tool choice:"""
                
                # Get reasoning from Gemma 2
                llm_result = self.llm.generate(
                    reasoning_prompt,
                    temperature=0.3,
                    max_tokens=50
                )
                
                if llm_result["success"]:
                    generated_text = llm_result["generated_text"].strip().lower()
                    
                    # Extract tool name
                    available_tools = self.registry.list_tools()
                    selected_tool = None
                    
                    for tool in available_tools:
                        if tool in generated_text:
                            selected_tool = tool
                            break
                    
                    if not selected_tool:
                        selected_tool = "llm_generation"
                    
                    return {
                        "success": True,
                        "selected_tool": selected_tool,
                        "reasoning": generated_text,
                        "model": llm_result.get("model", "gemma2")
                    }
                else:
                    return {
                        "success": False,
                        "error": "Both router and LLM reasoning failed"
                    }
                
        except Exception as e:
            # Fallback to router
            routing = self.router.route(query)
            return {
                "success": True,
                "selected_tool": routing.get("selected_tool", "llm_generation"),
                "reasoning": f"Fallback due to error: {str(e)}",
                "model": "router"
            }
    
    def _parse_action(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse action and action input from text.
        
        Args:
            text: Text to parse
            
        Returns:
            (action_name, action_input) or (None, None) if parsing fails
        """
        # Look for Action: and Action Input: patterns
        action_match = re.search(r'Action:\s*(\w+)', text, re.IGNORECASE)
        input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', text, re.IGNORECASE | re.DOTALL)
        
        if action_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return action, action_input
        
        return None, None
    
    def _extract_final_answer(self, text: str) -> Optional[str]:
        """
        Extract final answer from text.
        
        Args:
            text: Text to parse
            
        Returns:
            Final answer or None
        """
        match = re.search(r'Final Answer:\s*(.+)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _execute_tool(self, tool_name: str, tool_input: Any) -> Dict[str, Any]:
        """
        Execute a tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            
        Returns:
            Tool execution result
        """
        try:
            tool = self.registry.get_tool(tool_name)
            
            if not tool:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            # Parse input if it's a string (might be JSON or plain text)
            if isinstance(tool_input, str):
                # Try to parse as JSON
                try:
                    parsed_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    # Use as-is for text-based tools
                    parsed_input = {"query": tool_input} if tool_name in ["rag_retrieval", "llm_generation"] else {"text": tool_input}
            else:
                parsed_input = tool_input
            
            # Execute based on tool type
            if tool_name == "rag_retrieval":
                result = tool.query(parsed_input.get("query", ""))
            elif tool_name == "llm_generation":
                # If we have previous observations (e.g., from Tavily or RAG), include them as context
                query_text = parsed_input.get("query", "")
                if self.observations:
                    # Add context from previous tool results
                    context_text = "\n\n".join(self.observations[-2:])  # Last 2 observations
                    
                    # Check if context is from RAG or Tavily
                    if "Context:" in context_text or "retrieved documents" in context_text.lower():
                        # RAG context - emphasize using the knowledge base information
                        enhanced_query = f"""Based on the following agricultural knowledge from our database, provide a comprehensive answer to the user's question.

Knowledge Base Information:
{context_text}

User's question: {query_text}

Instructions:
- Use the specific information from the knowledge base above
- Provide a clear, detailed answer based on the retrieved context
- If the context contains specific techniques, methods, or recommendations, include them
- Organize the information in a helpful way for farmers
- Be practical and actionable
- If the knowledge base doesn't fully answer the question, acknowledge what information is available

Answer:"""
                    else:
                        # Tavily or other context
                        enhanced_query = f"""Based on the following information, provide a comprehensive answer to the user's question.

Information available:
{context_text}

User's question: {query_text}

Instructions:
- Use the specific information provided above (product names, recommendations, sources)
- Provide a clear, direct answer
- Include specific product names, dosages, or recommendations when available
- Cite sources when mentioned in the information
- Be helpful and specific, not generic

Answer:"""
                    result = tool.generate(enhanced_query)
                else:
                    result = tool.generate(query_text)
            elif tool_name == "translation":
                result = tool.run(
                    parsed_input.get("text", ""),
                    parsed_input.get("target_lang", "en")
                )
            elif tool_name == "weather_realtime":
                # weather_realtime is a function, not a class
                # Import geocoding utilities
                import sys
                from pathlib import Path
                project_root = Path(__file__).resolve().parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                    
                from src.backend.utils.geocoding import is_valid_location, search_location
                
                # Extract location from query - improved regex
                query_text = parsed_input.get("query", tool_input if isinstance(tool_input, str) else "")
                
                self._log(f"🔍 Query text for location extraction: '{query_text}'", "INFO")
                
                # Try multiple patterns to find location
                location = None
                patterns = [
                    r'weather\s+(?:in|at|for)\s+([A-Za-z\s]+?)(?:\s+(?:today|this week|forecast|now|\d+\s*days?)|[?,.]|$)',
                    r'(?:in|at|for)\s+([A-Za-z\s]+?)(?:\s+(?:weather|today|this week|forecast|\d+\s*days?)|[?,.]|$)',
                    r'([A-Za-z\s]+?)(?:\s+weather|\s+today)',
                ]
                
                for pattern in patterns:
                    location_match = re.search(pattern, query_text, re.IGNORECASE)
                    if location_match:
                        location = location_match.group(1).strip()
                        # Validate it's a known location
                        if is_valid_location(location):
                            self._log(f"📍 Extracted location: {location}", "INFO")
                            break
                        # Try searching for similar
                        matches = search_location(location)
                        if matches:
                            location = matches[0]
                            self._log(f"📍 Found similar location: {location}", "INFO")
                            break
                
                # Fallback to Maharashtra if no location found
                if not location:
                    location = "Maharashtra"
                    self._log(f"📍 No location found, using fallback: {location}", "INFO")
                
                # Extract days
                days_match = re.search(r'(\d+)\s*days?', query_text, re.IGNORECASE)
                days = int(days_match.group(1)) if days_match else 7
                days = min(max(days, 1), 16)  # Clamp between 1 and 16
                
                self._log(f"🌤️  Calling weather tool: location={location}, days={days}", "INFO")
                
                # Call the function
                weather_result = tool(location, days)
                result = {
                    "success": True,
                    "result": weather_result,
                    "location": location,
                    "days": days
                }
            elif tool_name == "yield_prediction":
                # Pass the original query for intelligent parsing
                query_text = parsed_input.get("query", tool_input if isinstance(tool_input, str) else "")
                result = tool.run(query=query_text, **parsed_input if isinstance(parsed_input, dict) else {})
            elif tool_name == "pest_detection":
                # Pass the original query for image detection/sample selection
                query_text = parsed_input.get("query", tool_input if isinstance(tool_input, str) else "")
                image_path = parsed_input.get("image_path", "") if isinstance(parsed_input, dict) else ""
                result = tool.run(query=query_text, image_path=image_path)
            elif tool_name == "tavily_search":
                # Extract query from parsed input
                query_text = parsed_input.get("query", tool_input if isinstance(tool_input, str) else "")
                max_results = parsed_input.get("max_results", 5) if isinstance(parsed_input, dict) else 5
                search_depth = parsed_input.get("search_depth", "basic") if isinstance(parsed_input, dict) else "basic"
                result = tool.search(query_text, max_results, search_depth)
            elif isinstance(parsed_input, dict):
                result = tool.run(**parsed_input)
            else:
                result = tool.run(parsed_input)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the ReAct agent on a query using Gemma 2 for reasoning.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Dictionary with agent response and reasoning trace
        """
        self.reset_state()
        start_time = datetime.now()
        
        self._log("="*70, "INFO")
        self._log(f"REACT AGENT STARTED", "INFO")
        self._log(f"Query: {query}", "INFO")
        self._log("="*70, "INFO")
        
        # Get available tools description
        tools_desc = self._format_tools_description()
        
        # Build context from previous interactions if available
        conversation_context = ""
        if self.observations:
            conversation_context = f"\nPrevious observations: {self.observations[-1][:200]}..."
        
        reasoning_steps = []
        tools_used = set()
        final_answer = None
        
        # ReAct loop using Gemma 2 for reasoning
        for iteration in range(1, self.max_iterations + 1):
            try:
                self.current_iteration = iteration
                
                self._log(f"\n--- Iteration {iteration} ---", "INFO")
                
                # Create ReAct prompt for Gemma 2
                react_prompt = self.react_prompt.format(
                    query=query,
                    tools=tools_desc,
                    context=conversation_context
                )
                
                # Use Gemma 2 for reasoning about tool selection
                reasoning_result = self._reason_with_gemma(query, conversation_context)
                
                tool_to_use = reasoning_result.get("selected_tool", "llm_generation")
                reasoning_text = reasoning_result.get("reasoning", "")
                model_used = reasoning_result.get("model", "unknown")
                
                self._log(f"💭 Thought: I should use {tool_to_use} to address this query", "THOUGHT")
                self._log(f"⚡ Selected Tool: {tool_to_use}", "ACTION")
                self._log(f"ℹ️ Model: {model_used}", "INFO")
                
                # Execute tool
                self._log(f"⚡ Action: {tool_to_use}", "ACTION")
                
                result = self._execute_tool(tool_to_use, query)
                tools_used.add(tool_to_use)
                
                # Process observation
                observation = self._format_tool_result(result, tool_to_use)
                self._log(f"👁️ Observation: {observation[:200]}...", "OBSERVATION")
                self.observations.append(observation)
                
                # Record step
                reasoning_steps.append({
                    "iteration": iteration,
                    "thought": f"I should use {tool_to_use} to address this query",
                    "action": tool_to_use,
                    "action_input": query,
                    "observation": observation,
                    "success": result.get("success", False)
                })
                
                # Check if we have sufficient information
                # For yield prediction, pass results to LLM for better analysis
                if result.get("success") and tool_to_use == "yield_prediction":
                    self._log(f"✅ Got yield prediction results, now calling LLM for analysis", "INFO")
                    # Create context-rich query for LLM
                    llm_query = f"{query}\n\nYield Prediction Result: {observation}"
                    llm_result = self._execute_tool("llm_generation", llm_query)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM analyzed yield prediction", "SUCCESS")
                        
                        # Add LLM step to reasoning
                        reasoning_steps.append({
                            "iteration": iteration + 0.5,  # Sub-step
                            "thought": "I should analyze the yield prediction with detailed insights",
                            "action": "llm_generation",
                            "action_input": llm_query,
                            "observation": final_answer,
                            "success": True
                        })
                        break
                    else:
                        # Fallback to raw prediction
                        final_answer = observation
                        break
                
                # For pest detection, pass results to LLM for detailed analysis
                if result.get("success") and tool_to_use == "pest_detection":
                    self._log(f"✅ Got pest detection results, now calling LLM for analysis", "INFO")
                    # Create context-rich query for LLM
                    llm_query = f"{query}\n\nPest Detection Result: {observation}"
                    llm_result = self._execute_tool("llm_generation", llm_query)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM analyzed pest detection", "SUCCESS")
                        
                        # Add LLM step to reasoning
                        reasoning_steps.append({
                            "iteration": iteration + 0.5,  # Sub-step
                            "thought": "I should analyze the pest detection with detailed treatment and prevention information",
                            "action": "llm_generation",
                            "action_input": llm_query,
                            "observation": final_answer,
                            "success": True
                        })
                        break
                    else:
                        # Fallback to raw detection
                        final_answer = observation
                        break
                
                # For other prediction tools, stop immediately with their result  
                if result.get("success") and tool_to_use in ["weather_prediction", "weather_realtime"]:
                    final_answer = observation
                    self._log(f"✅ Got successful result from {tool_to_use}, using it as final answer", "SUCCESS")
                    break
                
                # For Tavily search, pass results to LLM for better synthesis
                if result.get("success") and tool_to_use == "tavily_search":
                    self._log(f"✅ Got Tavily results, now calling LLM for synthesis", "INFO")
                    # Directly call LLM with Tavily context
                    llm_result = self._execute_tool("llm_generation", query)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized Tavily results", "SUCCESS")
                        break
                    else:
                        # Fallback to raw Tavily results
                        final_answer = observation
                        break
                
                # For RAG retrieval, pass results to LLM for better synthesis
                if result.get("success") and tool_to_use == "rag_retrieval":
                    self._log(f"✅ Got RAG results, now calling LLM for synthesis", "INFO")
                    # Directly call LLM with RAG context in observations
                    llm_result = self._execute_tool("llm_generation", query)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized RAG results", "SUCCESS")
                        
                        # Add LLM step to reasoning
                        reasoning_steps.append({
                            "iteration": iteration + 0.5,  # Sub-step
                            "thought": "I should synthesize the RAG results into a clear answer",
                            "action": "llm_generation",
                            "action_input": query,
                            "observation": final_answer,
                            "success": True
                        })
                        break
                    else:
                        # Fallback to raw RAG results
                        final_answer = observation
                        break
                
                # For LLM generation, stop after getting results
                if result.get("success") and tool_to_use == "llm_generation":
                    final_answer = observation
                    self._log(f"✅ Got successful result from {tool_to_use}, stopping", "SUCCESS")
                    break
                
                # Update context for next iteration
                conversation_context = f"\nPrevious step: Used {tool_to_use}, got: {observation[:100]}..."
                
            except Exception as e:
                self._log(f"❌ Error in iteration {iteration}: {str(e)}", "ERROR")
                # Continue to next iteration or use fallback
                if iteration >= 2 or not tools_used:
                    # Try using LLM generation as fallback
                    try:
                        result = self._execute_tool("llm_generation", query)
                        if result.get("success"):
                            final_answer = self._format_tool_result(result, "llm_generation")
                            tools_used.add("llm_generation")
                            break
                    except:
                        pass
                continue
        
        # If no final answer, use the last observation
        if not final_answer and self.observations:
            final_answer = self.observations[-1]
        elif not final_answer:
            final_answer = "I apologize, but I couldn't process your request successfully."
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "success": True,
            "query": query,
            "final_answer": final_answer,
            "reasoning_steps": reasoning_steps,
            "tools_used": list(tools_used),
            "total_iterations": self.current_iteration,
            "execution_time": execution_time
        }
        
        # Add to history
        self.history.add_turn(query, final_answer, {
            "tools": list(tools_used),
            "iterations": self.current_iteration,
            "execution_time": execution_time
        })
        
        self._log(f"\n{'='*70}", "INFO")
        self._log(f"✅ AGENT COMPLETED in {execution_time:.2f}s", "SUCCESS")
        self._log(f"ℹ️ Tools used: {', '.join(tools_used)}", "INFO")
        self._log(f"{'='*70}", "INFO")
        
        return response
    
    def _format_tool_result(self, result: Dict[str, Any], tool_name: str) -> str:
        """
        Format tool result into a readable string.
        
        Args:
            result: Tool result dictionary
            tool_name: Name of the tool
            
        Returns:
            Formatted string
        """
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if tool_name == "rag_retrieval":
            return result.get("context", "No context found")
        elif tool_name == "llm_generation":
            return result.get("generated_text", result.get("answer", "No answer generated"))
        elif tool_name == "translation":
            return result.get("translated_text", "Translation failed")
        elif tool_name == "yield_prediction":
            if result.get("success"):
                pred = result.get('prediction', 'N/A')
                unit = result.get('unit', '')
                crop = result.get('crop', 'Unknown')
                state = result.get('state', 'Unknown')
                return f"Predicted yield for {crop} in {state}: {pred} {unit}"
            else:
                return f"Error: {result.get('error', 'Prediction failed')}"
        elif tool_name == "pest_detection":
            if result.get("success"):
                pred = result.get('top_prediction', 'N/A')
                conf = result.get('confidence', 0)
                return f"Detected: {pred} ({conf:.0%} confidence)"
            elif result.get("guidance"):
                guidance = result.get("guidance", {})
                options = "\n".join(guidance.get("options", []))
                return f"Image required for pest detection.\n{options}"
            else:
                return f"Error: {result.get('error', 'Detection failed')}"
        elif tool_name == "weather_prediction":
            return result.get("advice", result.get("message", "Weather information unavailable"))
        elif tool_name == "weather_realtime":
            # Return the weather data string directly
            return result.get("result", "Weather data unavailable")
        elif tool_name == "tavily_search":
            # Return the formatted summary from Tavily with sources
            return result.get("summary", "No search results found")
        else:
            return str(result)
    
    def get_reasoning_trace(self) -> str:
        """
        Get formatted reasoning trace.
        
        Returns:
            Formatted trace string
        """
        trace = []
        for i, (thought, action, obs) in enumerate(zip(self.thoughts, self.actions, self.observations), 1):
            trace.append(f"Step {i}:")
            trace.append(f"  Thought: {thought}")
            trace.append(f"  Action: {action}")
            trace.append(f"  Observation: {obs[:100]}...")
        
        return "\n".join(trace)


# Example usage
if __name__ == "__main__":
    agent = ReActAgent(max_iterations=3, verbose=True)
    
    # Test query
    query = "What are the best fertilizers for rice cultivation?"
    
    result = agent.run(query)
    
    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(f"Query: {result['query']}")
    print(f"Answer: {result['final_answer']}")
    print(f"Tools Used: {', '.join(result['tools_used'])}")
    print(f"Iterations: {result['total_iterations']}")
    print(f"Time: {result['execution_time']:.2f}s")
    print("="*70)
