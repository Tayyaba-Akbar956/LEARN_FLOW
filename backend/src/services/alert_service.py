"""Alert Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.models.teacher_alert import TeacherAlert, AlertStatus, AlertPriority
from backend.src.models.struggle_event import StruggleEvent
from backend.src.models.student import Student
from backend.src.models.teacher import Teacher
from backend.src.observability.tracing import trace_function
import json


class AlertService:
    """
    Service that creates and manages teacher alerts.

    Creates alerts when struggle events exceed thresholds,
    manages alert lifecycle, and tracks teacher responses.
    """

    def __init__(self, db: Session):
        """
        Initialize AlertService.

        Args:
            db: Database session
        """
        self.db = db

    @trace_function(name="alert_service.create_alert")
    def create_alert(
        self,
        struggle_event: StruggleEvent,
        teacher_id: int
    ) -> TeacherAlert:
        """
        Create a teacher alert from a struggle event.

        Args:
            struggle_event: The struggle event triggering the alert
            teacher_id: Teacher to notify

        Returns:
            Created TeacherAlert
        """
        # Get student info
        student = self.db.query(Student).filter(Student.id == struggle_event.student_id).first()

        # Determine priority based on severity
        if struggle_event.severity >= 0.8:
            priority = AlertPriority.URGENT
        elif struggle_event.severity >= 0.6:
            priority = AlertPriority.HIGH
        elif struggle_event.severity >= 0.4:
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW

        # Build alert message
        message = self._build_alert_message(struggle_event, student)

        # Get student context
        student_context = self._build_student_context(struggle_event)

        # Create alert
        alert = TeacherAlert(
            teacher_id=teacher_id,
            student_id=struggle_event.student_id,
            struggle_event_id=struggle_event.id,
            priority=priority,
            status=AlertStatus.PENDING,
            message=message,
            student_context=json.dumps(student_context),
            created_at=datetime.utcnow()
        )

        self.db.add(alert)

        # Mark struggle event as notified
        struggle_event.teacher_notified = 1

        self.db.commit()
        self.db.refresh(alert)

        return alert

    def _build_alert_message(
        self,
        struggle_event: StruggleEvent,
        student: Student
    ) -> str:
        """Build human-readable alert message."""
        trigger_messages = {
            "repeated_failures": f"{student.name} has failed multiple exercises on {struggle_event.topic}",
            "excessive_time": f"{student.name} has spent excessive time on a {struggle_event.topic} exercise",
            "hint_exhaustion": f"{student.name} has exhausted all hints without success on {struggle_event.topic}",
            "multiple_help_requests": f"{student.name} has requested help multiple times on {struggle_event.topic}",
            "error_pattern": f"{student.name} is encountering repeated errors on {struggle_event.topic}"
        }

        base_message = trigger_messages.get(
            struggle_event.trigger.value,
            f"{student.name} is struggling with {struggle_event.topic}"
        )

        return f"{base_message} (severity: {struggle_event.severity:.1%})"

    def _build_student_context(
        self,
        struggle_event: StruggleEvent
    ) -> Dict[str, Any]:
        """Build context about student's current work."""
        # Parse struggle event context
        try:
            event_context = json.loads(struggle_event.context) if struggle_event.context else {}
        except json.JSONDecodeError:
            event_context = {}

        return {
            "trigger": struggle_event.trigger.value,
            "topic": struggle_event.topic,
            "severity": struggle_event.severity,
            "detected_at": struggle_event.detected_at.isoformat(),
            "details": event_context
        }

    @trace_function(name="alert_service.acknowledge_alert")
    def acknowledge_alert(
        self,
        alert_id: int,
        teacher_id: int
    ) -> bool:
        """
        Mark an alert as acknowledged by teacher.

        Args:
            alert_id: Alert identifier
            teacher_id: Teacher acknowledging the alert

        Returns:
            True if acknowledged successfully
        """
        alert = self.db.query(TeacherAlert).filter(
            TeacherAlert.id == alert_id,
            TeacherAlert.teacher_id == teacher_id
        ).first()

        if alert and alert.status == AlertStatus.PENDING:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            self.db.commit()
            return True

        return False

    @trace_function(name="alert_service.resolve_alert")
    def resolve_alert(
        self,
        alert_id: int,
        teacher_id: int,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Mark an alert as resolved.

        Args:
            alert_id: Alert identifier
            teacher_id: Teacher resolving the alert
            resolution_notes: Optional notes about resolution

        Returns:
            True if resolved successfully
        """
        alert = self.db.query(TeacherAlert).filter(
            TeacherAlert.id == alert_id,
            TeacherAlert.teacher_id == teacher_id
        ).first()

        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            if resolution_notes:
                alert.resolution_notes = resolution_notes
            self.db.commit()
            return True

        return False

    def dismiss_alert(
        self,
        alert_id: int,
        teacher_id: int
    ) -> bool:
        """
        Dismiss an alert without intervention.

        Args:
            alert_id: Alert identifier
            teacher_id: Teacher dismissing the alert

        Returns:
            True if dismissed successfully
        """
        alert = self.db.query(TeacherAlert).filter(
            TeacherAlert.id == alert_id,
            TeacherAlert.teacher_id == teacher_id
        ).first()

        if alert:
            alert.status = AlertStatus.DISMISSED
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True

        return False

    def get_pending_alerts(
        self,
        teacher_id: int,
        limit: int = 50
    ) -> List[TeacherAlert]:
        """
        Get pending alerts for a teacher.

        Args:
            teacher_id: Teacher identifier
            limit: Maximum number of alerts to return

        Returns:
            List of pending alerts ordered by priority and creation time
        """
        alerts = (
            self.db.query(TeacherAlert)
            .filter(
                TeacherAlert.teacher_id == teacher_id,
                TeacherAlert.status == AlertStatus.PENDING
            )
            .order_by(
                TeacherAlert.priority.desc(),
                TeacherAlert.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return alerts

    def get_alert_statistics(
        self,
        teacher_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get alert statistics for a teacher.

        Args:
            teacher_id: Teacher identifier
            days: Number of days to look back

        Returns:
            Dictionary with alert statistics
        """
        time_threshold = datetime.utcnow() - timedelta(days=days)

        alerts = (
            self.db.query(TeacherAlert)
            .filter(
                TeacherAlert.teacher_id == teacher_id,
                TeacherAlert.created_at >= time_threshold
            )
            .all()
        )

        total_alerts = len(alerts)
        pending = sum(1 for a in alerts if a.status == AlertStatus.PENDING)
        acknowledged = sum(1 for a in alerts if a.status == AlertStatus.ACKNOWLEDGED)
        resolved = sum(1 for a in alerts if a.status == AlertStatus.RESOLVED)
        dismissed = sum(1 for a in alerts if a.status == AlertStatus.DISMISSED)

        # Calculate average response time
        response_times = [a.response_time_seconds for a in alerts if a.acknowledged_at]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "total_alerts": total_alerts,
            "pending": pending,
            "acknowledged": acknowledged,
            "resolved": resolved,
            "dismissed": dismissed,
            "avg_response_time_seconds": avg_response_time,
            "intervention_rate": (resolved / total_alerts) if total_alerts > 0 else 0
        }
