from langchain_qdrant import QdrantVectorStore
from app.agent.state import AgentState
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


def retrieval_node(state: AgentState) -> AgentState:
    """Retrieve relevant knowledge based on user category

    Think of this like having different levels of library access:
    - Category 1: Basic books only
    - Category 2: Basic + Intermediate books
    - Category 3: Basic + Intermediate + Advanced books
    - Category 4: All books including Expert level

    Higher category users get access to more detailed information.
    """
    category = state["category"]

    # Define knowledge levels based on user category
    collection_mapping = {
        4: [
            "bejo-knowledge-level-4",
            "bejo-knowledge-level-3",
            "bejo-knowledge-level-2",
            "bejo-knowledge-level-1",
        ],
        3: [
            "bejo-knowledge-level-3",
            "bejo-knowledge-level-2",
            "bejo-knowledge-level-1",
        ],
        2: ["bejo-knowledge-level-2", "bejo-knowledge-level-1"],
        1: ["bejo-knowledge-level-1"],
    }

    collection_names = collection_mapping.get(category, ["bejo-knowledge-level-1"])
    all_results = []

    # Search each accessible knowledge collection
    for collection_name in collection_names:
        try:
            qdrant = QdrantVectorStore.from_existing_collection(
                embedding=settings.embedding,
                collection_name=collection_name,
                url=settings.qdrant_url,
            )

            # Search for relevant documents (top 2 from each collection)
            results = qdrant.similarity_search(state["messages"][-1].content, k=2)
            all_results.extend(results)

            logger.info(f"Retrieved {len(results)} documents from {collection_name}")

        except Exception as e:
            logger.warning(f"Failed to query {collection_name}: {e}")

    # Combine all retrieved knowledge into one string
    retrieved_knowledge = "\n\n".join(
        [
            f"{doc.page_content}\n(Source: {doc.metadata.get('source', 'unknown')})"
            for doc in all_results
        ]
    )

    if not retrieved_knowledge:
        retrieved_knowledge = (
            "I'm sorry, I don't have any relevant information for your question."
        )

    # Remove duplicates
    retrieved_knowledge = "\n\n".join(set(retrieved_knowledge.split("\n\n")))

    print(retrieved_knowledge)

    state["retrieved_knowledge"] = retrieved_knowledge
    logger.info(f"Total retrieved documents: {len(all_results)}")

    return state
