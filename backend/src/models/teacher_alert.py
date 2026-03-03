"""TeacherAlert model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.models.base import Base


class AlertStatus(str, enum.Enum):
    """Alert status enumeration."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertPriority(str, enum.Enum):
    """Alert priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TeacherAlert(Base):
    """
    Represents an alert sent to a teacher about student struggle.

    Alerts are created when struggle detection thresholds are exceeded,
    providing teachers with context to decide on intervention.

    Attributes:
        id: Unique alert identifier
        teacher_id: Foreign key to teacher
        student_id: Foreign key to student
        struggle_event_id: Foreign key to struggle event
        priority: Alert priority level
        status: Alert status (pending, acknowledged, resolved, dismissed)
        message: Alert message text
        student_context: JSON context about student's current work
        created_at: Alert creation timestamp
        acknowledged_at: When teacher acknowledged alert
        resolved_at: When alert was resolved
        resolution_notes: Teacher's notes on resolution
    """

    __tablename__ = "teacher_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    struggle_event_id = Column(Integer, ForeignKey("struggle_events.id"), nullable=False, index=True)
    priority = Column(Enum(AlertPriority), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False)
    message = Column(Text, nullable=False)
    student_context = Column(Text, nullable=True)  # JSON stored as text
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    teacher = relationship("Teacher", back_populates="alerts")
    student = relationship("Student", back_populates="teacher_alerts")
    struggle_event = relationship("StruggleEvent", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<TeacherAlert(id={self.id}, teacher_id={self.teacher_id}, student_id={self.student_id}, priority='{self.priority}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert teacher alert to dictionary representation."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "struggle_event_id": self.struggle_event_id,
            "priority": self.priority.value if isinstance(self.priority, AlertPriority) else self.priority,
            "status": self.status.value if isinstance(self.status, AlertStatus) else self.status,
            "message": self.message,
            "student_context": self.student_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
        }

    @property
    def is_pending(self) -> bool:
        """Check if alert is pending."""
        return self.status == AlertStatus.PENDING

    @property
    def response_time_seconds(self) -> float:
        """Calculate response time in seconds."""
        if self.acknowledged_at:
            return (self.acknowledged_at - self.created_at).total_seconds()
        return 0.0
