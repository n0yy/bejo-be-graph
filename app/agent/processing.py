from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agent.state import AgentState
from app.services.memory import memory_service
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


def processing_node(state: AgentState) -> AgentState:
    """Process user input with LLM using memory and knowledge

    This is like having a conversation with someone who:
    1. Remembers your previous conversations (user memory)
    2. Has access to a knowledge database (retrieved knowledge)
    3. Can give thoughtful responses based on both
    """

    # Get user's personal memory
    user_memory = memory_service.search_user_memory(
        query=state["messages"][-1].content, user_id=state["user_id"]
    )
    state["user_memory"] = user_memory

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are Bejo, an assistant that is helpful, friendly, and informative 😊.\n"
                "If the information is not available or not clearly stated, respond politely that you do not have enough data to answer.\n\n"
                "Here is some relevant memory of the user:\n{user_memory}\n\n"
                "### Supporting Knowledge:\n"
                "Use this reference **only if it's relevant** to the user's question.\n"
                "When using this knowledge, **always mention the source** by referencing the provided (Source: ...) in your response:\n"
                "------------------\n"
                "{retrieved_knowledge}\n"
                "------------------\n\n"
                "Strictly avoid making assumptions or hallucinating information. Always ensure your responses are factual and based on the data above.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Format the prompt with context
    prompt_messages = prompt.format_messages(
        messages=state["messages"],
        user_memory=state["user_memory"],
        retrieved_knowledge=state["retrieved_knowledge"],
    )

    try:
        result = settings.llm.invoke(prompt_messages)
        response = result.content

        usage = getattr(result, "usage_metadata", None) or {}
        state["input_tokens_usage"] += usage.get("input_tokens", 0)
        state["output_tokens_usage"] += usage.get("output_tokens", 0)
        state["total_tokens_usage"] += usage.get("total_tokens", 0)

        logger.info(
            f"[Token Usage] Input: {usage.get('input_tokens', 0)} | "
            f"Output: {usage.get('output_tokens', 0)} | "
            f"Total: {usage.get('total_tokens', 0)}"
        )

    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        response = "Maaf, saya mengalami kesulitan dalam menjawab. Silakan coba lagi."
        # Set default usage values when error occurs
        state["input_tokens_usage"] += 0
        state["output_tokens_usage"] += 0
        state["total_tokens_usage"] += 0

    # Add AI response to conversation
    state["messages"].append(AIMessage(content=response))

    return state
