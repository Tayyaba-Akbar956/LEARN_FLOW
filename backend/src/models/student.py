"""Student model for LearnFlow platform."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.src.models.base import Base


class Student(Base):
    """
    Represents a student user in the LearnFlow platform.

    Attributes:
        id: Unique student identifier
        email: Student email address (unique)
        name: Student full name
        password_hash: Hashed password for authentication
        created_at: Account creation timestamp
        last_active: Last activity timestamp
        consent_monitoring: Whether student consented to session monitoring
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    consent_monitoring = Column(Boolean, default=False, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="student", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="student", cascade="all, delete-orphan")
    struggle_events = relationship("StruggleEvent", back_populates="student", cascade="all, delete-orphan")
    teacher_alerts = relationship("TeacherAlert", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, email='{self.email}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert student to dictionary representation."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "consent_monitoring": self.consent_monitoring,
        }
