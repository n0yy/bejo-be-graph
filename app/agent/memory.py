from app.agent.state import AgentState
from app.services.memory import memory_service
import logging

logger = logging.getLogger(__name__)


def memory_node(state: AgentState) -> AgentState:
    """Store conversation to user's memory"""

    try:
        # Store the conversation in user's memory
        success = memory_service.store_conversation(
            messages=state["messages"], user_id=state["user_id"]
        )

        if success:
            logger.info(f"Successfully stored conversation for user {state['user_id']}")
        else:
            logger.warning(f"Failed to store conversation for user {state['user_id']}")

    except Exception as e:
        logger.error(f"Error in memory storage: {e}")

    return state
