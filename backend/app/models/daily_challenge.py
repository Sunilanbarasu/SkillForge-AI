from sqlalchemy import Column, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.session import Base


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "challenge_date", name="uq_daily_challenge_user_date"),
    )
