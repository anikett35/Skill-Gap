"""
ML Pipeline for AI Adaptive Onboarding Engine v3

Replaces pure LLM prompts with:
  1. spaCy NER for skill extraction (with LLM fallback)
  2. Sentence Transformers for embedding-based matching
  3. Feature-engineered gap scoring (replaces hardcoded rules)
  4. Topological sort for learning path ordering
"""

from __future__ import annotations
import re
import logging
from typing import Optional
import numpy as np
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── Lazy-load heavy models ───────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_nlp():
    """Load spaCy model once and cache."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy NER model loaded")
        return nlp
    except Exception as e:
        logger.warning(f"spaCy unavailable: {e} — will use LLM extraction only")
        return None


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


# ── Known tech skill vocabulary for NER augmentation ────────────────────────

TECH_SKILLS_VOCAB = {
    "python", "javascript", "typescript", "java", "go", "rust", "c++", "c#",
    "react", "vue", "angular", "next.js", "svelte",
    "fastapi", "django", "flask", "express", "node.js",
    "tensorflow", "pytorch", "scikit-learn", "keras", "transformers",
    "docker", "kubernetes", "terraform", "ansible",
    "aws", "gcp", "azure", "vercel", "heroku",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "graphql", "rest", "grpc",
    "git", "ci/cd", "github actions", "jenkins",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data structures", "algorithms", "system design",
    "sql", "nosql", "data engineering", "spark", "kafka",
}

LEVEL_INDICATORS = {
    "expert": "advanced", "senior": "advanced", "lead": "advanced",
    "proficient": "intermediate", "experienced": "intermediate",
    "familiar": "beginner", "basic": "beginner", "beginner": "beginner",
    "intermediate": "intermediate", "advanced": "advanced",
}


# ── 1. SKILL EXTRACTION ──────────────────────────────────────────────────────

def extract_skills_with_ner(text: str) -> list[dict]:
    """
    Two-pass extraction:
      Pass 1 — spaCy NER for entity recognition
      Pass 2 — Vocabulary matching against known tech skills
    Returns list of {name, level, confidence, category}
    """
    found: dict[str, dict] = {}
    text_lower = text.lower()

    # Pass 1: spaCy NER
    nlp = get_nlp()
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            name_lower = ent.text.lower().strip()
            if name_lower in TECH_SKILLS_VOCAB:
                if name_lower not in found:
                    found[name_lower] = {
                        "name": ent.text.strip(),
                        "raw_name": name_lower,
                        "confidence": 70,
                        "source": "ner",
                    }

    # Pass 2: vocabulary matching (handles multi-word skills)
    for skill in TECH_SKILLS_VOCAB:
        # Use word-boundary aware regex
        pattern = r'\b' + re.escape(skill) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            freq = len(matches)
            if skill not in found:
                found[skill] = {
                    "name": skill.title(),
                    "raw_name": skill,
                    "confidence": min(50 + freq * 10, 95),
                    "source": "vocab",
                }
            else:
                # Boost confidence from frequency
                found[skill]["confidence"] = min(found[skill]["confidence"] + freq * 5, 95)
            found[skill]["frequency"] = freq

    # Infer experience level from surrounding context
    results = []
    for skill_key, skill_data in found.items():
        level = _infer_level(text_lower, skill_key)
        category = _categorize_skill(skill_key)
        results.append({
            "name": skill_data["name"],
            "level": level,
            "category": category,
            "confidence": skill_data["confidence"],
            "frequency": skill_data.get("frequency", 1),
        })

    return results


def _infer_level(text: str, skill: str) -> str:
    """Look for level indicators near a skill mention."""
    # Find the skill in context (±50 chars)
    idx = text.find(skill)
    if idx == -1:
        return "intermediate"
    context = text[max(0, idx - 50): idx + 50]
    for keyword, level in LEVEL_INDICATORS.items():
        if keyword in context:
            return level
    return "intermediate"


def _categorize_skill(skill: str) -> str:
    categories = {
        "Programming": {"python", "javascript", "typescript", "java", "go", "rust", "c++", "c#"},
        "Frontend": {"react", "vue", "angular", "next.js", "svelte", "html", "css"},
        "Backend": {"fastapi", "django", "flask", "express", "node.js", "graphql", "rest", "grpc"},
        "AI/ML": {"tensorflow", "pytorch", "scikit-learn", "keras", "transformers",
                  "machine learning", "deep learning", "nlp", "computer vision"},
        "Cloud & DevOps": {"docker", "kubernetes", "terraform", "aws", "gcp", "azure",
                           "ci/cd", "github actions", "jenkins"},
        "Database": {"postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sql", "nosql"},
        "Data Engineering": {"spark", "kafka", "data engineering"},
        "CS Fundamentals": {"data structures", "algorithms", "system design"},
    }
    for cat, skills in categories.items():
        if skill.lower() in skills:
            return cat
    return "General"


# ── 2. EMBEDDING-BASED SIMILARITY ───────────────────────────────────────────

def compute_embedding_similarity(resume_text: str, jd_text: str) -> float:
    """
    Cosine similarity between resume and JD embeddings.
    Returns 0.0–1.0 (1.0 = perfect match).
    Falls back to keyword-overlap if model unavailable.
    """
    embedder = get_embedder()
    if embedder:
        embeddings = embedder.encode([resume_text, jd_text], normalize_embeddings=True)
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        return round(max(0.0, min(1.0, similarity)), 3)
    else:
        # Fallback: Jaccard similarity on word tokens
        set_a = set(resume_text.lower().split())
        set_b = set(jd_text.lower().split())
        if not set_a or not set_b:
            return 0.0
        return round(len(set_a & set_b) / len(set_a | set_b), 3)


def embed_skill_list(skills: list[str]) -> Optional[np.ndarray]:
    """Return embeddings matrix for a list of skill names."""
    embedder = get_embedder()
    if not embedder or not skills:
        return None
    return embedder.encode(skills, normalize_embeddings=True)


def skill_similarity_matrix(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """
    For each JD skill, find the best matching resume skill by cosine similarity.
    Returns {jd_skill: {best_match: str, score: float}}
    """
    embedder = get_embedder()
    if not embedder:
        return {}

    resume_embeddings = embedder.encode(resume_skills, normalize_embeddings=True)
    jd_embeddings = embedder.encode(jd_skills, normalize_embeddings=True)

    result = {}
    for i, jd_skill in enumerate(jd_skills):
        scores = np.dot(resume_embeddings, jd_embeddings[i])
        best_idx = int(np.argmax(scores))
        result[jd_skill] = {
            "best_match": resume_skills[best_idx],
            "score": round(float(scores[best_idx]), 3),
        }
    return result


# ── 3. GAP SCORING MODEL ─────────────────────────────────────────────────────

LEVEL_MAP = {"beginner": 1, "intermediate": 2, "advanced": 3}


def compute_gap_features(
    required_level: str,
    candidate_level: Optional[str],
    mention_count: int = 1,
    embedding_similarity: float = 0.0,
) -> dict:
    """
    Feature engineering for gap scoring:
      - level_gap: normalized 0–1 level difference
      - frequency_weight: log-scaled mention frequency
      - context_similarity: embedding-based partial credit
    """
    req = LEVEL_MAP.get(required_level.lower(), 2)
    cand = LEVEL_MAP.get((candidate_level or "").lower(), 0)

    level_gap = max(0.0, (req - cand) / req) if req > 0 else 0.0

    # Frequency weight: more JD mentions = higher priority
    import math
    freq_weight = math.log1p(mention_count) / math.log1p(10)  # normalized 0–1

    # Embedding similarity provides partial credit even for renamed skills
    partial_credit = embedding_similarity * 0.3  # max 30% credit from similarity

    raw_gap = max(0.0, level_gap - partial_credit)

    return {
        "level_gap": round(level_gap, 3),
        "freq_weight": round(freq_weight, 3),
        "similarity_credit": round(partial_credit, 3),
        "raw_gap_score": round(raw_gap * 100, 1),
    }


def score_gaps(
    required_skills: list[dict],
    candidate_skills: list[dict],
    similarity_matrix: dict = None,
) -> list[dict]:
    """
    Main gap scoring function.
    Combines rule-based levels + embedding similarity for accurate scoring.
    """
    candidate_map = {s["name"].lower(): s for s in candidate_skills}
    similarity_matrix = similarity_matrix or {}
    gaps = []

    for req_skill in required_skills:
        name_lower = req_skill["name"].lower()
        match = candidate_map.get(name_lower)
        candidate_level = match["level"] if match else None

        # Get embedding similarity for this skill
        sim_data = similarity_matrix.get(req_skill["name"], {})
        emb_score = sim_data.get("score", 0.0) if (not match) else 1.0

        features = compute_gap_features(
            required_level=req_skill.get("level", "intermediate"),
            candidate_level=candidate_level,
            mention_count=req_skill.get("mention_count", 1),
            embedding_similarity=emb_score,
        )

        gap_score = features["raw_gap_score"]

        if gap_score > 5:  # Only include meaningful gaps
            # Learning time estimate based on gap severity
            days = _estimate_days(gap_score)
            gaps.append({
                "skill": req_skill["name"],
                "category": req_skill.get("category", "General"),
                "required_level": req_skill.get("level", "intermediate"),
                "candidate_level": candidate_level,
                "gap_score": gap_score,
                "mention_count": req_skill.get("mention_count", 1),
                "embedding_match": sim_data.get("best_match"),
                "embedding_score": sim_data.get("score", 0.0),
                "estimated_days": days,
                "features": features,
            })

    gaps.sort(key=lambda x: (x["gap_score"] * x["mention_count"]), reverse=True)
    return gaps


def _estimate_days(gap_score: float) -> int:
    if gap_score >= 90:
        return 21  # ~3 weeks
    elif gap_score >= 70:
        return 14  # ~2 weeks
    elif gap_score >= 50:
        return 10
    elif gap_score >= 30:
        return 5
    else:
        return 2


# ── 4. RESUME SCORE (0–100) ──────────────────────────────────────────────────

def compute_resume_score(
    skill_gaps: list[dict],
    required_skills: list[dict],
    overall_similarity: float,
) -> dict:
    """
    Composite resume score:
      - Skills match rate (40%)
    - Level adequacy (30%)
    - Embedding similarity (20%)
    - Coverage breadth (10%)
    """
    total = len(required_skills)
    if total == 0:
        return {"score": 0, "breakdown": {}}

    # Skills match rate
    matched = sum(1 for g in skill_gaps if g["gap_score"] < 50)
    fully_met = total - len(skill_gaps)
    match_rate = (fully_met + matched * 0.5) / total

    # Level adequacy: average (1 - gap_score/100)
    avg_gap = sum(g["gap_score"] for g in skill_gaps) / max(len(skill_gaps), 1)
    level_adequacy = max(0.0, 1 - avg_gap / 100)

    # Weighted composite
    score = (
        match_rate * 40 +
        level_adequacy * 30 +
        overall_similarity * 20 +
        min(fully_met / total, 1.0) * 10
    )

    return {
        "score": round(min(score, 100), 1),
        "breakdown": {
            "skills_match": round(match_rate * 40, 1),
            "level_adequacy": round(level_adequacy * 30, 1),
            "semantic_match": round(overall_similarity * 20, 1),
            "coverage": round(min(fully_met / total, 1.0) * 10, 1),
        },
    }


# ── 5. LEARNING PATH — DEPENDENCY GRAPH + TOPOLOGICAL SORT ──────────────────

SKILL_PREREQUISITES = {
    "Machine Learning": ["Python", "Statistics"],
    "Deep Learning": ["Machine Learning", "Python", "TensorFlow"],
    "TensorFlow": ["Python"],
    "PyTorch": ["Python"],
    "React": ["JavaScript", "HTML/CSS"],
    "Next.js": ["React", "JavaScript"],
    "FastAPI": ["Python"],
    "Docker": ["Linux Basics"],
    "Kubernetes": ["Docker"],
    "AWS": ["Linux Basics"],
    "GraphQL": ["REST", "JavaScript"],
    "PostgreSQL": ["SQL"],
    "MongoDB": ["NoSQL Concepts"],
    "Spark": ["Python", "SQL"],
    "Kafka": ["Linux Basics"],
    "System Design": ["Databases", "Networking Basics"],
    "Algorithms": ["Data Structures"],
}


def get_ordered_learning_path(skill_gaps: list[dict]) -> list[dict]:
    """
    Topological sort of skills respecting dependency graph.
    Higher priority = higher gap_score × mention_count.
    """
    skill_names = [g["skill"] for g in skill_gaps]
    skill_map = {g["skill"]: g for g in skill_gaps}

    # Build adjacency: skill → prerequisite skills in the gap list
    in_deps: dict[str, set] = {s: set() for s in skill_names}
    for skill in skill_names:
        prereqs = SKILL_PREREQUISITES.get(skill, [])
        for p in prereqs:
            if p in skill_map:  # only if prereq is also a gap
                in_deps[skill].add(p)

    # Kahn's algorithm for topological sort with priority tie-breaking
    ready = sorted(
        [s for s, deps in in_deps.items() if len(deps) == 0],
        key=lambda s: -(skill_map[s]["gap_score"] * skill_map[s].get("mention_count", 1)),
    )
    order = []

    while ready:
        node = ready.pop(0)
        order.append(node)
        for s, deps in in_deps.items():
            if node in deps:
                deps.discard(node)
                if len(deps) == 0 and s not in order:
                    ready.append(s)
                    ready.sort(key=lambda x: -(skill_map[x]["gap_score"] * skill_map[x].get("mention_count", 1)))

    # Append any remaining (cycles shouldn't exist but just in case)
    remaining = [s for s in skill_names if s not in order]
    order.extend(remaining)

    return [skill_map[s] for s in order if s in skill_map]
