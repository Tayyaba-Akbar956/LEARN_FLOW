"""Teacher Intervention Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.src.models.teacher_alert import TeacherAlert
from backend.src.models.student import Student
from backend.src.models.session import Session as StudentSession
from backend.src.models.message import Message, MessageRole
from backend.src.models.exercise_attempt import ExerciseAttempt
from backend.src.models.code_submission import CodeSubmission
from backend.src.observability.tracing import trace_function


class TeacherInterventionService:
    """
    Service that manages teacher interventions and tracks outcomes.

    Provides context for intervention decisions and tracks effectiveness
    to improve AI tutor escalation thresholds.
    """

    def __init__(self, db: Session):
        """
        Initialize TeacherInterventionService.

        Args:
            db: Database session
        """
        self.db = db

    @trace_function(name="teacher_intervention.get_student_context")
    def get_student_context(
        self,
        student_id: int,
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive context about a student for intervention decisions.

        Args:
            student_id: Student identifier
            session_id: Optional specific session to focus on

        Returns:
            Dictionary with student context including code, chat, and struggle indicators
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {"error": "Student not found"}

        # Get current or most recent session
        if session_id:
            session = self.db.query(StudentSession).filter(
                StudentSession.id == session_id,
                StudentSession.student_id == student_id
            ).first()
        else:
            session = (
                self.db.query(StudentSession)
                .filter(StudentSession.student_id == student_id)
                .order_by(StudentSession.started_at.desc())
                .first()
            )

        if not session:
            return {"error": "No session found"}

        # Get recent chat messages
        recent_messages = (
            self.db.query(Message)
            .filter(Message.session_id == session.id)
            .order_by(Message.created_at.desc())
            .limit(10)
            .all()
        )

        # Get recent code submissions
        recent_code = (
            self.db.query(CodeSubmission)
            .filter(
                CodeSubmission.student_id == student_id,
                CodeSubmission.session_id == session.id
            )
            .order_by(CodeSubmission.submitted_at.desc())
            .limit(5)
            .all()
        )

        # Get recent exercise attempts
        recent_exercises = (
            self.db.query(ExerciseAttempt)
            .filter(
                ExerciseAttempt.student_id == student_id,
                ExerciseAttempt.session_id == session.id
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(5)
            .all()
        )

        # Calculate struggle indicators
        struggle_indicators = self._calculate_struggle_indicators(
            student_id=student_id,
            session_id=session.id
        )

        return {
            "student": student.to_dict(),
            "session": session.to_dict(),
            "recent_messages": [m.to_dict() for m in recent_messages],
            "recent_code": [c.to_dict() for c in recent_code],
            "recent_exercises": [e.to_dict() for e in recent_exercises],
            "struggle_indicators": struggle_indicators
        }

    def _calculate_struggle_indicators(
        self,
        student_id: int,
        session_id: int
    ) -> Dict[str, Any]:
        """Calculate current struggle indicators for a student."""
        # Get exercise attempts in current session
        attempts = (
            self.db.query(ExerciseAttempt)
            .filter(
                ExerciseAttempt.student_id == student_id,
                ExerciseAttempt.session_id == session_id
            )
            .all()
        )

        if not attempts:
            return {
                "total_attempts": 0,
                "failure_rate": 0.0,
                "avg_hints_used": 0.0,
                "avg_time_seconds": 0.0
            }

        total_attempts = len(attempts)
        failures = sum(1 for a in attempts if not a.is_correct)
        total_hints = sum(a.hints_used for a in attempts)
        total_time = sum(a.time_spent_seconds or 0 for a in attempts)

        return {
            "total_attempts": total_attempts,
            "failure_rate": failures / total_attempts,
            "avg_hints_used": total_hints / total_attempts,
            "avg_time_seconds": total_time / total_attempts
        }

    @trace_function(name="teacher_intervention.send_message")
    def send_message_to_student(
        self,
        teacher_id: int,
        student_id: int,
        session_id: int,
        message_content: str
    ) -> Message:
        """
        Send a message from teacher to student.

        Args:
            teacher_id: Teacher identifier
            student_id: Student identifier
            session_id: Session identifier
            message_content: Message content

        Returns:
            Created Message object
        """
        # Create message with teacher role
        message = Message(
            session_id=session_id,
            role=MessageRole.TEACHER,
            content=message_content,
            created_at=datetime.utcnow()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def track_intervention_outcome(
        self,
        alert_id: int,
        outcome: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Track the outcome of a teacher intervention.

        Args:
            alert_id: Alert identifier
            outcome: Outcome description
            notes: Optional notes

        Returns:
            True if tracked successfully
        """
        alert = self.db.query(TeacherAlert).filter(TeacherAlert.id == alert_id).first()

        if alert:
            resolution_data = {
                "outcome": outcome,
                "notes": notes,
                "tracked_at": datetime.utcnow().isoformat()
            }

            alert.resolution_notes = str(resolution_data)
            self.db.commit()
            return True

        return False

    def get_intervention_metrics(
        self,
        teacher_id: int
    ) -> Dict[str, Any]:
        """
        Get metrics about teacher interventions.

        Args:
            teacher_id: Teacher identifier

        Returns:
            Dictionary with intervention metrics
        """
        # Get all resolved alerts
        resolved_alerts = (
            self.db.query(TeacherAlert)
            .filter(
                TeacherAlert.teacher_id == teacher_id,
                TeacherAlert.resolved_at.isnot(None)
            )
            .all()
        )

        if not resolved_alerts:
            return {
                "total_interventions": 0,
                "avg_response_time_seconds": 0,
                "resolution_rate": 0
            }

        total_interventions = len(resolved_alerts)
        response_times = [a.response_time_seconds for a in resolved_alerts if a.acknowledged_at]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "total_interventions": total_interventions,
            "avg_response_time_seconds": avg_response_time,
            "resolution_rate": 1.0  # All resolved alerts count as resolutions
        }

    def get_students_online(self) -> List[Dict[str, Any]]:
        """
        Get list of students currently online (active sessions).

        Returns:
            List of student dictionaries with session info
        """
        # Get active sessions (not ended)
        active_sessions = (
            self.db.query(StudentSession)
            .filter(StudentSession.ended_at.is_(None))
            .order_by(StudentSession.started_at.desc())
            .all()
        )

        students_online = []
        for session in active_sessions:
            student = self.db.query(Student).filter(Student.id == session.student_id).first()
            if student:
                students_online.append({
                    "student": student.to_dict(),
                    "session": session.to_dict()
                })

        return students_online
