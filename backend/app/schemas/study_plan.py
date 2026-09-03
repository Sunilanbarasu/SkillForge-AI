from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class StudyTask(BaseModel):
    skill: str = Field(..., min_length=1, max_length=50)
    week_number: int = Field(..., gt=0, description="Positive integer week number")
    task: str = Field(..., min_length=1)
    difficulty: str = Field(
        ...,
        description="'Beginner', 'Intermediate', or 'Advanced'"
    )
    estimated_minutes: int = Field(
        ...,
        gt=0,
        description="Positive integer estimated minutes"
    )

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"Beginner", "Intermediate", "Advanced"}
        if v not in allowed:
            raise ValueError(f"difficulty must be one of {sorted(allowed)}")
        return v


class StudyPlanAIResponse(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    goal: str = Field(..., min_length=1)
    duration_weeks: int = Field(..., gt=0)
    tasks: List[StudyTask] = Field(..., min_length=1)

    @field_validator("duration_weeks")
    @classmethod
    def validate_duration_weeks(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_weeks must be a positive integer")
        return v


class TaskResponse(BaseModel):
    id: int
    study_plan_id: int
    skill: str
    week_number: int
    task: str
    difficulty: str
    estimated_minutes: int
    status: str
    completed_at: Optional[datetime] = None

    # Study resource
    resource_title: Optional[str] = None
    resource_url: Optional[str] = None

    class Config:
        from_attributes = True


class StudyPlanResponse(BaseModel):
    id: int
    user_id: int
    assessment_id: int
    title: str
    goal: str
    duration_weeks: int
    created_at: datetime
    tasks: List[TaskResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TaskUpdateRequest(BaseModel):
    status: str = Field(..., description="'pending' or 'completed'")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in {"pending", "completed"}:
            raise ValueError("status must be 'pending' or 'completed'")
        return v