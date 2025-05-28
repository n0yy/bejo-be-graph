from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    input: str = Field(..., description="User's question or message")
    category: int = Field(..., ge=1, le=4, description="User category level (1-4)")
    user_id: str = Field(..., description="Unique identifier for the user")
    thread_id: str = Field(..., description="unique identifier for the session")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    response: str = Field(..., description="BEJO's response to the user")
    input_tokens: int = Field(..., description="Number of input tokens used")
    output_tokens: int = Field(..., description="Number of output tokens used")
    total_tokens: int = Field(..., description="Total tokens used")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    message: str = "BEJO chatbot is running"
