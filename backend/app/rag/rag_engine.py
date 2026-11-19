import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.rag.embeddings import embedding_service
from app.rag.qdrant_store import qdrant_store
from app.rag.bm25_index import bm25_index
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.reranker import cross_encoder_reranker
from app.rag.graph_rag import graph_rag
from app.rag.query_classifier import query_classifier
from app.rag.generator import rag_generator

class RAGEngine:
    def __init__(self):
        self._indexed_chunks: List[Dict[str, Any]] = []

    def index_document(
        self,
        document_id: str,
        project_id: str,
        title: str,
        source_type: str,
        file_path: Optional[str],
        content: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> int:
        """
        Chunk, embed, and index a document into both Qdrant (dense) and BM25 (sparse).
        """
        if not content.strip():
            return 0

        # Intelligent chunking
        raw_chunks = []
        words = content.split()
        if len(words) <= chunk_size:
            raw_chunks.append(content)
        else:
            step = chunk_size - chunk_overlap
            for i in range(0, len(words), step):
                chunk_text = " ".join(words[i : i + chunk_size])
                raw_chunks.append(chunk_text)

        points = []
        for idx, text in enumerate(raw_chunks):
            chunk_id = f"{document_id}_c{idx}"
            vector = embedding_service.embed_text(text)
            payload = {
                "chunkId": chunk_id,
                "documentId": document_id,
                "projectId": project_id,
                "title": title,
                "sourceType": source_type,
                "filePath": file_path or f"docs/{title.lower().replace(' ', '_')}.md",
                "text": text,
                "chunkIndex": idx,
            }
            point = {
                "id": chunk_id,
                "vector": vector,
                "payload": payload,
                "text": text,
            }
            points.append(point)
            self._indexed_chunks.append(point)

        # Upsert to Qdrant
        qdrant_store.upsert_chunks(points)

        # Update BM25 index
        bm25_index.index_chunks(self._indexed_chunks)

        return len(points)

    def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        source_type: Optional[str] = None,
        mode: str = "hybrid_rerank",  # dense, bm25, hybrid, hybrid_rerank
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Unified multi-modal retrieval.
        """
        if mode == "dense":
            q_vec = embedding_service.embed_text(query)
            return qdrant_store.search(
                query_vector=q_vec,
                project_id=project_id,
                source_type=source_type,
                limit=top_k,
            )
        elif mode == "bm25":
            return bm25_index.search(
                query=query,
                project_id=project_id,
                source_type=source_type,
                limit=top_k,
            )
        elif mode == "hybrid":
            return hybrid_retriever.retrieve(
                query=query,
                project_id=project_id,
                source_type=source_type,
                top_k=top_k,
            )
        else:
            # hybrid_rerank (default)
            candidates = hybrid_retriever.retrieve(
                query=query,
                project_id=project_id,
                source_type=source_type,
                top_k=max(15, top_k * 3),
            )
            return cross_encoder_reranker.rerank(
                query=query,
                candidates=candidates,
                top_k=top_k,
            )

    def ask(
        self,
        query: str,
        project_id: Optional[str] = None,
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """
        Full RAG Pipeline:
        Query Analysis -> Entity Extraction -> Hybrid Retrieval + Reranking -> GraphRAG Context -> Answer Generation.
        """
        # 1. Query Understanding
        analysis = query_classifier.analyze(query)
        entities = analysis.get("extractedEntities", [])

        # 2. GraphRAG context
        graph_context = graph_rag.query_graph_context(entities)

        # 3. Hybrid Retrieval + Cross-Encoder Reranking
        retrieved_chunks = self.search(
            query=query,
            project_id=project_id,
            source_type=analysis.get("suggestedSourceType"),
            mode="hybrid_rerank",
            top_k=top_k,
        )

        # 4. Synthesize Answer with Citations
        answer_result = rag_generator.generate_answer(
            query=query,
            retrieved_chunks=retrieved_chunks,
            graph_context=graph_context,
        )

        return {
            "query": query,
            "queryIntent": analysis["intent"],
            "detectedEntities": entities,
            "answer": answer_result["answer"],
            "evidence": answer_result["evidence"],
            "citations": answer_result["citations"],
            "graphContext": answer_result["graphContext"],
            "confidenceScore": answer_result["confidenceScore"],
            "isFaithful": answer_result["isFaithful"],
            "faithfulnessDetails": answer_result["faithfulnessDetails"],
            "recommendedNextSteps": answer_result["recommendedNextSteps"],
        }

# Singleton instance
rag_engine = RAGEngine()
