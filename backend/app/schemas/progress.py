from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SkillProgressResponse(BaseModel):
    skill: str
    previous_score: float
    current_score: float
    score_change: float
    status: str

    class Config:
        from_attributes = True


class ProgressSummaryResponse(BaseModel):
    previous_assessment_id: int
    current_assessment_id: int

    previous_overall_score: float
    current_overall_score: float
    overall_score_change: float

    improved_skills: int
    declined_skills: int
    unchanged_skills: int

    skill_progress: List[SkillProgressResponse]

    created_at: datetime | None = None

    class Config:
        from_attributes = True