"""Teacher model for LearnFlow platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.src.models.base import Base


class Teacher(Base):
    """
    Represents a teacher user in the LearnFlow platform.

    Teachers monitor student progress, receive struggle alerts,
    and intervene when AI tutoring is insufficient.

    Attributes:
        id: Unique teacher identifier
        email: Teacher email address (unique)
        name: Teacher full name
        password_hash: Hashed password for authentication
        created_at: Account creation timestamp
        last_active: Last activity timestamp
        is_active: Whether teacher account is active
    """

    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    alerts = relationship("TeacherAlert", back_populates="teacher", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, email='{self.email}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert teacher to dictionary representation."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "is_active": self.is_active,
        }
