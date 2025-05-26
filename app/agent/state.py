from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage


class AgentState(TypedDict):
    """State definition for the BEJO agent workflow"""

    messages: List[Union[HumanMessage, AIMessage]]
    input_tokens_usage: int
    output_tokens_usage: int
    total_tokens_usage: int
    user_memory: str
    retrieved_knowledge: str
    category: int
    user_id: str
