from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    target_role = Column(String(100), nullable=True)
    experience_level = Column(String(50), nullable=True)
    interests = Column(JSON, nullable=True)  # Store list of interest strings
    selected_skills = Column(JSON, nullable=True)  # Store list of skills: ["Python", "DSA", "SQL", etc.]
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="profile")
