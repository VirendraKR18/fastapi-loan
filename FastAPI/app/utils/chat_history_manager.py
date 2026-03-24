"""
Chat history manager for RAG Q&A
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ChatHistoryManager:
    """Manage chat history with automatic trimming"""
    
    def __init__(self, max_size: int = 3):
        """
        Initialize chat history manager
        
        Args:
            max_size: Maximum number of Q&A pairs to keep
        """
        self.max_size = max_size
    
    def add_qa_pair(
        self, 
        history: List[Dict[str, str]], 
        question: str, 
        answer: str
    ) -> List[Dict[str, str]]:
        """
        Add Q&A pair to history and trim if needed
        
        Args:
            history: Current chat history
            question: User question
            answer: AI answer
            
        Returns:
            Updated chat history
        """
        # Create new Q&A pair
        qa_pair = {
            "question": question,
            "answer": answer
        }
        
        # Add to history
        history.append(qa_pair)
        
        # Trim if exceeds max size
        if len(history) > self.max_size:
            trimmed = self.trim_history(history)
            logger.info(f"Chat history trimmed from {len(history)} to {len(trimmed)} items")
            return trimmed
        
        return history
    
    def trim_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Trim history to max size by removing oldest entries
        
        Args:
            history: Chat history to trim
            
        Returns:
            Trimmed chat history
        """
        if len(history) <= self.max_size:
            return history
        
        # Keep only the most recent max_size items
        return history[-self.max_size:]
    
    def validate_history(self, history: Any) -> List[Dict[str, str]]:
        """
        Validate chat history format and reset if corrupted
        
        Args:
            history: Chat history to validate
            
        Returns:
            Validated chat history or empty list if corrupted
        """
        # Check if history is a list
        if not isinstance(history, list):
            logger.warning("Chat history is not a list, resetting to empty")
            return []
        
        # Validate each item
        validated = []
        for item in history:
            if not isinstance(item, dict):
                logger.warning(f"Invalid history item (not dict): {type(item)}")
                continue
            
            if 'question' not in item or 'answer' not in item:
                logger.warning(f"Invalid history item (missing fields): {item.keys()}")
                continue
            
            if not isinstance(item['question'], str) or not isinstance(item['answer'], str):
                logger.warning(f"Invalid history item (wrong types)")
                continue
            
            validated.append(item)
        
        # Trim validated history
        if len(validated) > self.max_size:
            validated = validated[-self.max_size:]
        
        return validated
    
    def reset_history(self) -> List[Dict[str, str]]:
        """
        Reset history to empty list
        
        Returns:
            Empty list
        """
        logger.info("Chat history reset to empty")
        return []


# Global instance
chat_history_manager = ChatHistoryManager(max_size=3)
