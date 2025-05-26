from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from app.models.messages import ChatRequest, ChatResponse, HealthResponse
from app.agent.graph import agent_app
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for BEJO assistant"""

    try:
        # Create initial state for the agent
        initial_state = {
            "messages": [HumanMessage(content=request.input)],
            "input_tokens_usage": 0,
            "output_tokens_usage": 0,
            "total_tokens_usage": 0,
            "user_memory": "",
            "retrieved_knowledge": "",
            "category": request.category,
            "user_id": request.user_id,
        }

        # Run the agent workflow
        result = agent_app.invoke(initial_state)

        # Extract the response
        ai_response = result["messages"][-1].content

        logger.info(
            f"Processed request for user {request.user_id}, category {request.category}"
        )

        return ChatResponse(
            response=ai_response,
            input_tokens=result["input_tokens_usage"],
            output_tokens=result["output_tokens_usage"],
            total_tokens=result["total_tokens_usage"],
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing your request",
        )
