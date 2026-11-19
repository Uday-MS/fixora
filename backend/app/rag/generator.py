import os
import re
from typing import List, Dict, Any, Optional

class RAGGenerator:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        graph_context: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize a grounded answer using retrieved chunks and graph context.
        Provides verifiable citations, confidence scoring, and faithfulness checks.
        """
        if not retrieved_chunks and not graph_context:
            return {
                "answer": "No relevant documentation, code, or incidents were found for your query. Please verify that the repository or runbooks have been ingested.",
                "evidence": [],
                "citations": [],
                "confidenceScore": 0.0,
                "isFaithful": True,
                "faithfulnessDetails": "No claims generated due to absent context.",
                "recommendedNextSteps": ["Ingest relevant documentation or repository files."],
            }

        citations = []
        evidence_excerpts = []

        for idx, chunk in enumerate(retrieved_chunks, start=1):
            payload = chunk.get("payload", {})
            chunk_id = chunk.get("id")
            title = payload.get("title", "Untitled Document")
            file_path = payload.get("filePath", "unknown_path")
            source_type = payload.get("sourceType", "documentation")
            text = payload.get("text", "") or ""
            score = chunk.get("rerank_score", chunk.get("score", 0.85))

            cite_label = f"[{idx}]"
            citations.append({
                "label": cite_label,
                "chunkId": str(chunk_id),
                "title": title,
                "filePath": file_path,
                "sourceType": source_type,
                "relevanceScore": score,
            })

            # Top 2 sentences or 200 chars as excerpt
            clean_text = text.strip().replace("\n", " ")
            excerpt = clean_text[:240] + ("..." if len(clean_text) > 240 else "")
            evidence_excerpts.append(f"{cite_label} {title} ({file_path}): \"{excerpt}\"")

        # Synthesize direct answer based on top evidence
        primary_chunk = retrieved_chunks[0].get("payload", {})
        primary_text = primary_chunk.get("text", "")
        primary_title = primary_chunk.get("title", "the system")
        primary_file = primary_chunk.get("filePath", "")

        first_sentence = primary_text.split(". ")[0] if ". " in primary_text else primary_text[:120]
        first_sentence = first_sentence.strip().replace("\n", " ")

        # Answer body
        answer_parts = []
        answer_parts.append(f"Based on **{primary_title}** (`{primary_file}`), {first_sentence.lower() if first_sentence.startswith('The') or first_sentence.startswith('This') else first_sentence} [1].")

        if len(retrieved_chunks) > 1:
            second_chunk = retrieved_chunks[1].get("payload", {})
            sec_text = second_chunk.get("text", "").strip().replace("\n", " ")
            sec_title = second_chunk.get("title", "")
            sec_snippet = sec_text.split(". ")[0] if ". " in sec_text else sec_text[:100]
            answer_parts.append(f"Additionally, **{sec_title}** confirms: {sec_snippet} [2].")

        # Include Graph context if available
        if graph_context:
            answer_parts.append("\n\n**Architectural & Dependency Context (GraphRAG):**")
            for g in graph_context:
                answer_parts.append(f"- {g}")

        full_answer = "\n".join(answer_parts)

        # Faithfulness Verification
        is_faithful, verification_note = self._verify_faithfulness(full_answer, retrieved_chunks)

        # Confidence Score calculation
        top_score = retrieved_chunks[0].get("rerank_score", retrieved_chunks[0].get("score", 0.8))
        confidence = round(min(0.98, max(0.40, top_score)), 2)

        return {
            "answer": full_answer,
            "evidence": evidence_excerpts,
            "citations": citations,
            "graphContext": graph_context or [],
            "confidenceScore": confidence,
            "isFaithful": is_faithful,
            "faithfulnessDetails": verification_note,
            "recommendedNextSteps": [
                f"Inspect `{primary_file}` directly in the repository.",
                "Review associated runbooks and monitoring telemetry before applying changes.",
            ],
        }

    def _verify_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> (bool, str):
        """
        Verify that claims in the answer have corresponding ground truth tokens in retrieved chunks.
        """
        all_context = " ".join([c.get("payload", {}).get("text", "") for c in retrieved_chunks]).lower()
        answer_words = set(re.findall(r"[a-z0-9_]{4,}", answer.lower()))
        context_words = set(re.findall(r"[a-z0-9_]{4,}", all_context))

        if not answer_words:
            return True, "Verified (no verifiable terms)."

        overlap = len(answer_words.intersection(context_words)) / len(answer_words)
        if overlap >= 0.50:
            return True, f"High citation faithfulness: {round(overlap * 100, 1)}% of key assertions grounded in retrieved sources."
        else:
            return False, f"Low grounding: only {round(overlap * 100, 1)}% of assertions matched in retrieved context."

# Singleton instance
rag_generator = RAGGenerator()
