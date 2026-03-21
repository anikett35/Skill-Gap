import asyncio
from app.services.analysis import run_full_analysis
from app.ml.extractor import extract_resume_context, extract_job_context
from app.ml.adaptive import analyze_gaps, generate_roadmap

async def test():
    resume = """John Smith
    Email: john@example.com
    
    SUMMARY
    Recent CS graduate with 1 year of experience building Python applications and REST APIs.
    
    SKILLS
    Python (intermediate), JavaScript (beginner), HTML/CSS (beginner), SQL (beginner), Git (intermediate)
    
    EXPERIENCE
    Junior Developer - StartupXYZ (2023-Present)
    - Built internal tools using Python and Flask
    - Wrote SQL queries for reporting dashboards
    """
    
    jd = """Senior Backend Developer
    Requirements:
    - 5+ years of Python experience (advanced level required)
    - Strong knowledge of FastAPI or Django (advanced)
    - PostgreSQL and Redis experience (intermediate)
    - Docker and Kubernetes proficiency (intermediate)
    - AWS or GCP cloud experience
    - System Design skills (advanced)
    - Experience with CI/CD pipelines
    - REST API design best practices
    """
    
    print("=" * 60)
    print("Testing ML Pipeline Components")
    print("=" * 60)
    
    # Test 1: Extract resume context
    print("\n1. Testing resume extraction...")
    try:
        resume_ctx = extract_resume_context(resume)
        print(f"   ✅ Candidate: {resume_ctx['candidate_name']}")
        print(f"   ✅ Skills found: {len(resume_ctx['skills'])}")
        for skill in resume_ctx['skills'][:3]:
            print(f"      - {skill['name']} ({skill['level']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Extract job context
    print("\n2. Testing JD extraction...")
    try:
        jd_ctx = extract_job_context(jd)
        print(f"   ✅ Job title: {jd_ctx['job_title']}")
        print(f"   ✅ Skills required: {len(jd_ctx['required_skills'])}")
        for skill in jd_ctx['required_skills'][:3]:
            print(f"      - {skill['name']} ({skill.get('level', 'N/A')})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Full analysis
    print("\n3. Testing full analysis pipeline...")
    try:
        result = await run_full_analysis(resume, jd)
        print(f"   ✅ Analysis completed")
        print(f"   ✅ Overall similarity: {result['overall_similarity']}")
        print(f"   ✅ Skill gaps found: {len(result['skill_gaps'])}")
        print(f"   ✅ Resume score: {result['resume_score']['score']:.1f}/100")
        if result['skill_gaps']:
            print(f"   Top gap: {result['skill_gaps'][0]['skill']} (gap score: {result['skill_gaps'][0]['gap_score']:.1f})")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

asyncio.run(test())

