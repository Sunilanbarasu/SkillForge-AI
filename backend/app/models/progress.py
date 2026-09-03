from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class SkillProgress(Base):
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    previous_assessment_id = Column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    current_assessment_id = Column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    skill = Column(String(50), nullable=False, index=True)

    previous_score = Column(Float, nullable=False)
    current_score = Column(Float, nullable=False)
    score_change = Column(Float, nullable=False)

    status = Column(String(30), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User")

    previous_assessment = relationship(
        "Assessment",
        foreign_keys=[previous_assessment_id]
    )

    current_assessment = relationship(
        "Assessment",
        foreign_keys=[current_assessment_id]
    )