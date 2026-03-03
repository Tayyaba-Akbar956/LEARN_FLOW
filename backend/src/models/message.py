"""Message model for chat history in LearnFlow platform."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from backend.src.models.base import Base


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    STUDENT = "student"
    AGENT = "agent"
    TEACHER = "teacher"
    SYSTEM = "system"


class Message(Base):
    """
    Represents a chat message in a learning session.

    Tracks all messages between students, AI agents, and teachers,
    maintaining conversation history for context and review.

    Attributes:
        id: Unique message identifier
        session_id: Foreign key to session
        role: Who sent the message (student, agent, teacher)
        content: Message text content
        agent_type: Type of agent if role is 'agent' (e.g., 'concept_explainer', 'debugger')
        created_at: Message creation timestamp
        metadata: Additional metadata (JSON stored as text)
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    agent_type = Column(String(100), nullable=True)  # e.g., 'concept_explainer', 'debugger'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(Text, nullable=True)  # JSON stored as text

    # Relationships
    session = relationship("Session", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, role='{self.role}')>"

    def to_dict(self) -> dict:
        """Convert message to dictionary representation."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value if isinstance(self.role, MessageRole) else self.role,
            "content": self.content,
            "agent_type": self.agent_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }
