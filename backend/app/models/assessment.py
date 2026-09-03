from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_questions = Column(Integer, default=0, nullable=False)
    total_correct = Column(Integer, default=0, nullable=False)
    overall_score = Column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", backref="assessments")
    answers = relationship("Answer", back_populates="assessment", cascade="all, delete-orphan")
    skill_scores = relationship("SkillScore", back_populates="assessment", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_answer = Column(String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    is_correct = Column(Boolean, nullable=False, default=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question")


class SkillScore(Base):
    __tablename__ = "skill_scores"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    skill = Column(String(50), nullable=False, index=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # Percentage 0-100

    # Relationships
    assessment = relationship("Assessment", back_populates="skill_scores")
