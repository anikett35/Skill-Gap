from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
import logging

from app.schemas.schemas import AnalyzeRequest
from app.services.analysis import run_full_analysis
from app.core.security import get_current_user
from app.db.mongodb import analyses_col

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def analyze(
    body: AnalyzeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Run full ML + AI analysis pipeline on resume and job description."""
    # Step 1: Run analysis (this should NOT fail)
    try:
        result = await run_full_analysis(body.resume_text, body.jd_text)
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {type(e).__name__} - {str(e)}"
        )

    # Step 2: Try to persist to MongoDB (should NOT fail the response if it fails)
    analysis_id = None
    try:
        doc = {
            "user_id": current_user["user_id"],
            "resume_text": body.resume_text[:5000],
            "jd_text": body.jd_text[:3000],
            "result": result,
            "created_at": datetime.utcnow(),
        }
        inserted = await analyses_col().insert_one(doc)
        analysis_id = str(inserted.inserted_id)
        result["id"] = analysis_id
        logger.info(f"Analysis saved to MongoDB: {analysis_id}")
    except Exception as e:
        logger.warning(f"Failed to save analysis to MongoDB: {type(e).__name__}: {str(e)}")
        # Still return the analysis result even if storage failed
        result["id"] = "temp_" + datetime.utcnow().isoformat()
        result["storage_warning"] = "Analysis completed but could not be saved to database"

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
