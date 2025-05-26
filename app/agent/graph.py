from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.retrieval import retrieval_node
from app.agent.processing import processing_node
from app.agent.memory import memory_node


def create_agent_graph():
    """Create the BEJO agent workflow graph
    creates a pipeline that flows like:
    User Question → Retrieve Knowledge → Process with LLM → Store Memory → End

    """

    # Create the graph
    graph = StateGraph(AgentState)

    # Add processing nodes
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("processing", processing_node)
    graph.add_node("memory", memory_node)

    # Define the flow: START → retrieval → processing → memory → END
    graph.add_edge(START, "retrieval")
    graph.add_edge("retrieval", "processing")
    graph.add_edge("processing", "memory")
    graph.add_edge("memory", END)

    # Compile the graph into a runnable application
    app = graph.compile()

    return app


# Create the compiled graph instance
agent_app = create_agent_graph()
