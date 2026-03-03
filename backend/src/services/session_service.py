"""Session service for managing learning sessions."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class SessionService:
    """
    Service for managing student learning sessions.

    Handles session creation, retrieval, updates, and context management.
    """

    def __init__(self, db_client=None):
        """
        Initialize SessionService.

        Args:
            db_client: Database client (Dapr state store or SQLAlchemy session)
        """
        self.db = db_client

    async def create_session(
        self,
        student_id: int,
        current_topic: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Create a new learning session for a student.

        Args:
            student_id: Student identifier
            current_topic: Initial learning topic
            context: Initial session context data

        Returns:
            Created session data as dictionary
        """
        session_data = {
            "student_id": student_id,
            "started_at": datetime.utcnow().isoformat(),
            "ended_at": None,
            "current_topic": current_topic,
            "context": json.dumps(context) if context else None,
        }

        # TODO: Save to database via Dapr state store
        # session_id = await self.db.save_state("sessions", None, session_data)
        # session_data["id"] = session_id

        return session_data

    async def get_session(self, session_id: int) -> Optional[dict]:
        """
        Retrieve session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        # TODO: Retrieve from database via Dapr state store
        # return await self.db.get_state("sessions", str(session_id))
        return None

    async def get_active_session(self, student_id: int) -> Optional[dict]:
        """
        Get the currently active session for a student.

        Args:
            student_id: Student identifier

        Returns:
            Active session data or None if no active session
        """
        # TODO: Query database for active session (ended_at is None)
        # return await self.db.query_state(
        #     "sessions",
        #     filter={"student_id": student_id, "ended_at": None}
        # )
        return None

    async def update_session(
        self,
        session_id: int,
        **updates
    ) -> Optional[dict]:
        """
        Update session information.

        Args:
            session_id: Session identifier
            **updates: Fields to update (current_topic, context, etc.)

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        # Update fields
        for key, value in updates.items():
            if key in session and key != "id":
                if key == "context" and isinstance(value, dict):
                    session[key] = json.dumps(value)
                else:
                    session[key] = value

        # TODO: Save updated data via Dapr state store
        # await self.db.save_state("sessions", str(session_id), session)

        return session

    async def end_session(self, session_id: int) -> Optional[dict]:
        """
        End an active session.

        Args:
            session_id: Session identifier

        Returns:
            Updated session data or None if not found
        """
        return await self.update_session(
            session_id,
            ended_at=datetime.utcnow().isoformat()
        )

    async def get_student_sessions(
        self,
        student_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get all sessions for a student with pagination.

        Args:
            student_id: Student identifier
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip

        Returns:
            List of session data dictionaries
        """
        # TODO: Query database via Dapr state store
        # return await self.db.query_state(
        #     "sessions",
        #     filter={"student_id": student_id},
        #     limit=limit,
        #     offset=offset,
        #     order_by="started_at DESC"
        # )
        return []

    async def update_context(
        self,
        session_id: int,
        context_updates: Dict[str, Any]
    ) -> Optional[dict]:
        """
        Update session context with new data.

        Args:
            session_id: Session identifier
            context_updates: Context data to merge

        Returns:
            Updated session data or None if not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        # Merge context
        existing_context = json.loads(session.get("context", "{}")) if session.get("context") else {}
        existing_context.update(context_updates)

        return await self.update_session(session_id, context=existing_context)

    async def get_session_duration(self, session_id: int) -> Optional[float]:
        """
        Calculate session duration in seconds.

        Args:
            session_id: Session identifier

        Returns:
            Duration in seconds or None if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        started_at = datetime.fromisoformat(session["started_at"])
        ended_at = datetime.fromisoformat(session["ended_at"]) if session.get("ended_at") else datetime.utcnow()

        return (ended_at - started_at).total_seconds()
