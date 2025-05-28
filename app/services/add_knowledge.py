from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from uuid import uuid4
from dotenv import load_dotenv
import hashlib
import logging
import os

load_dotenv()
logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def add_knowledge(file_content: bytes, safe_filename: str, category_level: str):
    try:
        # STEP 1: CHECK: IF THE FILE NOT EXEIST THEN SAVE FILE (CONTUNIUE PROCESS) ELSE STOP PROCESS
        UPLOAD_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "uploads")
        )
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, safe_filename)
        url = f"{BASE_URL}/uploads/{safe_filename}"

        # STEP 1: CHECK IF FILE EXISTS
        if os.path.exists(filepath):
            yield {
                "step": "file_exists",
                "message": f"File '{safe_filename}' already exists. Process stopped.",
                "progress": 100,
                "filepath": filepath,
                "url": url,
                "stopped": True,
            }
            return

        # FILE DOES NOT EXIST - CONTINUE WITH SAVE PROCESS
        yield {"step": "saving_file", "message": "Saving file...", "progress": 10}

        # Validate file content
        if not file_content or len(file_content) == 0:
            yield {
                "step": "error",
                "message": "Uploaded file is empty or unreadable",
                "progress": 10,
                "error": True,
            }
            return

        # Save file
        try:
            with open(filepath, "wb") as f:
                f.write(file_content)

            yield {
                "step": "file_saved",
                "message": "File saved successfully",
                "progress": 50,
            }

        except Exception as e:
            yield {
                "step": "error",
                "message": f"Error saving file: {str(e)}",
                "progress": 25,
                "error": True,
            }
            return

        # Verify file was saved properly
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            yield {
                "step": "error",
                "message": "File was not saved properly",
                "progress": 15,
                "error": True,
            }
            return

        # STEP 2: INITIALIZE COMPONENTS
        yield {"step": "initializing", "message": "Initializing...", "progress": 30}

        try:
            embedding = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            converter = DocumentConverter()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            qdrant_client = QdrantClient(url="http://localhost:6333")
        except Exception as init_error:
            yield {
                "step": "error",
                "message": f"Failed to initialize components: {str(init_error)}",
                "progress": 30,
                "error": True,
            }
            return

        yield {"step": "component_ready", "message": "Component ready", "progress": 40}

        # STEP 3: CALCULATE HASH
        file_hash = compute_sha256(file_content)

        # STEP 4: CHECK FOR DUPLICATE
        collection_name = f"bejo-knowledge-level-{category_level}"
        try:
            existing = qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_hash", match=MatchValue(value=file_hash)
                        )
                    ]
                ),
                limit=1,
            )

            if existing and len(existing[0]) > 0:
                yield {
                    "step": "error",
                    "message": f"File already exists in collection (hash: {file_hash})",
                    "progress": 45,
                    "error": True,
                }
                return
        except Exception as check_error:
            pass  # Collection might not exist yet — continue

        # STEP 5: CONVERT DOCUMENT
        yield {"step": "converting", "message": "Converting...", "progress": 50}

        try:
            result = converter.convert(filepath).document
            document = Document(
                page_content=result.export_to_markdown(),
                metadata={
                    "source": url,
                    "filename": (
                        result.origin.filename if result.origin else safe_filename
                    ),
                    "mimetype": (
                        result.origin.mimetype
                        if result.origin
                        else "application/octet-stream"
                    ),
                    "category_level": category_level,
                    "file_hash": file_hash,
                },
            )
        except Exception as convert_error:
            yield {
                "step": "error",
                "message": f"Failed to convert document: {str(convert_error)}",
                "progress": 50,
                "error": True,
            }
            return

        yield {"step": "converted", "message": f"Document converted", "progress": 60}

        # STEP 6: SPLIT DOCUMENT
        yield {"step": "splitting", "message": "Chunking document...", "progress": 70}

        try:
            docs_splitted = splitter.split_documents([document])
        except Exception as split_error:
            yield {
                "step": "error",
                "message": f"Failed to split document: {str(split_error)}",
                "progress": 70,
                "error": True,
            }
            return

        yield {
            "step": "chunked",
            "message": f"Document chunked - Total: {len(docs_splitted)}",
            "progress": 80,
        }

        # STEP 7: VECTORIZE AND STORE
        yield {
            "step": "vectorizing",
            "message": "Vectorizing and storing in Qdrant...",
            "progress": 85,
        }

        try:
            try:
                qdrant = QdrantVectorStore(
                    client=qdrant_client,
                    embedding=embedding,
                    collection_name=collection_name,
                )
            except Exception:
                yield {
                    "step": "collection_not_found",
                    "message": f"Collection {collection_name} not found. Creating...",
                    "progress": 87,
                }

                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                qdrant = QdrantVectorStore(
                    client=qdrant_client,
                    embedding=embedding,
                    collection_name=collection_name,
                )

                yield {
                    "step": "collection_created",
                    "message": f"Collection {collection_name} created",
                    "progress": 90,
                }

        except Exception as collection_error:
            yield {
                "step": "error",
                "message": f"Failed to setup collection: {str(collection_error)}",
                "progress": 87,
                "error": True,
            }
            return

        try:
            uuids = [str(uuid4()) for _ in docs_splitted]
            qdrant.add_documents(docs_splitted, ids=uuids)

            yield {
                "step": "documents_added",
                "message": f"Added {len(docs_splitted)} chunks to {collection_name}",
                "progress": 95,
            }
        except Exception as add_error:
            yield {
                "step": "error",
                "message": f"Failed to add documents: {str(add_error)}",
                "progress": 95,
                "error": True,
            }
            return

        # STEP 8: COMPLETE
        yield {
            "step": "completed",
            "message": f"Successfully processed with {len(docs_splitted)} chunks",
            "progress": 100,
            "data": {
                "file_path": filepath,
                "url": url,
                "filename": safe_filename,
                "category_level": category_level,
                "chunks_count": len(docs_splitted),
                "collection_name": collection_name,
                "file_hash": file_hash,
            },
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield {
            "step": "error",
            "message": f"Unexpected error: {str(e)}",
            "progress": 0,
            "error": True,
        }
