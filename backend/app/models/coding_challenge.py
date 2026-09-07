from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func

from app.db.session import Base


class CodingChallenge(Base):
    __tablename__ = "coding_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    skill = Column(String(100), nullable=False, index=True)
    language = Column(String(30), nullable=False, default="Python")
    difficulty = Column(String(30), nullable=False, default="Beginner")
    starter_code = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=False, default=list)
    hints = Column(JSON, nullable=False, default=list)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
