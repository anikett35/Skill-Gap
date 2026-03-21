import asyncio
from app.services.analysis import run_full_analysis

async def test():
    resume = """John Smith
Primary Skills: Python (3+ years), JavaScript (2 years), React (1 year), SQL (intermediate)
Experience: 
- Junior Developer at StartupXYZ (2023-Present) - Built Python REST APIs using FastAPI and Flask
- Freelance web development - Created React frontends with responsive CSS
"""
    jd = """Senior Backend Developer
Requirements:
- 5+ years Python experience
- FastAPI and Django expertise
- PostgreSQL and Redis knowledge
- Docker and Kubernetes deployment
- CI/CD pipeline experience
"""
    try:
        result = await run_full_analysis(resume, jd)
        print('✅ Analysis successful')
        print(f'Job title: {result.get("job_title")}')
        print(f'Gaps found: {len(result.get("skill_gaps", []))}')
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
