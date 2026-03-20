"""
Unit tests for ML pipeline — no API keys needed.
"""
import pytest
from app.ml.pipeline import (
    extract_skills_with_ner,
    compute_gap_features,
    score_gaps,
    compute_resume_score,
    get_ordered_learning_path,
    _categorize_skill,
)


# ── Skill Extraction ─────────────────────────────────────────────────────────

def test_extract_known_skill():
    skills = extract_skills_with_ner("I have 3 years of Python experience")
    names = [s["name"].lower() for s in skills]
    assert "python" in names


def test_extract_multiple_skills():
    text = "Experienced in React, TypeScript, Docker, and AWS"
    skills = extract_skills_with_ner(text)
    names = [s["name"].lower() for s in skills]
    assert len(names) >= 3


def test_extract_frequency_boosts_confidence():
    text = "Python, Python, Python — we use Python everywhere"
    skills = extract_skills_with_ner(text)
    python = next((s for s in skills if s["name"].lower() == "python"), None)
    assert python is not None
    assert python["confidence"] > 70


def test_categorize_skill():
    assert _categorize_skill("python") == "Programming"
    assert _categorize_skill("react") == "Frontend"
    assert _categorize_skill("docker") == "Cloud & DevOps"
    assert _categorize_skill("machine learning") == "AI/ML"
    assert _categorize_skill("unknown_skill_xyz") == "General"


# ── Gap Scoring ──────────────────────────────────────────────────────────────

def test_gap_features_missing_skill():
    features = compute_gap_features("advanced", None, mention_count=3)
    assert features["raw_gap_score"] > 80


def test_gap_features_same_level():
    features = compute_gap_features("intermediate", "intermediate", mention_count=1)
    assert features["raw_gap_score"] < 10


def test_gap_features_partial_credit():
    # High embedding similarity should reduce gap even when skill is missing
    f_without = compute_gap_features("intermediate", None, embedding_similarity=0.0)
    f_with = compute_gap_features("intermediate", None, embedding_similarity=0.9)
    assert f_with["raw_gap_score"] < f_without["raw_gap_score"]


def test_score_gaps_basic():
    required = [
        {"name": "Python", "level": "advanced", "mention_count": 3, "category": "Programming"},
        {"name": "Docker", "level": "intermediate", "mention_count": 1, "category": "Cloud & DevOps"},
    ]
    candidate = [
        {"name": "Python", "level": "beginner"},
    ]
    gaps = score_gaps(required, candidate)
    # Python should have a gap (beginner vs advanced)
    python_gap = next((g for g in gaps if g["skill"] == "Python"), None)
    assert python_gap is not None
    assert python_gap["gap_score"] > 0


def test_score_gaps_met_skill_excluded():
    required = [{"name": "Python", "level": "intermediate", "mention_count": 1, "category": "Programming"}]
    candidate = [{"name": "Python", "level": "advanced"}]
    gaps = score_gaps(required, candidate)
    # Advanced candidate meets intermediate requirement — no gap
    assert len(gaps) == 0


# ── Resume Score ─────────────────────────────────────────────────────────────

def test_resume_score_range():
    required = [
        {"name": "Python", "level": "advanced", "mention_count": 2, "category": "Programming"},
        {"name": "Docker", "level": "intermediate", "mention_count": 1, "category": "DevOps"},
    ]
    gaps = [{"gap_score": 50, "estimated_days": 10}]
    result = compute_resume_score(gaps, required, overall_similarity=0.6)
    assert 0 <= result["score"] <= 100


def test_resume_score_no_gaps():
    required = [{"name": "Python", "level": "beginner", "mention_count": 1}]
    result = compute_resume_score([], required, overall_similarity=0.8)
    assert result["score"] > 60


# ── Learning Path Ordering ────────────────────────────────────────────────────

def test_topological_sort_respects_prerequisites():
    gaps = [
        {"skill": "Machine Learning", "gap_score": 80, "mention_count": 3, "estimated_days": 14, "category": "AI/ML", "required_level": "advanced", "candidate_level": None},
        {"skill": "Python", "gap_score": 60, "mention_count": 2, "estimated_days": 7, "category": "Programming", "required_level": "intermediate", "candidate_level": None},
    ]
    ordered = get_ordered_learning_path(gaps)
    names = [g["skill"] for g in ordered]
    # Python must come before Machine Learning
    assert names.index("Python") < names.index("Machine Learning")


def test_empty_gaps_returns_empty():
    assert get_ordered_learning_path([]) == []
