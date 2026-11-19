from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.knowledge import (
    KnowledgeDocumentResponse,
    RAGSearchRequest,
    RAGSearchResult,
    RAGAskRequest,
    RAGAskResponse,
    RAGEvaluationReport,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter()

@router.get("/documents", response_model=PaginatedResponse[KnowledgeDocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    docs = await KnowledgeService.list_documents(db)
    items = [KnowledgeDocumentResponse.model_validate(d) for d in docs]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("/search", response_model=ApiResponse[List[RAGSearchResult]])
async def rag_search(req: RAGSearchRequest, db: AsyncSession = Depends(get_db)):
    results = await KnowledgeService.search(
        db=db,
        query=req.query,
        project_id=req.project_id,
        mode=req.mode or "hybrid_rerank",
        top_k=req.top_k or 5,
    )
    return ApiResponse(data=[RAGSearchResult.model_validate(r) for r in results])

@router.post("/ask", response_model=ApiResponse[RAGAskResponse])
async def rag_ask(req: RAGAskRequest, db: AsyncSession = Depends(get_db)):
    answer_dict = await KnowledgeService.ask(
        db=db,
        query=req.query,
        project_id=req.project_id,
        top_k=req.top_k or 4,
    )
    return ApiResponse(data=RAGAskResponse.model_validate(answer_dict))

@router.get("/evaluation", response_model=ApiResponse[RAGEvaluationReport])
async def rag_evaluation():
    report = KnowledgeService.evaluate()
    return ApiResponse(data=RAGEvaluationReport.model_validate(report))
