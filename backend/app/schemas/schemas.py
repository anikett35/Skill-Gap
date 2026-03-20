from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ── Analysis ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=20000)
    jd_text: str = Field(..., min_length=50, max_length=10000)


class SkillGap(BaseModel):
    skill: str
    category: str
    required_level: str
    candidate_level: Optional[str]
    gap_score: float
    mention_count: int
    estimated_days: int


class ResumeScore(BaseModel):
    score: float
    breakdown: dict


class AnalysisResponse(BaseModel):
    id: Optional[str] = None
    candidate_name: str
    job_title: str
    learner_level: str
    resume_score: ResumeScore
    overall_similarity: float
    skill_gaps: List[Any]
    overall_gap_score: float
    time_estimate: dict
    learning_roadmap: List[Any]
    ai_summary: str
    created_at: str


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    question: str = Field(..., max_length=2000)
    analysis_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None


# ── Progress ─────────────────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    analysis_id: str
    module_index: int
    completed: bool
