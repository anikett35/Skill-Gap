#!/usr/bin/env python
"""
Debug script to test the analysis API endpoint
"""
import asyncio
import json
from fastapi import FastAPI
from app.schemas.schemas import AnalyzeRequest
from app.services.analysis import run_full_analysis

async def test_api():
    print("Testing Analysis API...")
    
    # Simulate the request
    request_data = {
        "resume_text": """John Smith
        SUMMARY: Recent CS graduate with 1 year of experience
        SKILLS: Python (intermediate), JavaScript (beginner), HTML/CSS (beginner)""",
        "jd_text": """Senior Backend Engineer
        Requirements: 5+ years Python, FastAPI, PostgreSQL, Docker, AWS"""
    }
    
    try:
        print("1. Processing request...")
        body = AnalyzeRequest(**request_data)
        print(f"   ✓ Request validated")
        
        print("2. Running analysis...")
        result = await run_full_analysis(body.resume_text, body.jd_text)
        print(f"   ✓ Analysis complete")
        
        print("\n3. Result Summary:")
        print(f"   Overall similarity: {result.get('overall_similarity')}")
        print(f"   Resume score: {result.get('resume_score', {}).get('score')}/100")
        print(f"   Skill gaps: {len(result.get('skill_gaps', []))}")
        print(f"   ✓ API would return 200 OK")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_api())
    exit(0 if success else 1)
