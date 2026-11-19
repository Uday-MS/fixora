from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.base import CamelModel

class KnowledgeDocumentBase(CamelModel):
    title: str
    source_type: str = "documentation"
    content: str
    file_path: Optional[str] = None
    chunk_count: int = 1
    status: str = "indexed"

class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    project_id: str

class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: str
    project_id: str
    indexed_at: datetime

class RAGSearchRequest(CamelModel):
    query: str
    project_id: Optional[str] = None
    mode: Optional[str] = "hybrid_rerank"  # dense, bm25, hybrid, hybrid_rerank
    top_k: Optional[int] = 5

class RAGSearchResult(CamelModel):
    id: str
    content: str
    source: str
    source_type: str
    relevance_score: float
    metadata: Dict[str, Any]

class CitationItem(CamelModel):
    label: str
    chunk_id: str
    title: str
    file_path: str
    source_type: str
    relevance_score: float

class RAGAskRequest(CamelModel):
    query: str
    project_id: Optional[str] = None
    top_k: Optional[int] = 4

class RAGAskResponse(CamelModel):
    query: str
    query_intent: str
    detected_entities: list[str]
    answer: str
    evidence: list[str]
    citations: list[CitationItem]
    graph_context: list[str]
    confidence_score: float
    is_faithful: bool
    faithfulness_details: str
    recommended_next_steps: list[str]

class RAGEvaluationMetrics(CamelModel):
    k: int
    queries_evaluated: int
    mean_recall_at_k: float
    mean_precision_at_k: float
    mean_reciprocal_rank: float
    mean_ndcg_at_k: float
    avg_latency_ms: float

class RAGEvaluationReport(CamelModel):
    dense_only: RAGEvaluationMetrics
    hybrid_rrf: RAGEvaluationMetrics
    hybrid_with_reranking: RAGEvaluationMetrics
    comparison_summary: str
