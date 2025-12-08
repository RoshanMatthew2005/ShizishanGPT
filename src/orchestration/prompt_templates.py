"""
Prompt Templates
Templates for various prompting scenarios.
"""
from typing import Dict, Any, List


class PromptTemplate:
    """Base class for prompt templates."""
    
    def __init__(self, template: str, input_variables: List[str]):
        """
        Initialize a prompt template.
        
        Args:
            template: Template string with {variable} placeholders
            input_variables: List of required variable names
        """
        self.template = template
        self.input_variables = input_variables
    
    def format(self, **kwargs) -> str:
        """
        Format the template with provided variables.
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Formatted string
        """
        # Check for missing variables
        missing = set(self.input_variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        return self.template.format(**kwargs)
    
    def __call__(self, **kwargs) -> str:
        """Allow template to be called directly."""
        return self.format(**kwargs)


# ReAct Agent Templates
REACT_TEMPLATE = PromptTemplate(
    template="""You are ShizishanGPT, an expert agricultural AI assistant that uses specialized tools to answer questions.

**AVAILABLE TOOLS:**
{tools}

**CRITICAL TOOL SELECTION RULES:**

1. **ALWAYS use tavily_search for:**
   - Chemical/pesticide product information (names, dosages, brands)
   - Government schemes, subsidies, policies (frequently updated)
   - Current disease outbreaks, pest warnings, alerts
   - Latest treatment protocols, new research findings
   - Market prices, product availability, suppliers
   - Recent agricultural news, advisories
   - ANY query containing: "latest", "current", "new", "2024", "2025", "buy", "where to get", "price"

2. **Use query_rag for:**
   - Established crop cultivation practices
   - Soil science fundamentals, plant biology
   - General pest lifecycle information (non-treatment)
   - Historical agricultural data, textbook knowledge

3. **Use predict_* tools for:**
   - Forecasting tasks (yield, weather predictions)

4. **Tool Chaining Strategy:**
   - For product/chemical queries: tavily_search → query_rag (for application methods)
   - For treatment queries: tavily_search (latest products) → query_rag (techniques)
   - NEVER hallucinate chemical names or dosages - ALWAYS verify via tavily_search
   - Cite sources from Tavily results (include URLs in final answer)

**RESPONSE FORMAT:**
Thought: (reason about what information is needed and which tool to use)
Action: (choose ONE tool name)
Action Input: (specific input for the tool)
Observation: (result from the tool)
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have enough information to answer
Final Answer: (comprehensive answer with source citations when using Tavily)

**Question:** {question}

Begin!

Thought:""",
    input_variables=["question", "tools"]
)


# RAG Templates
RAG_CONTEXT_TEMPLATE = PromptTemplate(
    template="""Use the following context to answer the question. If you cannot answer based on the context, say so.

Context:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"]
)


# Q&A Templates
QA_TEMPLATE = PromptTemplate(
    template="""Q: {question}
A:""",
    input_variables=["question"]
)


# Translation Templates
TRANSLATION_TEMPLATE = PromptTemplate(
    template="""Translate the following text from {source_lang} to {target_lang}:

{text}

Translation:""",
    input_variables=["text", "source_lang", "target_lang"]
)


# Conversation Template
CONVERSATION_TEMPLATE = PromptTemplate(
    template="""Previous conversation:
{history}

User: {query}
Assistant:""",
    input_variables=["history", "query"]
)


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("PROMPT TEMPLATES TEST")
    print("="*70)
    
    # Test RAG template
    rag_prompt = RAG_CONTEXT_TEMPLATE.format(
        context="Rice requires 600-1200mm annual rainfall",
        question="How much water does rice need?"
    )
    print("\nRAG Template:")
    print(rag_prompt)
    
    # Test Q&A template
    qa_prompt = QA_TEMPLATE.format(question="What is nitrogen fertilizer?")
    print("\nQ&A Template:")
    print(qa_prompt)
    
    print("="*70)
