#!/usr/bin/env python
"""Test the analysis API endpoint"""
import asyncio
import json
import httpx
from app.core.security import create_access_token

async def test_api():
    # Create a test token
    test_user_id = "test_user_123"
    test_email = "test@example.com"
    token = create_access_token(test_user_id, test_email)
    
    resume = "John Smith\nSummary: Python developer with 1 year experience\nSkills: Python, JavaScript"
    jd = "Senior Backend Engineer\nRequired: Python, FastAPI, PostgreSQL, Docker"
    
    payload = {"resume_text": resume, "jd_text": jd}
    
    async with httpx.AsyncClient() as client:
        try:
            print("Testing API endpoint: POST /api/analyze")
            response = await client.post(
                "http://localhost:8000/api/analyze",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ API works!")
            else:
                print(f"✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Connection Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
