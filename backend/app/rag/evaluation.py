import time
import math
from typing import List, Dict, Any, Callable

# Ground truth test dataset
EVALUATION_DATASET = [
    {
        "query": "How does the payment service process customer card charges?",
        "relevant_ids": ["doc_readme_payment", "doc_code_payment"],
        "target_entity": "payment-service",
    },
    {
        "query": "What are the remediation steps for stripe payment gateway timeout?",
        "relevant_ids": ["doc_runbook_stripe", "doc_incident_001"],
        "target_entity": "stripe",
    },
    {
        "query": "Which services depend on api-gateway and auth-service?",
        "relevant_ids": ["doc_arch_spec", "doc_readme_gateway"],
        "target_entity": "api-gateway",
    },
    {
        "query": "What caused the database connection pool exhaustion in incident inc_demo_001?",
        "relevant_ids": ["doc_incident_001", "doc_runbook_stripe"],
        "target_entity": "inc_demo_001",
    },
]

class RAGEvaluator:
    @staticmethod
    def compute_recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        top_k = set(retrieved_ids[:k])
        relevant_set = set(relevant_ids)
        if not relevant_set:
            return 1.0
        hits = len(top_k.intersection(relevant_set))
        return hits / len(relevant_set)

    @staticmethod
    def compute_precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        top_k = retrieved_ids[:k]
        if not top_k:
            return 0.0
        relevant_set = set(relevant_ids)
        hits = len(set(top_k).intersection(relevant_set))
        return hits / len(top_k)

    @staticmethod
    def compute_reciprocal_rank(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        relevant_set = set(relevant_ids)
        for rank, item_id in enumerate(retrieved_ids, start=1):
            if item_id in relevant_set:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def compute_ndcg_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        top_k = retrieved_ids[:k]
        relevant_set = set(relevant_ids)
        dcg = 0.0
        seen_relevant = set()
        for idx, item_id in enumerate(top_k):
            if item_id in relevant_set and item_id not in seen_relevant:
                seen_relevant.add(item_id)
                dcg += 1.0 / math.log2(idx + 2)

        # Ideal DCG
        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant_set), k)))
        if idcg <= 0.0:
            return 0.0
        return min(1.0, dcg / idcg)

    def evaluate_retriever(
        self,
        retriever_fn: Callable[[str], List[Dict[str, Any]]],
        dataset: List[Dict[str, Any]] = EVALUATION_DATASET,
        k: int = 3,
    ) -> Dict[str, Any]:
        recalls = []
        precisions = []
        mrr_scores = []
        ndcg_scores = []
        latencies = []

        for item in dataset:
            query = item["query"]
            relevant_ids = item["relevant_ids"]

            t0 = time.perf_counter()
            retrieved = retriever_fn(query)
            latency = (time.perf_counter() - t0) * 1000.0
            latencies.append(latency)

            retrieved_ids = []
            for r in retrieved:
                p_id = str(r.get("payload", {}).get("chunkId", "")) or str(r.get("id", ""))
                clean_id = p_id.split("_c")[0] if "_c" in p_id else p_id
                retrieved_ids.append(clean_id)

            recalls.append(self.compute_recall_at_k(retrieved_ids, relevant_ids, k=k))
            precisions.append(self.compute_precision_at_k(retrieved_ids, relevant_ids, k=k))
            mrr_scores.append(self.compute_reciprocal_rank(retrieved_ids, relevant_ids))
            ndcg_scores.append(self.compute_ndcg_at_k(retrieved_ids, relevant_ids, k=k))

        return {
            "k": k,
            "queriesEvaluated": len(dataset),
            "meanRecallAtK": round(sum(recalls) / len(recalls), 4),
            "meanPrecisionAtK": round(sum(precisions) / len(precisions), 4),
            "meanReciprocalRank": round(sum(mrr_scores) / len(mrr_scores), 4),
            "meanNdcgAtK": round(sum(ndcg_scores) / len(ndcg_scores), 4),
            "meanNDCGAtK": round(sum(ndcg_scores) / len(ndcg_scores), 4),
            "avgLatencyMs": round(sum(latencies) / len(latencies), 2),
        }

# Singleton instance
rag_evaluator = RAGEvaluator()
