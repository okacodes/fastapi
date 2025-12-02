from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Business(BaseModel):
    """Business model for service businesses"""
    name: str
    email: str
    username: str
    password: str
    api_key: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatbotConfig(BaseModel):
    """Configuration for a chatbot"""
    name: str
    description: Optional[str] = None
    system_prompt: str = "You are a helpful assistant for a service business."
    welcome_message: str = "Hello! How can I help you today?"
    primary_color: str = "#646cff"
    position: str = "bottom-right"
    enabled: bool = True
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 500


class Chatbot(BaseModel):
    """Chatbot model"""
    business_id: str
    config: ChatbotConfig
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatSession(BaseModel):
    """Chat session between a user and chatbot"""
    chatbot_id: str
    messages: List[ChatMessage] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat"""
    message: str
    session_id: str

