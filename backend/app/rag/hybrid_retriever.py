from typing import List, Dict, Any, Optional
from app.rag.embeddings import embedding_service
from app.rag.qdrant_store import qdrant_store
from app.rag.bm25_index import bm25_index

class HybridRetriever:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        project_id: Optional[str] = None,
        source_type: Optional[str] = None,
        top_k: int = 10,
        dense_limit: int = 25,
        bm25_limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Execute Hybrid Search combining Dense Vector Search & BM25 Keyword Search
        using Reciprocal Rank Fusion (RRF).
        """
        # 1. Dense retrieval via Qdrant
        query_vector = embedding_service.embed_text(query)
        dense_results = qdrant_store.search(
            query_vector=query_vector,
            project_id=project_id,
            source_type=source_type,
            limit=dense_limit,
        )

        # 2. BM25 retrieval
        bm25_results = bm25_index.search(
            query=query,
            project_id=project_id,
            source_type=source_type,
            limit=bm25_limit,
        )

        # 3. Reciprocal Rank Fusion
        fused_scores: Dict[str, float] = {}
        candidate_map: Dict[str, Dict[str, Any]] = {}
        provenance: Dict[str, Dict[str, int]] = {}

        # Dense ranks
        for rank, item in enumerate(dense_results, start=1):
            doc_id = str(item["id"])
            candidate_map[doc_id] = item
            provenance[doc_id] = {"dense_rank": rank, "bm25_rank": 0}
            fused_scores[doc_id] = 1.0 / (self.rrf_k + rank)

        # BM25 ranks
        for rank, item in enumerate(bm25_results, start=1):
            doc_id = str(item["id"])
            if doc_id not in candidate_map:
                candidate_map[doc_id] = item
                provenance[doc_id] = {"dense_rank": 0, "bm25_rank": rank}
                fused_scores[doc_id] = 1.0 / (self.rrf_k + rank)
            else:
                provenance[doc_id]["bm25_rank"] = rank
                fused_scores[doc_id] += 1.0 / (self.rrf_k + rank)

        # Sort by fused score descending
        sorted_doc_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

        final_candidates: List[Dict[str, Any]] = []
        for doc_id in sorted_doc_ids[:top_k]:
            candidate = candidate_map[doc_id]
            final_candidates.append({
                "id": doc_id,
                "score": round(fused_scores[doc_id], 5),
                "payload": candidate.get("payload", {}),
                "provenance": provenance[doc_id],
                "retrieval_method": "hybrid_rrf",
            })

        return final_candidates

# Singleton instance
hybrid_retriever = HybridRetriever()
