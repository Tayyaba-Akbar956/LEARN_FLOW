"""ExecutionResult model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from backend.src.models.base import Base


class ExecutionResult(Base):
    """
    Represents the result of code execution.

    Stores stdout, stderr, exit code, and execution metrics.

    Attributes:
        id: Unique result identifier
        submission_id: Foreign key to code submission
        stdout: Standard output from code execution
        stderr: Standard error from code execution
        exit_code: Process exit code (0 = success)
        execution_time_ms: Execution time in milliseconds
        memory_used_mb: Memory used in megabytes
        timed_out: Whether execution timed out
        error_message: Error message if execution failed
        created_at: Result creation timestamp
    """

    __tablename__ = "execution_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey("code_submissions.id"), nullable=False, unique=True, index=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    exit_code = Column(Integer, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    memory_used_mb = Column(Float, nullable=True)
    timed_out = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = relationship("CodeSubmission", back_populates="execution_result")

    def __repr__(self) -> str:
        return f"<ExecutionResult(id={self.id}, submission_id={self.submission_id}, exit_code={self.exit_code})>"

    def to_dict(self) -> dict:
        """Convert execution result to dictionary representation."""
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "memory_used_mb": self.memory_used_mb,
            "timed_out": self.timed_out,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0 and not self.timed_out

    @property
    def has_output(self) -> bool:
        """Check if execution produced any output."""
        return bool(self.stdout or self.stderr)
