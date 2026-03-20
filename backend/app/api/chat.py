from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas.schemas import ChatMessage, ChatResponse
from app.core.security import get_current_user
from app.db.mongodb import chat_col
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _smart_local_response(question: str, context: dict) -> str:
    """Rule-based mentor fallback when no API key is configured."""
    q = question.lower()
    job_title = context.get("job_title", "your target role")
    level = context.get("learner_level", "intermediate")
    gaps = context.get("skill_gaps", [])
    top_gap = gaps[0] if gaps else "your priority skill"

    if any(w in q for w in ["first", "start", "begin", "priority"]):
        return (
            f"Start with **{top_gap}** — it's your highest-priority gap for {job_title}. "
            f"Focus on fundamentals first, then build projects to solidify the knowledge. "
            f"2 hours of daily practice is more effective than marathon sessions."
        )
    if any(w in q for w in ["long", "time", "weeks", "days", "how long"]):
        return (
            f"At 2 hours per day, most skill gaps take 2–4 weeks each to close at {level} level. "
            f"Your full roadmap estimate is shown in the Roadmap tab. "
            f"Consistent daily practice is more important than total hours."
        )
    if any(w in q for w in ["resource", "course", "learn", "tutorial", "book"]):
        return (
            f"All recommended resources in your roadmap are free and from verified platforms "
            f"(Coursera, freeCodeCamp, official docs). Check the Roadmap tab for your "
            f"personalized list. Prioritize hands-on projects over passive reading."
        )
    if any(w in q for w in ["interview", "prepare", "question"]):
        return (
            f"For {job_title} interviews: (1) Review fundamentals of your gap skills, "
            f"(2) Practice LeetCode for coding roles or domain-specific problems for others, "
            f"(3) Build 2–3 projects showcasing your skills, "
            f"(4) Be ready to explain your learning journey — it shows initiative."
        )
    if any(w in q for w in ["roadmap", "plan", "path"]):
        return (
            f"Your personalized roadmap is in the Roadmap tab. It's ordered by skill dependencies "
            f"— prerequisites come first so you're never blocked. Each module has a curated "
            f"free resource and a week-by-week plan tailored to your {level} level."
        )
    if any(w in q for w in ["score", "match", "percentage", "percent"]):
        return (
            f"Your resume score reflects how well your current skills match the {job_title} requirements. "
            f"It considers skill coverage (which required skills you have) and level adequacy "
            f"(whether your level meets the requirement). Close your top gaps to improve it."
        )
    return (
        f"Great question! For {job_title} at {level} level, the key is consistent, "
        f"structured learning. Focus on your top priority skill first, build small projects "
        f"as you learn, and track progress in the Roadmap tab. "
        f"What specific aspect would you like guidance on?"
    )


@router.post("", response_model=ChatResponse)
async def mentor_chat(
    body: ChatMessage,
    current_user: dict = Depends(get_current_user),
):
    ctx = body.context or {}
    answer = None

    # Try Groq first if key is configured
    try:
        from app.services.ai_client import chat as ai_chat
        from app.core.config import settings
        if settings.GROQ_API_KEY:
            job_title = ctx.get("job_title", "Software Engineer")
            level = ctx.get("learner_level", "Intermediate")
            gaps = ctx.get("skill_gaps", [])

            prompt = f"""You are an expert career mentor. User context:
- Target role: {job_title}
- Level: {level}
- Top skill gaps: {', '.join(gaps[:5]) if gaps else 'Unknown'}

Answer concisely (2-3 sentences). No markdown formatting.
User: {body.question}"""

            answer = await ai_chat(prompt, max_tokens=300)
    except Exception as e:
        logger.warning(f"AI chat unavailable, using local fallback: {e}")

    # Fallback to smart local response
    if not answer:
        answer = _smart_local_response(body.question, ctx)

    # Save to history
    try:
        await chat_col().insert_one({
            "user_id": current_user["user_id"],
            "analysis_id": body.analysis_id,
            "question": body.question,
            "answer": answer,
            "timestamp": datetime.utcnow(),
        })
    except Exception as e:
        logger.warning(f"Failed to save chat history: {e}")

    return ChatResponse(answer=answer)


@router.get("/history")
async def get_chat_history(
    analysis_id: str = None,
    current_user: dict = Depends(get_current_user),
):
    query = {"user_id": current_user["user_id"]}
    if analysis_id:
        query["analysis_id"] = analysis_id
    cursor = chat_col().find(query).sort("timestamp", -1).limit(50)
    history = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        history.append(doc)
    return list(reversed(history))
