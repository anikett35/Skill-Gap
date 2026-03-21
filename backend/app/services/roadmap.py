"""
Roadmap service — local only, uses curated catalog, zero API calls
"""
from app.ml.catalog import get_course

def get_course_for_skill(skill_name: str, learner_level: str):
    return get_course(skill_name, learner_level)