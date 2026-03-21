"""
Analysis Service — 100% local, NO external API calls, NO timeouts
"""
from __future__ import annotations
import logging
from datetime import datetime
from app.ml.extractor import extract_resume_context, extract_job_context
from app.ml.adaptive import analyze_gaps, generate_roadmap, generate_reasoning_trace
from app.ml.pipeline import compute_embedding_similarity

logger = logging.getLogger(__name__)


async def run_full_analysis(resume_text: str, jd_text: str) -> dict:
    """
    Full local pipeline — zero external API calls, no timeout risk.
    All processing done locally using ML models only.
    """
    logger.info("Step 1: Extracting resume skills")
    resume_ctx = extract_resume_context(resume_text)
    candidate_skills = resume_ctx["skills"]

    logger.info("Step 2: Parsing job description")
    jd_ctx = extract_job_context(jd_text)
    required_skills = jd_ctx["required_skills"]
    job_title = jd_ctx["job_title"]

    logger.info(f"Found {len(candidate_skills)} resume skills, {len(required_skills)} JD requirements")

    logger.info("Step 3: Embedding similarity")
    try:
        overall_similarity = compute_embedding_similarity(resume_text, jd_text)
    except Exception as e:
        logger.warning(f"Embedding failed: {e}, using 0.5 default")
        overall_similarity = 0.5

    logger.info("Step 4: Gap scoring + knowledge tracing + topological sort")
    gap_analysis = analyze_gaps(candidate_skills, required_skills)
    gaps = gap_analysis["skill_gaps"]
    learner_level = gap_analysis["learner_level"]

    logger.info("Step 5: Generating roadmap from local catalog")
    roadmap = generate_roadmap(gaps, learner_level, job_title)

    logger.info("Step 6: Generating reasoning trace")
    try:
        reasoning_trace = generate_reasoning_trace(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            gaps=gaps,
            resume_score=gap_analysis["resume_score"],
            learner_level=learner_level,
            job_title=job_title,
        )
    except Exception as e:
        logger.warning(f"Reasoning trace failed: {e}")
        reasoning_trace = {"verdict": "Analysis complete", "steps": []}

    ai_summary = _generate_summary(
        gap_analysis["resume_score"]["score"],
        gaps[:3],
        learner_level,
        job_title,
    )

    return {
        "candidate_name": resume_ctx.get("candidate_name", "Candidate"),
        "job_title": job_title,
        "learner_level": learner_level,
        "overall_similarity": overall_similarity,
        "resume_score": gap_analysis["resume_score"],
        "overall_gap_score": gap_analysis["overall_gap_score"],
        "skills_met": gap_analysis["skills_met"],
        "skills_total": gap_analysis["skills_total"],
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
        "skill_gaps": gaps,
        "time_estimate": gap_analysis["time_estimate"],
        "learning_roadmap": roadmap,
        "reasoning_trace": reasoning_trace,
        "ai_summary": ai_summary,
        "created_at": datetime.utcnow().isoformat(),
        "pipeline_info": {
            "extraction": "TF-IDF + O*NET 27.3 taxonomy",
            "similarity": "sentence-transformers/all-MiniLM-L6-v2",
            "pathing": "Kahn's topological sort + knowledge tracing",
            "catalog": "Curated — 100% verified URLs, zero hallucinations",
            "api_calls": 0,
        },
    }


def _generate_summary(score, top_gaps, learner_level, job_title):
    names = [g["skill"] for g in top_gaps]
    if score >= 75:
        s, a = "strong", "focus on a few key areas to reach full competency"
    elif score >= 50:
        s, a = "moderate", "bridge specific skill gaps with targeted learning"
    else:
        s, a = "foundational", "build core skills systematically from prerequisites up"
    out = (f"Your resume shows a {s} match ({score:.0f}/100) for {job_title}. "
           f"As a {learner_level}-level candidate, you should {a}. ")
    if names:
        out += f"Priority areas: {', '.join(names[:3])}."
    return out