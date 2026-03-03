"""Hint model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.models.base import Base


class HintLevel(str, enum.Enum):
    """Hint specificity level enumeration."""
    VAGUE = "vague"
    MODERATE = "moderate"
    SPECIFIC = "specific"


class Hint(Base):
    """
    Represents a progressive hint for an exercise.

    Hints are ordered from vague to specific, guiding students
    toward the solution without giving it away immediately.

    Attributes:
        id: Unique hint identifier
        exercise_id: Foreign key to exercise
        level: Hint specificity level (vague, moderate, specific)
        sequence: Order in which hints should be revealed (1, 2, 3...)
        content: Hint text content
        created_at: Hint creation timestamp
    """

    __tablename__ = "hints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    level = Column(Enum(HintLevel), nullable=False)
    sequence = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    exercise = relationship("Exercise", back_populates="hints")

    def __repr__(self) -> str:
        return f"<Hint(id={self.id}, exercise_id={self.exercise_id}, level='{self.level}', sequence={self.sequence})>"

    def to_dict(self) -> dict:
        """Convert hint to dictionary representation."""
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "level": self.level.value if isinstance(self.level, HintLevel) else self.level,
            "sequence": self.sequence,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
