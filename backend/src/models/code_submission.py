"""CodeSubmission model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.models.base import Base


class SubmissionStatus(str, enum.Enum):
    """Code submission status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CodeSubmission(Base):
    """
    Represents a student's code submission for execution.

    Tracks all code submissions, their execution status, and results.

    Attributes:
        id: Unique submission identifier
        student_id: Foreign key to student
        session_id: Foreign key to session
        code: Python code submitted by student
        language: Programming language (always 'python' for now)
        status: Submission status (pending, running, completed, failed, timeout)
        submitted_at: Submission timestamp
        executed_at: Execution start timestamp
        completed_at: Execution completion timestamp
    """

    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50), default="python", nullable=False)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="code_submissions")
    session = relationship("Session", back_populates="code_submissions")
    execution_result = relationship("ExecutionResult", back_populates="submission", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CodeSubmission(id={self.id}, student_id={self.student_id}, status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert code submission to dictionary representation."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "session_id": self.session_id,
            "code": self.code,
            "language": self.language,
            "status": self.status.value if isinstance(self.status, SubmissionStatus) else self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @property
    def execution_time_ms(self) -> float:
        """Calculate execution time in milliseconds."""
        if self.executed_at and self.completed_at:
            return (self.completed_at - self.executed_at).total_seconds() * 1000
        return 0.0
