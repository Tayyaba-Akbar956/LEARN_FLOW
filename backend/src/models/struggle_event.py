"""StruggleEvent model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.models.base import Base


class StruggleTrigger(str, enum.Enum):
    """Struggle trigger type enumeration."""
    REPEATED_FAILURES = "repeated_failures"
    EXCESSIVE_TIME = "excessive_time"
    MULTIPLE_HELP_REQUESTS = "multiple_help_requests"
    ERROR_PATTERN = "error_pattern"
    HINT_EXHAUSTION = "hint_exhaustion"


class StruggleEvent(Base):
    """
    Represents a detected instance of student struggle.

    Tracks various struggle indicators to determine when
    human teacher intervention may be needed.

    Attributes:
        id: Unique event identifier
        student_id: Foreign key to student
        session_id: Foreign key to session
        trigger: Type of struggle detected
        topic: Current topic student is working on
        severity: Severity score (0.0 to 1.0)
        context: JSON context data (code, errors, attempts)
        detected_at: When struggle was detected
        resolved_at: When struggle was resolved (if applicable)
        teacher_notified: Whether teacher was notified
    """

    __tablename__ = "struggle_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    trigger = Column(Enum(StruggleTrigger), nullable=False)
    topic = Column(String(100), nullable=False)
    severity = Column(Float, nullable=False)  # 0.0 to 1.0
    context = Column(Text, nullable=True)  # JSON stored as text
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    teacher_notified = Column(Integer, default=0, nullable=False)  # Boolean as int

    # Relationships
    student = relationship("Student", back_populates="struggle_events")
    session = relationship("Session", back_populates="struggle_events")
    alerts = relationship("TeacherAlert", back_populates="struggle_event", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StruggleEvent(id={self.id}, student_id={self.student_id}, trigger='{self.trigger}', severity={self.severity})>"

    def to_dict(self) -> dict:
        """Convert struggle event to dictionary representation."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "session_id": self.session_id,
            "trigger": self.trigger.value if isinstance(self.trigger, StruggleTrigger) else self.trigger,
            "topic": self.topic,
            "severity": self.severity,
            "context": self.context,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "teacher_notified": bool(self.teacher_notified),
        }

    @property
    def is_resolved(self) -> bool:
        """Check if struggle has been resolved."""
        return self.resolved_at is not None
