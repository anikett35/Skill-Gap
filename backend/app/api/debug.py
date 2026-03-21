"""Debug endpoint to diagnose deployment issues."""
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.db.mongodb import db
import importlib

router = APIRouter()


@router.get("/debug/status")
async def debug_status():
    """Check system status and dependencies."""
    status = {
        "environment": settings.ENVIRONMENT,
        "ml_pipeline_ok": False,
        "mongo_uri_set": bool(settings.MONGO_URI),
        "groq_key_set": bool(settings.GROQ_API_KEY),
        "imports": {},
        "errors": [],
    }

    # Check ML imports
    try:
        from app.ml.extractor import extract_skills, extract_resume_context, extract_job_context
        status["imports"]["extractor"] = "✅"
    except Exception as e:
        status["imports"]["extractor"] = f"❌ {str(e)}"
        status["errors"].append(f"Extractor import failed: {str(e)}")

    try:
        from app.ml.adaptive import analyze_gaps, generate_roadmap
        status["imports"]["adaptive"] = "✅"
    except Exception as e:
        status["imports"]["adaptive"] = f"❌ {str(e)}"
        status["errors"].append(f"Adaptive import failed: {str(e)}")

    try:
        from app.ml.pipeline import compute_embedding_similarity
        status["imports"]["pipeline"] = "✅"
    except Exception as e:
        status["imports"]["pipeline"] = f"❌ {str(e)}"
        status["errors"].append(f"Pipeline import failed: {str(e)}")

    try:
        from app.ml.catalog import SKILL_TAXONOMY, COURSE_CATALOG
        status["imports"]["catalog"] = "✅"
        status["skill_count"] = len(SKILL_TAXONOMY)
        status["course_count"] = len(COURSE_CATALOG)
    except Exception as e:
        status["imports"]["catalog"] = f"❌ {str(e)}"
        status["errors"].append(f"Catalog import failed: {str(e)}")

    try:
        from sentence_transformers import SentenceTransformer
        status["imports"]["sentence_transformers"] = "✅"
    except Exception as e:
        status["imports"]["sentence_transformers"] = f"❌ {str(e)}"
        status["errors"].append(f"SentenceTransformers import failed: {str(e)}")

    return status


@router.post("/debug/test-analysis")
async def test_analysis(resume_text: str, jd_text: str):
    """Test the analysis pipeline with given inputs."""
    try:
        from app.services.analysis import run_full_analysis
        import asyncio
        
        result = await run_full_analysis(resume_text, jd_text)
        return {
            "status": "✅ Success",
            "candidate_name": result.get("candidate_name"),
            "job_title": result.get("job_title"),
            "gaps_count": len(result.get("skill_gaps", [])),
        }
    except Exception as e:
        import traceback
        return {
            "status": "❌ Failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }
