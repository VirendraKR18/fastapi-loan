"""
Pydantic models for API requests and responses
"""
from .requests import ChatRequest, MedicalQueryRequest, ChatHistoryItem
from .responses import ChatResponse, MedicalAssistantResponse, HealthCheckResponse

__all__ = [
    "ChatRequest",
    "ChatHistoryItem",
    "MedicalQueryRequest",
    "ChatResponse",
    "MedicalAssistantResponse",
    "HealthCheckResponse",
]
