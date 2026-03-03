"""ExerciseAttempt model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from backend.src.models.base import Base


class ExerciseAttempt(Base):
    """
    Represents a student's attempt at completing an exercise.

    Tracks all attempts, solutions, validation results, and performance
    metrics used for difficulty adaptation.

    Attributes:
        id: Unique attempt identifier
        student_id: Foreign key to student
        exercise_id: Foreign key to exercise
        session_id: Foreign key to session
        solution_code: Student's solution code
        is_correct: Whether the solution passed all test cases
        test_results: JSON string containing detailed test results
        hints_used: Number of hints requested during this attempt
        time_spent_seconds: Time spent on this attempt in seconds
        submitted_at: Attempt submission timestamp
        validated_at: Validation completion timestamp
    """

    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    solution_code = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    test_results = Column(Text, nullable=True)  # JSON stored as text
    hints_used = Column(Integer, default=0, nullable=False)
    time_spent_seconds = Column(Float, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    validated_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="attempts")
    session = relationship("Session", back_populates="exercise_attempts")

    def __repr__(self) -> str:
        status = "correct" if self.is_correct else "incorrect"
        return f"<ExerciseAttempt(id={self.id}, student_id={self.student_id}, exercise_id={self.exercise_id}, status='{status}')>"

    def to_dict(self) -> dict:
        """Convert exercise attempt to dictionary representation."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "exercise_id": self.exercise_id,
            "session_id": self.session_id,
            "solution_code": self.solution_code,
            "is_correct": self.is_correct,
            "test_results": self.test_results,
            "hints_used": self.hints_used,
            "time_spent_seconds": self.time_spent_seconds,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
        }

    @property
    def validation_time_ms(self) -> float:
        """Calculate validation time in milliseconds."""
        if self.submitted_at and self.validated_at:
            return (self.validated_at - self.submitted_at).total_seconds() * 1000
        return 0.0
