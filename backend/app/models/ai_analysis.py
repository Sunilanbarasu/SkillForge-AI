from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    summary = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=False)        # List of {"skill": str, "reason": str}
    weaknesses = Column(JSON, nullable=False)       # List of {"skill": str, "reason": str}
    skill_gaps = Column(JSON, nullable=False)       # List of {"skill": str, "gap": str, "focus_topics": list}
    priorities = Column(JSON, nullable=False)       # List of {"skill": str, "priority": str, "reason": str}
    recommendations = Column(JSON, nullable=False) # List of {"skill": str, "actions": list}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="ai_analyses")
    assessment = relationship("Assessment", backref="ai_analysis", uselist=False)
