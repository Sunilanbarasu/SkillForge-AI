from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

ALLOWED_SKILLS = ["Python", "C", "DSA", "SQL", "OOP", "DBMS", "Aptitude"]


class ProfileCreateOrUpdate(BaseModel):
    target_role: Optional[str] = Field(None, max_length=100, description="Target role (e.g. Software Engineer)")
    experience_level: Optional[str] = Field(None, max_length=50, description="Experience level (e.g. Beginner, Intermediate, Advanced)")
    interests: Optional[List[str]] = Field(default_factory=list, description="List of topic interests")
    selected_skills: Optional[List[str]] = Field(default_factory=list, description="List of skills to prepare for")

    @field_validator("selected_skills")
    def validate_selected_skills(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return []
        invalid = [skill for skill in v if skill not in ALLOWED_SKILLS]
        if invalid:
            raise ValueError(f"Invalid skills provided: {invalid}. Allowed skills are: {ALLOWED_SKILLS}")
        return v


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    interests: Optional[List[str]] = []
    selected_skills: Optional[List[str]] = []
    updated_at: datetime

    class Config:
        from_attributes = True
