import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.rag.embeddings import embedding_service
from app.rag.qdrant_store import qdrant_store
from app.rag.bm25_index import bm25_index
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.reranker import cross_encoder_reranker
from app.rag.graph_rag import graph_rag
from app.rag.query_classifier import query_classifier
from app.rag.generator import rag_generator
from app.rag.rag_engine import rag_engine
from app.rag.evaluation import rag_evaluator

def test_embeddings_generation():
    vec1 = embedding_service.embed_text("Database connection timeout in payment gateway")
    vec2 = embedding_service.embed_text("Payment service database connection timeout")
    vec3 = embedding_service.embed_text("Frontend button color CSS styling")

    assert len(vec1) == 384
    # Unit norm test
    assert np.isclose(np.linalg.norm(vec1), 1.0, atol=1e-3)

    # Cosine similarity between related texts should be higher than unrelated
    sim_related = np.dot(vec1, vec2)
    sim_unrelated = np.dot(vec1, vec3)
    assert sim_related > sim_unrelated

def test_qdrant_vector_store():
    test_points = [
        {
            "id": "chunk_test_1",
            "vector": embedding_service.embed_text("Stripe payment processing retry logic"),
            "payload": {
                "projectId": "proj_demo_001",
                "sourceType": "runbook",
                "title": "Stripe Retry Runbook",
                "text": "Stripe payment processing retry logic with exponential backoff.",
            },
        },
        {
            "id": "chunk_test_2",
            "vector": embedding_service.embed_text("Authentication JWT token refresh mechanism"),
            "payload": {
                "projectId": "proj_demo_001",
                "sourceType": "documentation",
                "title": "Auth Architecture",
                "text": "Authentication JWT token refresh mechanism.",
            },
        },
    ]
    upserted = qdrant_store.upsert_chunks(test_points)
    assert upserted == 2

    # Search with filter
    q_vec = embedding_service.embed_text("retry logic stripe")
    results = qdrant_store.search(
        query_vector=q_vec,
        project_id="proj_demo_001",
        source_type="runbook",
        limit=5,
    )
    assert len(results) >= 1
    assert results[0]["payload"]["sourceType"] == "runbook"

def test_bm25_keyword_index():
    chunks = [
        {
            "id": "bm25_1",
            "text": "func ProcessTransaction(ctx context.Context, chargeReq *ChargeRequest) (*ChargeResponse, error)",
            "payload": {"title": "Transaction Processor", "sourceType": "code", "projectId": "proj_demo_001"},
        },
        {
            "id": "bm25_2",
            "text": "Redis cluster cache eviction policy and TTL configuration",
            "payload": {"title": "Redis Config", "sourceType": "documentation", "projectId": "proj_demo_001"},
        },
    ]
    bm25_index.index_chunks(chunks)
    res = bm25_index.search("ProcessTransaction ChargeRequest", project_id="proj_demo_001", limit=2)
    assert len(res) >= 1
    assert res[0]["id"] == "bm25_1"

def test_hybrid_retrieval_and_rrf():
    # Retrieve using hybrid fusion
    results = hybrid_retriever.retrieve(
        query="payment transaction processing",
        project_id="proj_demo_001",
        top_k=5,
    )
    assert len(results) >= 1
    top_hit = results[0]
    assert "score" in top_hit
    assert "provenance" in top_hit
    assert top_hit["retrieval_method"] == "hybrid_rrf"

def test_cross_encoder_reranker():
    candidates = [
        {
            "id": "cand_1",
            "score": 0.03,
            "payload": {
                "title": "CSS Styling",
                "filePath": "src/styles.css",
                "text": "Button styles and layout flexbox.",
            },
        },
        {
            "id": "cand_2",
            "score": 0.02,
            "payload": {
                "title": "Payment Gateway Timeout",
                "filePath": "runbooks/payment_gateway_timeout.md",
                "text": "Remediation steps for payment gateway timeout surge. Scale payment pods.",
            },
        },
    ]
    reranked = cross_encoder_reranker.rerank(
        query="payment gateway timeout",
        candidates=candidates,
        top_k=2,
    )
    assert len(reranked) == 2
    # The payment gateway timeout document should be reranked to top
    assert reranked[0]["id"] == "cand_2"
    assert reranked[0]["rerank_score"] > reranked[1]["rerank_score"]

def test_graph_rag_topology():
    deps = graph_rag.get_service_dependencies("payment-service")
    assert "postgres-cluster" in deps["downstreamDependencies"]
    assert "api-gateway" in deps["upstreamCallers"]

    blast = graph_rag.get_incident_blast_radius("inc_demo_001")
    assert "payment-service" in blast["affectedServices"]
    assert "c48a92f" in blast["linkedCommits"]

    ctx = graph_rag.query_graph_context(["payment-service", "inc_demo_001"])
    assert len(ctx) >= 1
    assert any("payment-service" in line for line in ctx)

def test_query_classifier():
    c_res = query_classifier.analyze("Where is ChargeCustomerCard defined in payment-service?")
    assert c_res["intent"] == "code"
    assert "payment-service" in c_res["extractedEntities"]

    inc_res = query_classifier.analyze("What was the root cause of incident inc_demo_001?")
    assert inc_res["intent"] == "incident"
    assert "inc_demo_001" in inc_res["extractedEntities"]

    dep_res = query_classifier.analyze("Which upstream services depend on auth-service?")
    assert dep_res["intent"] == "dependency"
    assert "auth-service" in dep_res["extractedEntities"]

@pytest.mark.asyncio
async def test_rag_end_to_end_ask_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Ingest a real runbook document
        doc_upload = await ac.post(
            "/api/knowledge/upload",
            data={"projectId": "proj_demo_001", "sourceType": "runbook"},
            files={"file": ("payment_runbook.md", b"# Stripe Payment Runbook\n\nWhen payment gateway latency spikes, verify database connection pool saturation. Scale payment-service replicas to 5.", "text/markdown")},
        )
        assert doc_upload.status_code == 200

        # Ask question via /api/knowledge/ask
        ask_res = await ac.post("/api/knowledge/ask", json={
            "query": "What should be done when payment gateway latency spikes?",
            "projectId": "proj_demo_001",
            "topK": 3
        })
        assert ask_res.status_code == 200
        data = ask_res.json()["data"]

        assert "answer" in data
        assert len(data["citations"]) >= 1
        assert data["confidenceScore"] > 0.0
        assert data["isFaithful"] is True
        assert len(data["recommendedNextSteps"]) >= 1

@pytest.mark.asyncio
async def test_rag_evaluation_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/knowledge/evaluation")
        assert res.status_code == 200
        report = res.json()["data"]

        assert "denseOnly" in report
        assert "hybridRrf" in report
        assert "hybridWithReranking" in report

        rerank = report["hybridWithReranking"]
        assert rerank["queriesEvaluated"] >= 4
        assert rerank["meanRecallAtK"] > 0.0
        assert rerank["meanReciprocalRank"] > 0.0
        assert rerank["meanNdcgAtK"] > 0.0
        assert "comparisonSummary" in report
