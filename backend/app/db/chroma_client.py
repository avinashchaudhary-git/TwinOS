import os
from typing import Any

import chromadb

from app.core.config import settings
from app.core.logging import logger


class ChromaClientWrapper:
    """Wrapper managing the twinos_content collection in ChromaDB."""

    COLLECTION_NAME = "twinos_content"

    def __init__(self):
        self.client: Any | None = None
        self.collection: Any | None = None
        self._init_client()

    def _init_client(self):
        try:
            # Try connecting to remote HTTP Chroma service first
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            # Test connectivity
            self.client.heartbeat()
            logger.info(
                f"Connected to ChromaDB HTTP service at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}"
            )
        except Exception as e:
            logger.info(
                f"ChromaDB HTTP service not reachable ({e}). Falling back to local PersistentClient."
            )
            try:
                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            except Exception as pe:
                logger.warning(f"PersistentClient fallback failed ({pe}). Using EphemeralClient.")
                self.client = chromadb.EphemeralClient()

        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB collection '{self.COLLECTION_NAME}' ready.")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma collection: {e}")

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        embeddings: list[list[float]] | None = None,
    ):
        """Adds or updates documents in twinos_content collection."""
        if not self.collection:
            self._ensure_collection()
        if not ids:
            return

        kwargs: dict[str, Any] = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }
        if embeddings:
            kwargs["embeddings"] = embeddings

        self.collection.upsert(**kwargs)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Queries the vector store, strictly enforcing metadata filters (e.g. org_id)."""
        if not self.collection:
            self._ensure_collection()

        kwargs: dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        try:
            results = self.collection.query(**kwargs)
            return results
        except Exception as e:
            logger.error(f"ChromaDB query error: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    def count(self) -> int:
        if not self.collection:
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0


chroma_client = ChromaClientWrapper()
