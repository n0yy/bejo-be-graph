from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from mem0 import Memory
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings:
    """Configuration settings for the BEJO chatbot"""

    def __init__(self):
        # Model configurations
        self.llm_model = "gemini-2.0-flash"
        self.embedding_model = "models/text-embedding-004"
        self.llm_temperature = 0.7
        self.qdrant_url = "http://localhost:6333"

        # Memory configuration
        self.memory_config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "memory",
                    "host": "localhost",
                    "port": 6333,
                    "embedding_model_dims": 768,
                },
            },
            "llm": {
                "provider": "gemini",
                "config": {
                    "model": self.llm_model,
                    "temperature": 0.2,
                    "max_tokens": 2000,
                },
            },
            "embedder": {
                "provider": "gemini",
                "config": {
                    "model": self.embedding_model,
                },
            },
        }

        self._init_models()

    def _init_models(self):
        """Initialize LLM, embeddings, and memory instances"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.llm_model, temperature=self.llm_temperature
            )
            self.embedding = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
            self.memory = Memory.from_config(self.memory_config)
            logger.info("Models and memory initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise


# Global settings instance
settings = Settings()
