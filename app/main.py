from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from app.routes.chat import router as chat_router
from app.routes.uploads import router as upload_router
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("BEJO Chatbot API is starting up...")
    yield
    logger.info("BEJO Chatbot API is shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="BEJO Chatbot API",
    description="Intelligent assistant for internal operations with memory and knowledge retrieval",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Add route
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(upload_router, prefix="/api/v1", tags=["uploads"])
