"""
ML Pipeline - Fixed for Render (no spaCy dependency)
Uses sentence-transformers for embeddings only
"""
from __future__ import annotations
import logging
from functools import lru_cache
import numpy as np

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedder():
    """Load SentenceTransformer once and cache."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer loaded: all-MiniLM-L6-v2")
        return model
    except Exception as e:
        logger.warning(f"SentenceTransformer unavailable: {e}")
        return None


def compute_embedding_similarity(resume_text: str, jd_text: str) -> float:
    """
    Cosine similarity between resume and JD embeddings.
    Falls back to Jaccard similarity if model unavailable.
    """
    embedder = get_embedder()
    if embedder:
        try:
            embeddings = embedder.encode(
                [resume_text[:1000], jd_text[:1000]],
                normalize_embeddings=True
            )
            similarity = float(np.dot(embeddings[0], embeddings[1]))
            return round(max(0.0, min(1.0, similarity)), 3)
        except Exception as e:
            logger.warning(f"Embedding failed, using Jaccard: {e}")

    # Fallback: Jaccard similarity
    set_a = set(resume_text.lower().split())
    set_b = set(jd_text.lower().split())
    if not set_a or not set_b:
        return 0.0
    return round(len(set_a & set_b) / len(set_a | set_b), 3)


def embed_skill_list(skills: list) -> None:
    """Stub - embeddings handled by similarity function."""
    return None


def skill_similarity_matrix(resume_skills: list, jd_skills: list) -> dict:
    """Stub - not needed without spaCy pipeline."""
    return {}