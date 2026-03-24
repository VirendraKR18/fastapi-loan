"""
Pydantic request models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., description="User question about the document")
    chat_history: Optional[List[dict]] = Field(
        default=None,
        description="Previous chat history for context"
    )


class ChatHistoryItem(BaseModel):
    """Chat history item"""
    question: str
    answer: str


class MedicalQueryRequest(BaseModel):
    """Request model for medical assistant endpoint"""
    query: str = Field(..., description="User medical query")
    chat_history: Optional[List[ChatHistoryItem]] = Field(
        default=None,
        description="Previous conversation history"
    )
