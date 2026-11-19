import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import settings

logger = logging.getLogger("fixora.rag.qdrant")

COLLECTION_NAME = "fixora_knowledge_chunks"
VECTOR_DIMENSION = 384

def to_valid_point_id(raw_id: Any) -> str:
    if isinstance(raw_id, int):
        return raw_id
    raw_str = str(raw_id)
    try:
        return str(uuid.UUID(raw_str))
    except (ValueError, AttributeError):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_str))

class QdrantVectorStore:
    def __init__(self):
        self.is_remote: bool = False
        self.client: QdrantClient = self._init_client()
        self._ensure_collection()

    def _init_client(self) -> QdrantClient:
        # Check if remote Qdrant connection is configured
        qdrant_url = getattr(settings, "QDRANT_URL", None)
        api_key = getattr(settings, "QDRANT_API_KEY", None)

        if qdrant_url and str(qdrant_url).strip():
            try:
                client = QdrantClient(url=qdrant_url, api_key=api_key, timeout=2.0)
                # Test connectivity
                client.get_collections()
                self.is_remote = True
                logger.info("Connected to remote Qdrant server at %s", qdrant_url)
                return client
            except Exception as e:
                logger.warning(
                    "Remote Qdrant unavailable (%s). Initializing in-memory vector store fallback.",
                    str(e),
                )
        else:
            logger.info("Remote QDRANT_URL not configured. Initializing in-memory vector store fallback.")

        self.is_remote = False
        return QdrantClient(":memory:")

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "connected (remote)" if self.is_remote else "in-memory (fallback active)",
            "persistent": self.is_remote,
            "mode": "remote" if self.is_remote else "in-memory",
            "description": (
                "Hosted Qdrant vector database"
                if self.is_remote
                else "Local in-memory vector store (ephemeral RAG fallback)"
            ),
        }

    def _ensure_collection(self):
        try:
            if not self.client.collection_exists(COLLECTION_NAME):
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_DIMENSION, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection: %s", COLLECTION_NAME)
        except Exception as e:
            logger.error("Failed to ensure collection: %s", str(e))

    def upsert_chunks(self, points: List[Dict[str, Any]]) -> int:
        if not points:
            return 0

        qdrant_points = []
        for p in points:
            raw_id = p.get("id") or str(uuid.uuid4())
            valid_id = to_valid_point_id(raw_id)
            payload = dict(p.get("payload", {}))
            if "chunkId" not in payload:
                payload["chunkId"] = str(raw_id)

            qdrant_points.append(
                PointStruct(
                    id=valid_id,
                    vector=p["vector"],
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=qdrant_points,
        )
        return len(qdrant_points)

    def search(
        self,
        query_vector: List[float],
        project_id: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        filter_conditions = []
        if project_id:
            filter_conditions.append(
                FieldCondition(key="projectId", match=MatchValue(value=project_id))
            )
        if source_type:
            filter_conditions.append(
                FieldCondition(key="sourceType", match=MatchValue(value=source_type))
            )

        query_filter = Filter(must=filter_conditions) if filter_conditions else None

        try:
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )

            hits = []
            for pt in results.points:
                payload = pt.payload or {}
                chunk_id = payload.get("chunkId", str(pt.id))
                hits.append({
                    "id": chunk_id,
                    "score": float(pt.score) if pt.score is not None else 0.0,
                    "payload": payload,
                })
            return hits
        except Exception as e:
            logger.error("Qdrant search error: %s", str(e))
            return []

    def count(self, project_id: Optional[str] = None) -> int:
        try:
            if project_id:
                res = self.client.count(
                    collection_name=COLLECTION_NAME,
                    count_filter=Filter(must=[FieldCondition(key="projectId", match=MatchValue(value=project_id))]),
                )
                return res.count
            res = self.client.count(collection_name=COLLECTION_NAME)
            return res.count
        except Exception:
            return 0

# Singleton instance
qdrant_store = QdrantVectorStore()
