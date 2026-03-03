"""Session model for LearnFlow platform."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.src.models.base import Base


class Session(Base):
    """
    Represents a learning session for a student.

    A session tracks a continuous period of student activity,
    including chat conversations, code submissions, and exercises.

    Attributes:
        id: Unique session identifier
        student_id: Foreign key to student
        started_at: Session start timestamp
        ended_at: Session end timestamp (None if active)
        context: JSON context data for the session
    """

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    context = Column(Text, nullable=True)  # JSON stored as text

    # Relationships
    student = relationship("Student", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="session", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="session", cascade="all, delete-orphan")
    struggle_events = relationship("StruggleEvent", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        status = "active" if self.ended_at is None else "ended"
        return f"<Session(id={self.id}, student_id={self.student_id}, status='{status}')>"

    def to_dict(self) -> dict:
        """Convert session to dictionary representation."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "context": self.context,
            "is_active": self.ended_at is None,
        }

    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.ended_at is None
