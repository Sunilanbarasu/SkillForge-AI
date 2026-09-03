from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuestionOut(BaseModel):
    """
    Public question schema returned to student during assessment.
    CRITICAL SECURITY RULE: correct_answer is NEVER exposed!
    """
    id: int
    skill: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str

    class Config:
        from_attributes = True


class AssessmentStartResponse(BaseModel):
    assessment_id: int
    total_questions: int
    started_at: datetime
    questions: List[QuestionOut]


class AnswerSubmitItem(BaseModel):
    question_id: int
    selected_answer: str = Field(..., pattern="^[A-Da-d]$", description="Answer choice: 'A', 'B', 'C', or 'D'")


class AssessmentSubmitRequest(BaseModel):
    answers: List[AnswerSubmitItem]


class SkillScoreDetail(BaseModel):
    skill: str
    total_questions: int
    correct_answers: int
    score: float

    class Config:
        from_attributes = True


class AssessmentResultResponse(BaseModel):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_questions: int
    total_correct: int
    overall_score: float
    skill_scores: List[SkillScoreDetail] = []

    class Config:
        from_attributes = True


class AssessmentHistoryItem(BaseModel):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_questions: int
    total_correct: int
    overall_score: float

    class Config:
        from_attributes = True
