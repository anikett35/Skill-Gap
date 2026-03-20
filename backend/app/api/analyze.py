from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId

from app.schemas.schemas import AnalyzeRequest
from app.services.analysis import run_full_analysis
from app.core.security import get_current_user
from app.db.mongodb import analyses_col

router = APIRouter()


@router.post("")
async def analyze(
    body: AnalyzeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Run full ML + AI analysis pipeline on resume and job description."""
    try:
        result = await run_full_analysis(body.resume_text, body.jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Persist to MongoDB
    doc = {
        "user_id": current_user["user_id"],
        "resume_text": body.resume_text[:5000],  # truncate for storage
        "jd_text": body.jd_text[:3000],
        "result": result,
        "created_at": datetime.utcnow(),
    }
    inserted = await analyses_col().insert_one(doc)
    result["id"] = str(inserted.inserted_id)

    return result


@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    """Return list of past analyses for the authenticated user."""
    cursor = analyses_col().find(
        {"user_id": current_user["user_id"]},
        {"result.candidate_name": 1, "result.job_title": 1,
         "result.resume_score": 1, "created_at": 1},
    ).sort("created_at", -1).limit(20)

    history = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        history.append(doc)
    return history


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a specific analysis by ID."""
    try:
        oid = ObjectId(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    doc = await analyses_col().find_one(
        {"_id": oid, "user_id": current_user["user_id"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Analysis not found")

    doc["id"] = str(doc.pop("_id"))
    return doc["result"]
