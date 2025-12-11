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

Use yield_prediction when the question asks about crop yield/production for a specific crop and location:
   - "Predict wheat yield in Punjab"
   - "What will be rice production in Tamil Nadu?"
   - "Expected harvest for maize in Maharashtra"
   - "Crop output for cotton with 800mm rainfall"
   
Required information:
   - Crop name (wheat, rice, maize, etc.)
   - State/region (Punjab, Tamil Nadu, etc.)
   - Optional: Rainfall amount, irrigation details
   
Examples that MUST use yield_prediction:
   - "Predicting Wheat Yield in Punjab with 800mm Rainfall" → yield_prediction
   - "What will be the rice yield in Telangana?" → yield_prediction
   - "Expected maize production in Karnataka" → yield_prediction
   - "Harvest prediction for cotton in Gujarat" → yield_prediction

**PRIORITY 3: Pest Detection Tool**

If the question describes crop symptoms, diseases, pests, insects, leaf color 
changes, or damage → call pest_detection.

**PRIORITY 4: Knowledge Graph (Structured Crop Relationships)**

Use agri_kg_query when the query asks about relationships between crops and:
   - Diseases: "What diseases affect rice?", "diseases in wheat", "rice blast"
   - Pests: "Which pests attack maize?", "pests in cotton", "aphids"
   - Fertilizers: "What fertilizers does wheat need?", "fertilizer for rice"
   - Soil: "What is ideal soil for maize?", "soil type for crops"
   - Treatments: "How to control blast disease?", "treatment for pests"

AgriKG provides instant structured answers from the knowledge graph for:
- Crop-disease relationships
- Crop-pest relationships
- Crop-fertilizer requirements
- Ideal soil types for crops
- Disease/pest treatments

**PRIORITY 5: Weather Queries (Use Tavily Search)**

For ALL weather-related questions → use tavily_search:
   - "What's the weather in Punjab today?" → tavily_search
   - "Will it rain tomorrow?" → tavily_search  
   - "Weather forecast for next week" → tavily_search
   - "How will drought affect crops?" → tavily_search → llm_generation
   - "Temperature and rainfall patterns" → tavily_search

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

**FORMATTING REQUIREMENTS:**
- Use proper spacing between sections and bullet points
- Add blank lines between major sections (e.g., between **1. Section** and **2. Section**)
- Add blank lines before and after nested bullet points for readability
- Structure with clear headings using **bold** for main sections
- Use * for bullet points with proper indentation
- Ensure nested points are indented with proper spacing
- Example format:
  **1. Main Section:**
  
  * Point one with details
  * Point two with details
  
  **2. Another Section:**
  
  * First point
  * Second point

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
    
    def _clean_citations(self, text: str) -> str:
        """
        Remove citation markers, source references, and page numbers from text.
        
        Args:
            text: Text with citation markers and source references
            
        Returns:
            Text with citations removed
        """
        if not text:
            return text
        
        # Remove source citations: (Source: "...", pg. 264), (Source: "...")
        text = re.sub(r'\(Source:\s*[^)]+\)', '', text, flags=re.IGNORECASE)
        
        # Remove source citations in square brackets: [Source: "..."]
        text = re.sub(r'\[Source:\s*[^\]]+\]', '', text, flags=re.IGNORECASE)
        
        # Remove inline source references: Source: "..." or Source: Title
        text = re.sub(r'Source:\s*["\']?[^"\'\n]+["\']?', '', text, flags=re.IGNORECASE)
        
        # Remove citation markers in square brackets: [1], [2], [3], etc.
        # Matches [number] or [number, number] patterns
        text = re.sub(r'\s*\[\d+(?:,\s*\d+)*\]', '', text)
        
        # Remove page references: "pg. 123", "page 123", "p. 123", "pp. 123-456"
        text = re.sub(r'\b(?:pg|page|p|pp)\.?\s*\d+(?:\s*-\s*\d+)?\b', '', text, flags=re.IGNORECASE)
        
        # Remove chapter/section references in text
        text = re.sub(r'\b(?:Chapter|Ch|Section|Sec)\.?\s*[\d.]+\b', '', text, flags=re.IGNORECASE)
        
        # Remove any double spaces created by removal
        text = re.sub(r'\s{2,}', ' ', text)
        
        # Clean up spaces before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Remove empty parentheses left after cleaning
        text = re.sub(r'\(\s*\)', '', text)
        
        # Clean up multiple punctuation marks
        text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', text)
        
        return text.strip()
    
    def _clean_plain_text_formatting(self, text: str) -> str:
        """
        Clean up plain text formatting - remove markdown symbols and fix spacing.
        Designed for LLM output that should be plain text without markdown.
        
        Args:
            text: Text potentially containing markdown formatting
            
        Returns:
            Clean plain text with proper spacing
        """
        if not text:
            return text
        
        # Remove markdown bold markers: **text** → text
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Remove markdown headers: ## Header → Header
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Normalize bullet points to use hyphens
        text = re.sub(r'^\s*[*•]\s+', '- ', text, flags=re.MULTILINE)
        
        # Fix excessive spacing between sections (max 1 blank line)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace on each line
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Ensure single space after punctuation
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        text = re.sub(r'([.,!?;:])\s{2,}', r'\1 ', text)
        
        # Fix common spacing issues around colons in headers
        # "HEADER :" → "HEADER:"
        text = re.sub(r'([A-Z\s]+)\s+:', r'\1:', text)
        
        return text.strip()
    
    def _format_markdown_output(self, text: str) -> str:
        """
        Ensure proper markdown spacing without destroying structure.
        Only adds spacing between sections - does NOT remove markdown symbols.
        
        Args:
            text: Markdown text from LLM
            
        Returns:
            Clean markdown with proper spacing
        """
        if not text:
            return text
        
        lines = text.split('\n')
        formatted = []
        prev_was_blank = True
        prev_was_heading = False
        prev_was_bullet = False
        prev_was_numbered = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip if empty
            if not stripped:
                # Keep track but don't add yet
                prev_was_blank = True
                continue
            
            # Detect line types
            is_heading = stripped.startswith('#')
            is_bullet = stripped.startswith('-') or stripped.startswith('*')
            is_numbered = bool(re.match(r'^\d+\.', stripped))
            is_text = not (is_heading or is_bullet or is_numbered)
            
            # Add blank line before heading (unless first line)
            if is_heading and formatted and not prev_was_blank:
                formatted.append('')
            
            # Add blank line before numbered list from text
            if is_numbered and prev_was_text and not prev_was_blank:
                formatted.append('')
            
            # Add blank line before bullet list from text/heading
            if is_bullet and (prev_was_text or prev_was_heading) and not prev_was_blank:
                formatted.append('')
            
            # Add blank line before text from bullet/numbered
            if is_text and (prev_was_bullet or prev_was_numbered) and not prev_was_blank:
                formatted.append('')
            
            # Add the line as-is (preserve original content)
            formatted.append(line.rstrip())
            
            # Update state
            prev_was_blank = False
            prev_was_heading = is_heading
            prev_was_bullet = is_bullet
            prev_was_numbered = is_numbered
            prev_was_text = is_text
        
        result = '\n'.join(formatted)
        
        # Only clean up excessive blank lines (more than 2)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def _ensure_proper_spacing(self, text: str) -> str:
        """
        Legacy spacing function - now replaced by _format_markdown_output.
        Kept for backwards compatibility.
        """
        return self._format_markdown_output(text)
    
    def _final_markdown_cleanup(self, text: str) -> str:
        """
        Final light cleanup - only remove duplicates and excessive whitespace.
        Does NOT modify markdown structure or symbols.
        
        Args:
            text: Formatted Markdown text
            
        Returns:
            Clean markdown
        """
        if not text:
            return text
        
        lines = text.split('\n')
        cleaned_lines = []
        prev_line = None
        
        for line in lines:
            stripped = line.strip()
            
            # Skip exact duplicate consecutive lines only
            if prev_line and stripped and stripped == prev_line:
                continue
            
            cleaned_lines.append(line)
            if stripped:  # Only update prev_line if current line has content
                prev_line = stripped
        
        text = '\n'.join(cleaned_lines)
        
        # Clean up excessive blank lines (max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace on each line (but preserve line structure)
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        return text.strip()
    
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
            elif tool_name == "agri_kg_query":
                # Extract query from parsed input for Knowledge Graph
                query_text = parsed_input.get("query", tool_input if isinstance(tool_input, str) else "")
                result = tool.run(query=query_text)
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
                
                # No special handling needed - removed weather_prediction and weather_realtime tools
                
                # For Tavily search, pass results to LLM for better synthesis
                if result.get("success") and tool_to_use == "tavily_search":
                    self._log(f"✅ Got Tavily results, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    tavily_content = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are helping a farmer with their question. Use the search results below to provide a comprehensive, practical answer.

FARMER'S QUESTION:
{query}

SEARCH RESULTS:
{tavily_content}

YOUR TASK:
Write a clear, detailed answer that directly addresses the farmer's question. Use the information from the search results to provide practical, actionable advice.

FORMATTING GUIDELINES:
- Use proper markdown formatting with ## for sections and ### for subsections
- Organize information into numbered lists (1., 2., 3.) for main topics
- Use bullet points (-) for specific details, examples, or sub-points
- Put blank lines between major sections
- Use **bold** for emphasis on key terms
- Be specific with measurements, timings, and methods
- Focus on practical implementation

Keep your answer comprehensive (200-400 words) and farmer-friendly. Do NOT mention sources or include citations."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
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
                    
                    # Extract the actual content from the result
                    rag_content = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are helping a farmer with their question. Use the retrieved agricultural knowledge below to provide a comprehensive, practical answer.

FARMER'S QUESTION:
{query}

RETRIEVED AGRICULTURAL KNOWLEDGE:
{rag_content}

YOUR TASK:
Write a clear, detailed answer that directly addresses the farmer's question. Use the information from the retrieved documents to provide practical, actionable advice. Synthesize the information into a coherent response.

FORMATTING GUIDELINES:
- Use proper markdown formatting with ## for sections and ### for subsections
- Organize information into numbered lists (1., 2., 3.) for main topics
- Use bullet points (-) for specific details, techniques, or examples
- Put blank lines between major sections
- Use **bold** for emphasis on key terms
- Be specific with measurements, timings, application rates, and methods
- Include practical implementation steps
- Focus on real-world farming applications

Keep your answer comprehensive (200-400 words) and farmer-friendly. Do NOT mention document sources, page numbers, or include citations."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized RAG results", "SUCCESS")
                        
                        # Add LLM step to reasoning
                        reasoning_steps.append({
                            "iteration": iteration + 0.5,  # Sub-step
                            "thought": "I should synthesize the RAG results into a clear answer",
                            "action": "llm_generation",
                            "action_input": synthesis_prompt,
                            "observation": final_answer,
                            "success": True
                        })
                        break
                    else:
                        # Fallback to raw RAG results
                        final_answer = observation
                        break
                
                # For AgriKG query, pass results to LLM for better synthesis
                if result.get("success") and tool_to_use == "agri_kg_query":
                    self._log(f"✅ Got AgriKG results, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    kg_content = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are helping a farmer with their question. Use the agricultural knowledge graph data below to provide a comprehensive, practical answer.

FARMER'S QUESTION:
{query}

KNOWLEDGE GRAPH DATA:
{kg_content}

YOUR TASK:
Write a clear, detailed answer that directly addresses the farmer's question. Use the structured agricultural knowledge to provide practical, actionable advice. Explain relationships and connections between concepts.

FORMATTING GUIDELINES:
- Use proper markdown formatting with ## for sections and ### for subsections
- Organize information into numbered lists (1., 2., 3.) for main topics
- Use bullet points (-) for specific details, relationships, or examples
- Put blank lines between major sections
- Use **bold** for emphasis on key terms
- Be specific with agricultural relationships and recommendations
- Focus on practical farming applications

Keep your answer comprehensive (200-400 words) and farmer-friendly. Do NOT mention sources or include citations."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized AgriKG results", "SUCCESS")
                        
                        # Add LLM step to reasoning
                        reasoning_steps.append({
                            "iteration": iteration + 0.5,  # Sub-step
                            "thought": "I should synthesize the AgriKG results into a clear answer",
                            "action": "llm_generation",
                            "action_input": synthesis_prompt,
                            "observation": final_answer,
                            "success": True
                        })
                        break
                    else:
                        # Fallback to raw AgriKG results
                        final_answer = observation
                        break
                
                # For Crop Climate Recommendation, pass results to LLM for detailed synthesis
                if result.get("success") and tool_to_use == "crop_climate_recommendation":
                    self._log(f"✅ Got crop climate recommendation, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    model_output = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are an agricultural advisor helping a farmer choose the best crop. Use the machine learning model prediction below to provide comprehensive farming advice.

FARMER'S QUESTION:
{query}

CROP CLIMATE RECOMMENDATION MODEL OUTPUT:
{model_output}

YOUR TASK:
Provide a detailed, practical recommendation that helps the farmer make an informed decision. Explain WHY the recommended crop is suitable, analyze the climate conditions, and provide actionable farming advice.

REQUIRED SECTIONS:

1. RECOMMENDED CROP
- State the top crop with confidence level
- Explain specifically why this crop is ideal for the given temperature, humidity, rainfall, and soil nutrients
- Mention expected benefits and yield potential

2. CLIMATE SUITABILITY ANALYSIS
- Temperature: Analyze how the given temperature suits this crop
- Humidity: Explain the humidity requirements and current suitability
- Rainfall: Assess if the rainfall pattern is adequate for this crop

3. ALTERNATIVE OPTIONS
- List 2-3 alternative crops with brief explanations of their suitability
- Mention any trade-offs compared to the top recommendation

4. PRACTICAL FARMING GUIDANCE
- Best planting season and timing
- Soil preparation requirements
- Irrigation and water management tips
- Expected growth duration

5. IMPORTANT CONSIDERATIONS
- Any weather-related risks or precautions
- Common challenges with this crop in similar conditions
- Tips to maximize yield

FORMATTING: Use markdown with ## for main sections and ### for subsections. Use numbered lists (1., 2., 3.) and bullet points (-) for details. Use **bold** for emphasis. Put blank lines between sections. Target 250-350 words."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized crop climate recommendation", "SUCCESS")
                        break
                    else:
                        final_answer = observation
                        break
                
                # For Crop Nutrient Recommendation, pass results to LLM for detailed synthesis
                if result.get("success") and tool_to_use == "crop_nutrient_recommendation":
                    self._log(f"✅ Got crop nutrient recommendation, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    model_output = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are an agricultural advisor helping a farmer choose crops based on soil analysis. Use the model prediction below to provide comprehensive advice.

FARMER'S QUESTION:
{query}

CROP NUTRIENT RECOMMENDATION MODEL OUTPUT:
{model_output}

YOUR TASK:
Provide detailed, practical recommendations based on the soil nutrient analysis. Help the farmer understand their soil health and choose the best crop.

REQUIRED SECTIONS:

1. RECOMMENDED CROP
- State the top crop with confidence level
- Explain why this crop matches the soil nutrient profile
- Mention expected yield potential with current soil conditions

2. SOIL HEALTH ASSESSMENT
- pH Level: Analyze if it's optimal, acidic, or alkaline and what this means
- NPK Status: Evaluate Nitrogen, Phosphorus, and Potassium levels (high/medium/low)
- Micronutrients: Assess key micronutrients (S, Cu, Fe, Mn, Zn, B) status
- Overall soil fertility rating

3. ALTERNATIVE CROP OPTIONS
- List 2-3 other suitable crops based on the soil analysis
- Explain briefly why each is compatible

4. FERTILIZER RECOMMENDATIONS
- Specific fertilizers needed to optimize soil for the recommended crop
- Approximate application rates (kg per acre or per hectare)
- Best timing for fertilizer application (before planting, during growth)
- Organic vs chemical options

5. SOIL IMPROVEMENT STRATEGY
- Priority actions to enhance soil health
- Long-term soil management tips
- Expected timeline for improvements

FORMATTING: Use markdown with ## for main sections and ### for subsections. Use numbered lists (1., 2., 3.) and bullet points (-) for details. Use **bold** for emphasis. Be specific with measurements. Target 300-400 words."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized crop nutrient recommendation", "SUCCESS")
                        break
                    else:
                        final_answer = observation
                        break
                
                # For Soil Moisture Classification, pass results to LLM for detailed synthesis
                if result.get("success") and tool_to_use == "soil_moisture_classification":
                    self._log(f"✅ Got soil moisture classification, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    model_output = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are an irrigation specialist helping a farmer manage soil moisture. Use the sensor analysis below to provide immediate, actionable advice.

FARMER'S QUESTION:
{query}

SOIL MOISTURE SENSOR ANALYSIS:
{model_output}

YOUR TASK:
Provide clear, urgent guidance on irrigation decisions based on the soil moisture classification. Focus on immediate actions the farmer should take.

REQUIRED SECTIONS:

1. CURRENT MOISTURE STATUS
- State the soil moisture classification (Very Dry / Dry / Wet / Very Wet)
- Explain what this means for the crops right now
- Indicate urgency level

2. IRRIGATION DECISION
- Should the farmer irrigate? YES or NO
- If YES: How soon? (Immediately / Within 6 hours / Within 24 hours)
- If NO: When to check again?
- Approximate water amount needed if applicable

3. WEATHER AND ENVIRONMENTAL FACTORS
- How the current temperature affects soil moisture and crop water needs
- Impact of atmospheric pressure and altitude on irrigation requirements
- Any weather considerations

4. IMMEDIATE ACTION STEPS
- List 3-4 specific actions the farmer should take right now
- Be very specific and practical
- Include timing for each action

5. MONITORING PLAN
- When to check soil moisture again
- What sensor readings to look for
- Signs to watch in the crops

FORMATTING: Use markdown with ## for main sections and ### for subsections. Use numbered lists (1., 2., 3.) and bullet points (-) for details. Use **bold** for emphasis. Be direct and action-focused. Target 200-300 words."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized soil moisture classification", "SUCCESS")
                        break
                    else:
                        final_answer = observation
                        break
                
                # For Soil Fertility Classification, pass results to LLM for detailed synthesis
                if result.get("success") and tool_to_use == "soil_fertility_classification":
                    self._log(f"✅ Got soil fertility classification, now calling LLM for synthesis", "INFO")
                    
                    # Extract the actual content from the result
                    model_output = result.get("output", observation)
                    
                    synthesis_prompt = f"""You are a soil health expert helping a farmer improve their land. Use the comprehensive soil analysis below to provide detailed guidance.

FARMER'S QUESTION:
{query}

SOIL FERTILITY ANALYSIS:
{model_output}

YOUR TASK:
Provide detailed, actionable advice to help the farmer understand and improve their soil fertility. Be specific about nutrients, amendments, and timelines.

REQUIRED SECTIONS:

1. SOIL FERTILITY RATING
- State the classification (Low / Medium / High Fertility)
- Explain what this means for crop production and yields
- Indicate whether immediate action is needed

2. DETAILED NUTRIENT ANALYSIS
- Major Nutrients: Assess N, P, K levels individually
- pH Status: Evaluate soil acidity/alkalinity and implications
- Organic Content: Assess organic matter and what it means
- Micronutrients: Evaluate S, Zn, Fe, Cu, Mn, B levels
- Identify specific deficiencies or excesses

3. IMPACT ON CROP YIELDS
- How the current fertility level affects crop production
- Expected yield compared to optimal conditions (percentage)
- Which crops would struggle vs thrive in current conditions

4. COMPREHENSIVE IMPROVEMENT PLAN
- Priority 1: Most urgent nutrient deficiency to address
- Priority 2: Secondary improvements needed
- Priority 3: Long-term soil building strategies
- Specific amendments with application rates (kg/acre or kg/hectare)
- Organic options (compost, manure, green manure)
- Chemical fertilizer options if needed

5. IMPLEMENTATION TIMELINE
- Immediate actions (this week)
- Short-term improvements (1-3 months)
- Long-term strategy (6-12 months)
- When to expect visible improvements
- When to retest soil

FORMATTING: Use markdown with ## for main sections and ### for subsections. Use numbered lists (1., 2., 3.) and bullet points (-) for details. Use **bold** for emphasis. Be very specific with measurements and methods. Target 350-450 words."""
                    
                    llm_result = self._execute_tool("llm_generation", synthesis_prompt)
                    tools_used.add("llm_generation")
                    if llm_result.get("success"):
                        final_answer = self._format_tool_result(llm_result, "llm_generation")
                        self._log(f"✅ LLM synthesized soil fertility classification", "SUCCESS")
                        break
                    else:
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
        
        # Format markdown output - preserve markdown structure with proper spacing
        final_answer = self._format_markdown_output(final_answer)
        final_answer = self._final_markdown_cleanup(final_answer)
        
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
        elif tool_name == "soil_moisture_classification":
            if result.get("success"):
                classification = result.get('classification', 'N/A')
                confidence = result.get('confidence', 0)
                sensor = result.get('sensor_readings', {})
                recommendations = result.get('recommendations', [])
                
                output = f"Soil Moisture Status: {classification} ({confidence:.1%} confidence)\\n"
                output += f"Sensor Readings: Temp {sensor.get('temperature', 'N/A')}, "
                output += f"Pressure {sensor.get('pressure', 'N/A')}, Moisture {sensor.get('soil_moisture_raw', 'N/A')}\\n\\n"
                output += "Recommendations:\\n" + "\\n".join(recommendations[:5])
                return output
            else:
                return f"Error: {result.get('error', 'Classification failed')}"
        
        elif tool_name == "crop_nutrient_recommendation":
            if result.get("success"):
                crop = result.get('recommended_crop', 'N/A')
                confidence = result.get('confidence', 0)
                top_crops = result.get('top_3_crops', [])
                recommendations = result.get('recommendations', [])
                soil_analysis = result.get('soil_analysis', {})
                
                output = f"Recommended Crop: {crop.upper()} ({confidence:.1%} confidence)\\n"
                output += f"Alternatives: {', '.join([c['crop'] for c in top_crops[1:]])}\\n\\n"
                output += "Soil Analysis:\\n"
                for key, value in soil_analysis.items():
                    output += f"- {key}: {value}\\n"
                output += "\\nRecommendations:\\n" + "\\n".join(recommendations[:6])
                return output
            else:
                return f"Error: {result.get('error', 'Recommendation failed')}"
        
        elif tool_name == "crop_climate_recommendation":
            if result.get("success"):
                crop = result.get('recommended_crop', 'N/A')
                confidence = result.get('confidence', 0)
                top_crops = result.get('top_5_crops', [])
                climate_analysis = result.get('climate_analysis', {})
                recommendations = result.get('recommendations', [])
                
                output = f"Best Crop for Climate: {crop.upper()} ({confidence:.1%} confidence)\\n"
                output += f"Top 5 Options: {', '.join([c['crop'] for c in top_crops[:5]])}\\n\\n"
                output += "Climate Analysis:\\n"
                for key, value in climate_analysis.items():
                    output += f"- {key.title()}: {value}\\n"
                output += "\\nRecommendations:\\n" + "\\n".join(recommendations[:6])
                return output
            else:
                return f"Error: {result.get('error', 'Recommendation failed')}"
        
        elif tool_name == "soil_fertility_classification":
            if result.get("success"):
                fertility = result.get('fertility_level', 'N/A')
                confidence = result.get('confidence', 0)
                deficiencies = result.get('deficiencies', [])
                recommendations = result.get('recommendations', [])
                
                output = f"Soil Fertility Level: {fertility} ({confidence:.1%} confidence)\\n\\n"
                output += "Deficiencies:\\n" + "\\n".join(deficiencies[:5]) + "\\n\\n"
                output += "Recommendations:\\n" + "\\n".join(recommendations[:8])
                return output
            else:
                return f"Error: {result.get('error', 'Classification failed')}"
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
