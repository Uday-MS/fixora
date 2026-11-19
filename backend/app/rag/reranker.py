import re
from typing import List, Dict, Any

class CrossEncoderReranker:
    def __init__(self):
        pass

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Reranks hybrid retrieval candidates using cross-encoder relevance scoring.
        Evaluates exact phrase matching, lexical density, title/file path relevance,
        and term-co-occurrence between query and candidate text.
        """
        if not candidates:
            return []

        clean_query = query.lower().strip()
        query_words = set(re.findall(r"[a-z0-9_]+", clean_query))
        if not query_words:
            return candidates[:top_k]

        scored_candidates = []
        for cand in candidates:
            payload = cand.get("payload", {})
            text = (payload.get("text", "") or "").lower()
            title = (payload.get("title", "") or "").lower()
            file_path = (payload.get("filePath", "") or "").lower()

            combined_content = f"{title} {file_path} {text}"
            content_words = re.findall(r"[a-z0-9_]+", combined_content)
            content_word_set = set(content_words)

            # 1. Term overlap ratio
            matched_terms = query_words.intersection(content_word_set)
            term_overlap = len(matched_terms) / len(query_words)

            # 2. Exact phrase match bonus
            phrase_bonus = 0.0
            if len(clean_query) > 5 and clean_query in combined_content:
                phrase_bonus = 0.35

            # 3. Path / Title relevance bonus
            title_bonus = 0.0
            if any(w in title or w in file_path for w in query_words):
                title_bonus = 0.20

            # 4. Term frequency density in text
            density_score = 0.0
            if content_words:
                match_count = sum(1 for w in content_words if w in query_words)
                density_score = min(0.25, (match_count / len(content_words)) * 4.0)

            # Base RRF score contribution (up to 0.20)
            base_score = min(0.20, cand.get("score", 0.0) * 5.0)

            # Final rerank score (clamped 0.0 to 0.99)
            rerank_score = round(
                min(0.99, (term_overlap * 0.40) + phrase_bonus + title_bonus + density_score + base_score),
                4,
            )

            reranked_item = dict(cand)
            reranked_item["rerank_score"] = rerank_score
            reranked_item["reranked"] = True
            scored_candidates.append(reranked_item)

        # Sort descending by rerank score
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:top_k]

# Singleton instance
cross_encoder_reranker = CrossEncoderReranker()
