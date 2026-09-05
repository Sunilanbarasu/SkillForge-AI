from typing import List
from pydantic import BaseModel


class AdaptiveSkillInsight(BaseModel):
    skill: str

    current_score: float
    previous_score: float | None = None
    score_change: float | None = None

    classification: str
    trend: str
    priority: str

    total_questions: int
    correct_answers: int
    accuracy: float

    beginner_accuracy: float | None = None
    intermediate_accuracy: float | None = None

    reason: str


class AdaptiveAnalysisResponse(BaseModel):
    assessment_id: int
    previous_assessment_id: int | None = None

    overall_score: float
    previous_overall_score: float | None = None
    overall_score_change: float | None = None

    strong_skills: List[str]
    good_skills: List[str]
    weak_skills: List[str]
    critical_skills: List[str]

    improving_skills: List[str]
    declining_skills: List[str]

    priority_skills: List[str]

    skills: List[AdaptiveSkillInsight]
