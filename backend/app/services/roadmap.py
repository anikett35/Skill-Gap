"""LLM-powered roadmap generation with curated resource DB fallback."""
from __future__ import annotations
import logging
from app.services.ai_client import chat_json

logger = logging.getLogger(__name__)

COURSE_DB = {
    "Python": [
        {"title": "Python for Everybody", "url": "https://www.coursera.org/specializations/python", "type": "course", "level": "beginner"},
        {"title": "Real Python Tutorials", "url": "https://realpython.com", "type": "article", "level": "intermediate"},
    ],
    "Machine Learning": [
        {"title": "ML Specialization — Andrew Ng", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "course", "level": "beginner"},
        {"title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai", "type": "course", "level": "intermediate"},
    ],
    "React": [
        {"title": "React Official Docs", "url": "https://react.dev/learn", "type": "docs", "level": "beginner"},
        {"title": "Full Stack Open", "url": "https://fullstackopen.com", "type": "course", "level": "intermediate"},
    ],
    "TypeScript": [
        {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/", "type": "docs", "level": "beginner"},
    ],
    "Docker": [
        {"title": "Docker Getting Started", "url": "https://docs.docker.com/get-started/", "type": "docs", "level": "beginner"},
        {"title": "Docker & Kubernetes — Udemy", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "type": "course", "level": "intermediate"},
    ],
    "AWS": [
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "type": "course", "level": "beginner"},
    ],
    "SQL": [
        {"title": "SQLZoo", "url": "https://sqlzoo.net", "type": "interactive", "level": "beginner"},
        {"title": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "article", "level": "intermediate"},
    ],
    "JavaScript": [
        {"title": "javascript.info", "url": "https://javascript.info", "type": "article", "level": "beginner"},
        {"title": "You Don't Know JS", "url": "https://github.com/getify/You-Dont-Know-JS", "type": "book", "level": "intermediate"},
    ],
    "System Design": [
        {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "article", "level": "intermediate"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Official Tutorial", "url": "https://kubernetes.io/docs/tutorials/", "type": "docs", "level": "intermediate"},
    ],
    "FastAPI": [
        {"title": "FastAPI Official Docs", "url": "https://fastapi.tiangolo.com", "type": "docs", "level": "beginner"},
    ],
}


def get_resource_for_skill(skill_name: str, learner_level: str) -> dict | None:
    courses = COURSE_DB.get(skill_name, [])
    target = "beginner" if learner_level == "Beginner" else "intermediate"
    for c in courses:
        if c["level"] == target:
            return c
    return courses[0] if courses else None


async def generate_roadmap_with_llm(
    ordered_gaps: list[dict],
    learner_level: str,
    job_title: str,
) -> list[dict]:
    """Generate an adaptive weekly roadmap with LLM, enriched with curated resources."""
    if not ordered_gaps:
        return []

    import json
    gaps_summary = json.dumps(
        [{"skill": g["skill"], "gap_score": g["gap_score"], "category": g["category"]} for g in ordered_gaps[:8]],
        indent=2,
    )

    prompt = f"""You are an expert learning path designer.
Candidate level: {learner_level}. Target role: {job_title}.
Top skill gaps (ordered by dependency): {gaps_summary}

Generate an adaptive weekly learning roadmap with max 8 modules.
Return ONLY a valid JSON array. No markdown, no preamble.

Rules:
- Beginner: fundamentals-first, shorter modules
- Intermediate: project-based, skip basics  
- Advanced: architecture & best practices

Format:
[{{
  "title": "Module title",
  "description": "2-sentence description",
  "duration": "2 weeks",
  "priority": 1,
  "skill_addressed": "Python",
  "category": "Programming",
  "resource_type": "course",
  "resource_url": "https://...",
  "reason": "Why this skill is prioritized (1 sentence)",
  "week_plan": {{"week1": "Core concepts", "week2": "Hands-on projects"}},
  "completed": false
}}]"""

    try:
        modules = await chat_json(prompt, max_tokens=3000)
        if not isinstance(modules, list):
            modules = []
    except Exception as e:
        logger.warning(f"LLM roadmap generation failed: {e}, using fallback")
        modules = _fallback_roadmap(ordered_gaps, learner_level)

    # Enrich with curated resources
    for i, m in enumerate(modules):
        skill = m.get("skill_addressed", "")
        resource = get_resource_for_skill(skill, learner_level)
        if resource:
            m["resource_url"] = resource["url"]
            m["resource_type"] = resource["type"]
        m["completed"] = False
        m["priority"] = i + 1

    return modules


def _fallback_roadmap(ordered_gaps: list[dict], learner_level: str) -> list[dict]:
    """Simple fallback when LLM is unavailable."""
    modules = []
    for i, gap in enumerate(ordered_gaps[:8]):
        skill = gap["skill"]
        resource = get_resource_for_skill(skill, learner_level)
        modules.append({
            "title": f"Master {skill}",
            "description": f"Build {gap['required_level']}-level proficiency in {skill}.",
            "duration": f"{max(1, gap['estimated_days'] // 7)} weeks",
            "priority": i + 1,
            "skill_addressed": skill,
            "category": gap.get("category", "General"),
            "resource_type": resource["type"] if resource else "article",
            "resource_url": resource["url"] if resource else f"https://google.com/search?q=learn+{skill}",
            "reason": f"{skill} has a {gap['gap_score']:.0f}% gap — required at {gap['required_level']} level.",
            "week_plan": {"week1": "Fundamentals", "week2": "Practice projects"},
            "completed": False,
        })
    return modules
