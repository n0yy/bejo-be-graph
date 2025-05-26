from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for handling user memory operations"""

    def __init__(self):
        self.memory = settings.memory

    def search_user_memory(self, query: str, user_id: str) -> str:
        """Search for relevant memories for a specific user"""
        try:
            search_result = self.memory.search(query=query, user_id=user_id)
            search_items = search_result.get("results", [])

            # Combine all relevant memories into one string
            user_memory = "\n".join(
                [item.get("memory", "") for item in search_items if item.get("memory")]
            )

            logger.info(f"Found {len(search_items)} memory items for user {user_id}")
            return user_memory

        except Exception as e:
            logger.error(f"Failed to search user memory: {e}")
            return ""

    def store_conversation(self, messages: List, user_id: str) -> bool:
        """Store conversation in user's memory"""
        try:
            # Convert messages to memory format
            memory_data = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    memory_data.append({"role": "user", "content": msg.content})
                # elif isinstance(msg, AIMessage):
                #     memory_data.append({"role": "assistant", "content": msg.content})

            self.memory.add(memory_data, user_id=user_id)
            logger.info(f"Stored conversation for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False


# Global memory service instance
memory_service = MemoryService()
