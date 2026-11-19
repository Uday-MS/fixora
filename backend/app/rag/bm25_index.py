import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

class BM25KeywordIndex:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Code and documentation tokenizer.
        Splits on whitespace, punctuation, and splits CamelCase / snake_case tokens.
        """
        # Split on non-alphanumeric characters but keep dots and underscores in context
        tokens = re.findall(r"[A-Za-z0-9_\.]+", text.lower())
        sub_tokens = []
        for t in tokens:
            sub_tokens.append(t)
            # Split snake_case
            parts = t.split("_")
            if len(parts) > 1:
                sub_tokens.extend([p for p in parts if p])
            # Split dotted paths
            dot_parts = t.split(".")
            if len(dot_parts) > 1:
                sub_tokens.extend([p for p in dot_parts if p])
        return sub_tokens

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Index or re-index chunks for BM25 keyword search.
        Each chunk is a dict with at least 'id', 'text', and 'payload'.
        """
        self.chunks = list(chunks)
        self.tokenized_corpus = [
            self.tokenize(c.get("text", "") or c.get("payload", {}).get("text", ""))
            for c in self.chunks
        ]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        BM25 search with score ranking and metadata filtering.
        """
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self.tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        scored_results = []

        for idx, score in enumerate(scores):
            matches = any(t in self.tokenized_corpus[idx] for t in tokenized_query)
            if score <= 0.0 and not matches:
                continue
            effective_score = max(float(score), 0.2 if matches else 0.0)

            chunk = self.chunks[idx]
            payload = chunk.get("payload", {})

            # Filter conditions
            if project_id and payload.get("projectId") != project_id:
                continue
            if source_type and payload.get("sourceType") != source_type:
                continue

            scored_results.append({
                "id": chunk.get("id"),
                "score": effective_score,
                "payload": payload,
            })

        # Sort descending by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]

# Singleton instance
bm25_index = BM25KeywordIndex()
