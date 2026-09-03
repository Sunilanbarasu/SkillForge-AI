from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class StrengthItem(BaseModel):
    skill: str
    reason: str


class WeaknessItem(BaseModel):
    skill: str
    reason: str


class SkillGapItem(BaseModel):
    skill: str
    gap: str
    focus_topics: List[str] = Field(default_factory=list)


class PriorityItem(BaseModel):
    skill: str
    priority: str = Field(..., description="'High', 'Medium', or 'Low'")
    reason: str


class RecommendationItem(BaseModel):
    skill: str
    actions: List[str] = Field(default_factory=list)


class AIAnalysisResultSchema(BaseModel):
    summary: str
    strengths: List[StrengthItem] = Field(default_factory=list)
    weaknesses: List[WeaknessItem] = Field(default_factory=list)
    skill_gaps: List[SkillGapItem] = Field(default_factory=list)
    priorities: List[PriorityItem] = Field(default_factory=list)
    recommendations: List[RecommendationItem] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AIAnalysisResponse(BaseModel):
    id: int
    user_id: int
    assessment_id: int
    summary: str
    strengths: List[StrengthItem]
    weaknesses: List[WeaknessItem]
    skill_gaps: List[SkillGapItem]
    priorities: List[PriorityItem]
    recommendations: List[RecommendationItem]
    created_at: datetime

    class Config:
        from_attributes = True
