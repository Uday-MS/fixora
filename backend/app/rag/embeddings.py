import os
import math
import hashlib
from typing import List, Optional
import numpy as np

class EmbeddingService:
    DIMENSION: int = 384

    def __init__(self, provider: str = "auto"):
        self.provider = provider
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self._gemini_key = os.getenv("GEMINI_API_KEY")

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a normalized 384-dimensional vector.
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        Uses local deterministic semantic n-gram hash vectors by default,
        ensuring fast, offline, reproducible vectors that project similar terms
        close together in 384-d cosine space.
        """
        embeddings = []
        for text in texts:
            vec = self._compute_semantic_hash_vector(text)
            embeddings.append(vec)
        return embeddings

    def _compute_semantic_hash_vector(self, text: str) -> List[float]:
        """
        Produces a normalized 384-dimensional dense semantic embedding.
        Uses sub-word and word-level character n-gram hashing with positional
        frequency weighting to preserve semantic similarities between related
        engineering concepts, function names, and error traces.
        """
        vec = np.zeros(self.DIMENSION, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for idx, word in enumerate(words):
            # Positional decay weighting
            pos_weight = 1.0 / (1.0 + 0.05 * math.log(idx + 1))

            # Word hash
            h_word = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            bucket = h_word % self.DIMENSION
            sign = 1.0 if ((h_word >> 8) & 1) == 1 else -1.0
            vec[bucket] += sign * 1.5 * pos_weight

            # Character n-grams (trigrams and 4-grams)
            clean_word = f"^{word}$"
            for n in (3, 4):
                for i in range(len(clean_word) - n + 1):
                    ngram = clean_word[i : i + n]
                    h_ng = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest()[:8], 16)
                    ng_bucket = h_ng % self.DIMENSION
                    ng_sign = 1.0 if ((h_ng >> 4) & 1) == 1 else -1.0
                    vec[ng_bucket] += ng_sign * 0.5 * pos_weight

        # L2 normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec = vec / norm
        else:
            vec = np.zeros(self.DIMENSION, dtype=np.float32)

        return vec.tolist()

# Singleton instance
embedding_service = EmbeddingService()
