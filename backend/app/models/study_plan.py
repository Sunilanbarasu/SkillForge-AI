from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    goal = Column(Text, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="study_plans")
    assessment = relationship("Assessment", backref="study_plan", uselist=False)
    tasks = relationship("Task", back_populates="study_plan", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    skill = Column(String(50), nullable=False)
    week_number = Column(Integer, nullable=False)
    task = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)
    estimated_minutes = Column(Integer, nullable=False)

    # Study resource
    resource_title = Column(String(200), nullable=True)
    resource_url = Column(Text, nullable=True)

    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    study_plan = relationship("StudyPlan", back_populates="tasks")