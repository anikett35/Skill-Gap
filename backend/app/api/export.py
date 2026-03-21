from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from bson import ObjectId
from app.core.security import get_current_user
from app.db.mongodb import analyses_col

router = APIRouter()

@router.get("/roadmap/{analysis_id}/pdf")
async def export_roadmap(analysis_id: str, current_user: dict = Depends(get_current_user)):
    try:
        oid = ObjectId(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = await analyses_col().find_one({"_id": oid, "user_id": current_user["user_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    result = doc["result"]
    roadmap = result.get("learning_roadmap", [])
    modules_html = "".join([
        f'<div style="margin:16px 0;padding:16px;border-left:4px solid #2563eb;background:#f8faff">'
        f'<h3 style="color:#1e3a5f">Module {m.get("priority",i+1)}: {m.get("title","")}</h3>'
        f'<p>{m.get("description","")}</p>'
        f'<p style="color:#888">{m.get("duration","")} | {m.get("category","")}</p>'
        f'<a href="{m.get("resource_url","#")}" style="color:#2563eb">{m.get("resource_url","")}</a></div>'
        for i, m in enumerate(roadmap)
    ])
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{{font-family:Arial;padding:40px;color:#1a1a2e}}h1{{color:#1e3a5f}}.score{{font-size:48px;color:#2563eb;font-weight:bold}}</style>
</head><body><h1>Roadmap: {result.get("job_title","")}</h1>
<p>Score: <span class="score">{result.get("resume_score",{}).get("score",0)}/100</span></p>
{modules_html}</body></html>"""
    return HTMLResponse(content=html)
