"""
Skill Extractor — Pure ML, NO external API
Uses: TF-IDF vectorization + regex pattern matching + O*NET skill taxonomy
Dataset: Derived from O*NET 27.3 + Kaggle Resume Dataset

Algorithm:
1. Tokenize and normalize text
2. Match against SKILL_TAXONOMY (exact + alias matching)
3. Compute TF-IDF confidence scores
4. Infer experience level from context window
5. Extract years of experience via regex
"""
from __future__ import annotations
import re
import math
import logging
from collections import Counter
from app.ml.catalog import SKILL_TAXONOMY, ALIAS_TO_SKILL

logger = logging.getLogger(__name__)

# Level detection patterns (contextual)
LEVEL_PATTERNS = [
    (r'\b(expert|principal|architect|staff)\b', 'advanced'),
    (r'\b(senior|lead|advanced|expert)\b', 'advanced'),
    (r'\b(\d+\+?\s*years?)\b', 'intermediate'),   # "3+ years" → intermediate
    (r'\b(proficient|experienced|solid|strong)\b', 'intermediate'),
    (r'\b(intermediate|working knowledge|good understanding)\b', 'intermediate'),
    (r'\b(junior|entry.level|beginner|basic|familiar|exposure)\b', 'beginner'),
    (r'\b(learning|studying|coursework|academic)\b', 'beginner'),
]

YEARS_PATTERN = re.compile(r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience\s+(?:with|in|using)?\s*)?([a-z][a-z\s\./\+#]*)', re.IGNORECASE)

def _normalize(text: str) -> str:
    return re.sub(r'[^\w\s\./\+#\-]', ' ', text.lower())

def _compute_tfidf_confidence(skill: str, text: str, total_words: int) -> float:
    """TF-IDF style confidence: higher frequency + rarity = higher confidence."""
    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
    tf = len(re.findall(pattern, text.lower()))
    if tf == 0:
        return 0.0
    # IDF proxy: rarer skills (longer names) get higher weight
    idf = math.log(1 + len(skill.split()))
    tf_normalized = tf / max(total_words, 1) * 100
    confidence = min(95, 40 + tf_normalized * 20 + idf * 10)
    return round(confidence, 1)

def _infer_level(skill: str, text: str) -> str:
    """Look for level indicators in a 120-char window around the skill mention."""
    text_lower = text.lower()
    idx = text_lower.find(skill.lower())
    if idx == -1:
        return 'intermediate'
    window = text_lower[max(0, idx - 120): idx + 120]
    for pattern, level in LEVEL_PATTERNS:
        if re.search(pattern, window):
            return level
    return 'intermediate'

def _extract_experience_years(text: str) -> int:
    """Extract total years of experience from text."""
    # e.g., "5 years of experience", "3+ years in Python"
    matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', text, re.IGNORECASE)
    if matches:
        return max(int(m) for m in matches)
    return 0

def extract_skills(text: str) -> list[dict]:
    """
    Extract skills from text using taxonomy matching + TF-IDF confidence.
    Returns: [{name, level, category, confidence, frequency}]
    """
    if not text or len(text.strip()) < 10:
        return []

    normalized = _normalize(text)
    words = normalized.split()
    total_words = len(words)
    found: dict[str, dict] = {}

    # Pass 1: Direct skill name matching
    for skill_key, meta in SKILL_TAXONOMY.items():
        pattern = r'\b' + re.escape(skill_key) + r'\b'
        if re.search(pattern, normalized):
            freq = len(re.findall(pattern, normalized))
            confidence = _compute_tfidf_confidence(skill_key, normalized, total_words)
            level = _infer_level(skill_key, text)
            found[skill_key] = {
                "name": skill_key,
                "level": level,
                "category": meta["category"],
                "confidence": confidence,
                "frequency": freq,
            }

    # Pass 2: Alias matching (maps aliases to canonical skill name)
    for alias, canonical in ALIAS_TO_SKILL.items():
        if canonical in found:
            continue  # already found via direct match
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, normalized):
            meta = SKILL_TAXONOMY[canonical]
            freq = len(re.findall(pattern, normalized))
            confidence = _compute_tfidf_confidence(alias, normalized, total_words)
            level = _infer_level(alias, text)
            found[canonical] = {
                "name": canonical,
                "level": level,
                "category": meta["category"],
                "confidence": confidence,
                "frequency": freq,
            }

    # Pass 3: Years-based level upgrade
    # e.g., "3 years Python" → upgrade to intermediate
    for match in YEARS_PATTERN.finditer(text.lower()):
        years = int(match.group(1))
        skill_context = match.group(2).strip()
        for skill_key in found:
            if skill_key in skill_context or skill_context in skill_key:
                if years >= 4:
                    found[skill_key]["level"] = "advanced"
                elif years >= 2:
                    found[skill_key]["level"] = "intermediate"
                else:
                    found[skill_key]["level"] = "beginner"
                break

    return sorted(found.values(), key=lambda x: x["confidence"], reverse=True)


def extract_job_context(text: str) -> dict:
    """Extract job title, required experience years, and skills from JD."""
    # Job title detection
    title_patterns = [
        r'(?:position|role|job title|we are looking for|hiring a?n?)\s*:?\s*([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Analyst|Designer|Scientist|Architect|Lead|Director|Consultant|Specialist|Officer|Coordinator))',
        r'^([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Analyst|Designer|Scientist))',
    ]
    job_title = "Professional Role"
    for pattern in title_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            job_title = match.group(1).strip()
            break

    # Experience years required
    exp_matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:relevant\s+)?experience', text, re.IGNORECASE)
    exp_years = max((int(m) for m in exp_matches), default=0)

    # Extract skills with mention counts
    skills = extract_skills(text)

    # Count how many times each skill is mentioned (higher = more important in JD)
    normalized = _normalize(text)
    for skill in skills:
        pattern = r'\b' + re.escape(skill["name"]) + r'\b'
        skill["mention_count"] = len(re.findall(pattern, normalized))

    return {
        "job_title": job_title,
        "required_experience_years": exp_years,
        "required_skills": skills,
    }


def extract_resume_context(text: str) -> dict:
    """Extract candidate name, experience years, and skills from resume."""
    # Candidate name — usually first line
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    candidate_name = lines[0] if lines else "Candidate"

    exp_years = _extract_experience_years(text)
    skills = extract_skills(text)

    return {
        "candidate_name": candidate_name,
        "overall_experience_years": exp_years,
        "skills": skills,
    }
