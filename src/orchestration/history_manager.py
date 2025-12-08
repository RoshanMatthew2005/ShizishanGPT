"""
History Manager
Manages conversation history in memory.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque


class ConversationTurn:
    """Represents a single conversation turn."""
    
    def __init__(self, 
                 user_query: str, 
                 assistant_response: str,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a conversation turn.
        
        Args:
            user_query: User's query
            assistant_response: Assistant's response
            metadata: Optional metadata (tool used, execution time, etc.)
        """
        self.user_query = user_query
        self.assistant_response = assistant_response
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_query": self.user_query,
            "assistant_response": self.assistant_response,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<ConversationTurn: {self.timestamp.strftime('%H:%M:%S')}>"


class HistoryManager:
    """Manages conversation history."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the history manager.
        
        Args:
            max_history: Maximum number of turns to keep in memory
        """
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.session_start = datetime.now()
    
    def add_turn(self, 
                 user_query: str, 
                 assistant_response: str,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a conversation turn to history.
        
        Args:
            user_query: User's query
            assistant_response: Assistant's response
            metadata: Optional metadata
        """
        turn = ConversationTurn(user_query, assistant_response, metadata)
        self.history.append(turn)
    
    def get_recent_history(self, n: int = 5) -> List[ConversationTurn]:
        """
        Get the n most recent conversation turns.
        
        Args:
            n: Number of recent turns to retrieve
            
        Returns:
            List of conversation turns
        """
        return list(self.history)[-n:]
    
    def get_full_history(self) -> List[ConversationTurn]:
        """
        Get full conversation history.
        
        Returns:
            List of all conversation turns
        """
        return list(self.history)
    
    def format_history(self, n: int = 5, include_metadata: bool = False) -> str:
        """
        Format conversation history as a string.
        
        Args:
            n: Number of recent turns to include
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted history string
        """
        recent = self.get_recent_history(n)
        
        if not recent:
            return "No conversation history."
        
        formatted = []
        for i, turn in enumerate(recent, 1):
            formatted.append(f"Turn {i}:")
            formatted.append(f"User: {turn.user_query}")
            formatted.append(f"Assistant: {turn.assistant_response}")
            
            if include_metadata and turn.metadata:
                formatted.append(f"Metadata: {turn.metadata}")
            
            formatted.append("")  # Empty line between turns
        
        return "\n".join(formatted)
    
    def get_context_summary(self, max_length: int = 500) -> str:
        """
        Get a summary of recent context for prompting.
        
        Args:
            max_length: Maximum character length
            
        Returns:
            Context summary string
        """
        recent = self.get_recent_history(3)
        
        if not recent:
            return ""
        
        context_parts = []
        for turn in recent:
            context_parts.append(f"Q: {turn.user_query[:100]}")
            context_parts.append(f"A: {turn.assistant_response[:100]}")
        
        context = "\n".join(context_parts)
        
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context
    
    def clear(self) -> None:
        """Clear all conversation history."""
        self.history.clear()
        self.session_start = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the conversation.
        
        Returns:
            Dictionary with statistics
        """
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "total_turns": len(self.history),
            "max_history": self.max_history,
            "session_duration_seconds": session_duration,
            "session_start": self.session_start.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entire history to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "session_start": self.session_start.isoformat(),
            "turns": [turn.to_dict() for turn in self.history],
            "stats": self.get_stats()
        }
    
    def __len__(self) -> int:
        """Get number of turns in history."""
        return len(self.history)
    
    def __repr__(self) -> str:
        return f"<HistoryManager: {len(self.history)} turns>"


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("HISTORY MANAGER TEST")
    print("="*70)
    
    manager = HistoryManager(max_history=5)
    
    # Add some turns
    manager.add_turn(
        "What fertilizers for rice?",
        "Use NPK fertilizers with ratio 4:2:1",
        {"tool": "rag_retrieval", "confidence": 0.85}
    )
    
    manager.add_turn(
        "What about pest control?",
        "Use integrated pest management strategies",
        {"tool": "llm_generation", "confidence": 0.75}
    )
    
    manager.add_turn(
        "Translate to Hindi",
        "चावल के लिए उर्वरक",
        {"tool": "translation", "target_lang": "hi"}
    )
    
    # Display formatted history
    print("\nFormatted History:")
    print(manager.format_history(include_metadata=True))
    
    # Get stats
    stats = manager.get_stats()
    print(f"\nStats:")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Session duration: {stats['session_duration_seconds']:.1f}s")
    
    # Get context summary
    print(f"\nContext Summary:")
    print(manager.get_context_summary(200))
    
    print("="*70)
