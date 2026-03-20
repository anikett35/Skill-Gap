from fastapi import APIRouter, Depends
from datetime import datetime

from app.schemas.schemas import ProgressUpdate
from app.core.security import get_current_user
from app.db.mongodb import progress_col

router = APIRouter()


@router.get("/{analysis_id}")
async def get_progress(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    doc = await progress_col().find_one({
        "user_id": current_user["user_id"],
        "analysis_id": analysis_id,
    })
    if not doc:
        return {"completed_modules": [], "progress_pct": 0, "streak_days": 0}

    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/update")
async def update_progress(
    body: ProgressUpdate,
    current_user: dict = Depends(get_current_user),
):
    query = {"user_id": current_user["user_id"], "analysis_id": body.analysis_id}
    existing = await progress_col().find_one(query)

    completed = set(existing.get("completed_modules", [])) if existing else set()

    if body.completed:
        completed.add(body.module_index)
    else:
        completed.discard(body.module_index)

    await progress_col().update_one(
        query,
        {
            "$set": {
                "completed_modules": list(completed),
                "last_updated": datetime.utcnow(),
            },
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )

    return {"completed_modules": list(completed)}
