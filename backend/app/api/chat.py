from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas.schemas import ChatMessage, ChatResponse
from app.core.security import get_current_user
from app.db.mongodb import chat_col
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _smart_response(question: str, context: dict) -> str:
    """Intelligent rule-based mentor — instant, no API timeout."""
    q = question.lower()
    job_title = context.get("job_title", "your target role")
    level = context.get("learner_level", "intermediate")
    gaps = context.get("skill_gaps", [])
    top = gaps[0] if gaps else "your priority skill"

    if any(w in q for w in ["first", "start", "begin", "priority", "where"]):
        return (f"Start with {top} — it has the highest gap score for {job_title}. "
                f"Focus 2 hours daily on fundamentals before moving to projects. "
                f"Check your Roadmap tab for the full ordered learning path.")

    if any(w in q for w in ["long", "time", "weeks", "days", "how long", "when"]):
        return (f"At 2 hours per day, each skill gap typically takes 2–4 weeks to close at {level} level. "
                f"Your full roadmap estimate is shown in the Roadmap tab with week-by-week plans. "
                f"Consistency beats intensity — daily practice is more effective than weekend marathons.")

    if any(w in q for w in ["resource", "course", "learn", "tutorial", "book", "where"]):
        return (f"All courses in your Roadmap tab are free and from verified platforms like "
                f"Coursera, freeCodeCamp, Khan Academy, and official documentation. "
                f"Every URL is manually verified — no broken links. Start with the top-priority module.")

    if any(w in q for w in ["interview", "prepare", "question", "hired"]):
        return (f"For {job_title} interviews: (1) Master the fundamentals of your top gap skills first, "
                f"(2) Build 2-3 small projects showcasing those skills, "
                f"(3) Practice explaining your learning journey — interviewers love proactive learners, "
                f"(4) Review system design basics if it's a senior role.")

    if any(w in q for w in ["score", "match", "percent", "result"]):
        return (f"Your resume score measures how well your current skills match the {job_title} requirements. "
                f"It weighs skill coverage (which required skills you have) and level adequacy "
                f"(whether your level meets the bar). Close your top-priority gaps to improve it significantly.")

    if any(w in q for w in ["roadmap", "plan", "path", "order"]):
        return (f"Your roadmap is dependency-aware — prerequisites always come before advanced topics. "
                f"For example, Python comes before Machine Learning, Docker before Kubernetes. "
                f"This ordering is computed by a topological sort algorithm using O*NET skill dependencies.")

    if any(w in q for w in ["help", "how", "what", "explain"]):
        return (f"I can help you understand your skill gaps, plan your learning path, and prepare for {job_title} interviews. "
                f"Try asking: 'What should I learn first?' or 'How long will my roadmap take?' "
                f"or 'How do I prepare for interviews?'")

    return (f"Great question! For {job_title} at {level} level, focus on consistent daily practice. "
            f"Check your Roadmap tab for your personalized learning plan with verified free resources. "
            f"Your top priority skill is: {top}. What specific aspect would you like guidance on?")


@router.post("", response_model=ChatResponse)
async def mentor_chat(
    body: ChatMessage,
    current_user: dict = Depends(get_current_user),
):
    ctx = body.context or {}

    # Try Groq if configured, with short timeout
    answer = None
    try:
        from app.core.config import settings
        if settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) > 10:
            import httpx
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": f"You are a career mentor. Answer briefly (2-3 sentences, no markdown): {body.question}"}],
                        "max_tokens": 200,
                        "temperature": 0.3,
                    },
                )
                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.debug(f"Groq unavailable, using local: {e}")

    if not answer:
        answer = _smart_response(body.question, ctx)

    try:
        await chat_col().insert_one({
            "user_id": current_user["user_id"],
            "analysis_id": body.analysis_id,
            "question": body.question,
            "answer": answer,
            "timestamp": datetime.utcnow(),
        })
    except Exception as e:
        logger.warning(f"Chat save failed: {e}")

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