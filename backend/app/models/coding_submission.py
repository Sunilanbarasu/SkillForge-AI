from sqlalchemy import Column, Integer, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=False, default=0.0)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
