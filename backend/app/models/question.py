from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.session import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String(50), nullable=False, index=True)  # Python, C, DSA, SQL, OOP, DBMS, Aptitude
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    difficulty = Column(String(20), nullable=False, default="Beginner")  # 'Beginner' or 'Intermediate'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
