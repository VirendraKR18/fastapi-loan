"""
Pydantic response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI-generated answer")
    chat_history: Optional[List[dict]] = Field(
        default=None,
        description="Updated chat history"
    )


class MedicalAssistantResponse(BaseModel):
    """Response model for medical assistant endpoint"""
    answer: str = Field(..., description="Medical assistant response")
    chat_history: Optional[List[dict]] = Field(
        default=None,
        description="Updated conversation history"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
