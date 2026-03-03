"""Struggle Detection Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.models.struggle_event import StruggleEvent, StruggleTrigger
from backend.src.models.exercise_attempt import ExerciseAttempt
from backend.src.models.code_submission import CodeSubmission
from backend.src.models.exercise import Exercise
from backend.src.observability.tracing import trace_function
import json


class StruggleDetectionService:
    """
    Service that detects student struggle and determines when intervention is needed.

    Tracks multiple struggle indicators: repeated failures, excessive time,
    help requests, and error patterns.
    """

    def __init__(self, db: Session):
        """
        Initialize StruggleDetectionService.

        Args:
            db: Database session
        """
        self.db = db

        # Configurable thresholds
        self.failure_threshold = 5  # failures in time window
        self.time_window_minutes = 20
        self.excessive_time_threshold = 600  # 10 minutes on single exercise
        self.hint_exhaustion_threshold = 3  # all hints used without success

    @trace_function(name="struggle_detection.check_student_struggle")
    def check_student_struggle(
        self,
        student_id: int,
        session_id: int,
        topic: str
    ) -> Optional[StruggleEvent]:
        """
        Check if student is currently struggling and needs intervention.

        Args:
            student_id: Student identifier
            session_id: Session identifier
            topic: Current topic

        Returns:
            StruggleEvent if struggle detected, None otherwise
        """
        # Check for repeated failures
        repeated_failures = self._check_repeated_failures(student_id, topic)
        if repeated_failures:
            return self._create_struggle_event(
                student_id=student_id,
                session_id=session_id,
                trigger=StruggleTrigger.REPEATED_FAILURES,
                topic=topic,
                severity=repeated_failures["severity"],
                context=repeated_failures["context"]
            )

        # Check for excessive time on single exercise
        excessive_time = self._check_excessive_time(student_id, topic)
        if excessive_time:
            return self._create_struggle_event(
                student_id=student_id,
                session_id=session_id,
                trigger=StruggleTrigger.EXCESSIVE_TIME,
                topic=topic,
                severity=excessive_time["severity"],
                context=excessive_time["context"]
            )

        # Check for hint exhaustion
        hint_exhaustion = self._check_hint_exhaustion(student_id, topic)
        if hint_exhaustion:
            return self._create_struggle_event(
                student_id=student_id,
                session_id=session_id,
                trigger=StruggleTrigger.HINT_EXHAUSTION,
                topic=topic,
                severity=hint_exhaustion["severity"],
                context=hint_exhaustion["context"]
            )

        return None

    def _check_repeated_failures(
        self,
        student_id: int,
        topic: str
    ) -> Optional[Dict[str, Any]]:
        """Check for repeated exercise failures in time window."""
        time_threshold = datetime.utcnow() - timedelta(minutes=self.time_window_minutes)

        # Get recent failed attempts
        failed_attempts = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .filter(
                ExerciseAttempt.student_id == student_id,
                Exercise.topic == topic,
                ExerciseAttempt.is_correct == False,
                ExerciseAttempt.submitted_at >= time_threshold
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(10)
            .all()
        )

        if len(failed_attempts) >= self.failure_threshold:
            # Calculate severity based on failure count and recency
            severity = min(1.0, len(failed_attempts) / 10.0)

            return {
                "severity": severity,
                "context": json.dumps({
                    "failure_count": len(failed_attempts),
                    "time_window_minutes": self.time_window_minutes,
                    "recent_exercises": [a.exercise_id for a in failed_attempts[:5]]
                })
            }

        return None

    def _check_excessive_time(
        self,
        student_id: int,
        topic: str
    ) -> Optional[Dict[str, Any]]:
        """Check for excessive time spent on single exercise."""
        # Get most recent attempt
        recent_attempt = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .filter(
                ExerciseAttempt.student_id == student_id,
                Exercise.topic == topic,
                ExerciseAttempt.is_correct == False
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .first()
        )

        if recent_attempt and recent_attempt.time_spent_seconds:
            if recent_attempt.time_spent_seconds >= self.excessive_time_threshold:
                # Calculate severity based on time spent
                severity = min(1.0, recent_attempt.time_spent_seconds / (self.excessive_time_threshold * 2))

                return {
                    "severity": severity,
                    "context": json.dumps({
                        "exercise_id": recent_attempt.exercise_id,
                        "time_spent_seconds": recent_attempt.time_spent_seconds,
                        "threshold_seconds": self.excessive_time_threshold
                    })
                }

        return None

    def _check_hint_exhaustion(
        self,
        student_id: int,
        topic: str
    ) -> Optional[Dict[str, Any]]:
        """Check for hint exhaustion without success."""
        # Get recent attempts with all hints used
        recent_attempts = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .filter(
                ExerciseAttempt.student_id == student_id,
                Exercise.topic == topic,
                ExerciseAttempt.hints_used >= self.hint_exhaustion_threshold,
                ExerciseAttempt.is_correct == False
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(3)
            .all()
        )

        if len(recent_attempts) >= 2:
            # Student used all hints multiple times without success
            severity = 0.8  # High severity

            return {
                "severity": severity,
                "context": json.dumps({
                    "attempts_with_max_hints": len(recent_attempts),
                    "exercises": [a.exercise_id for a in recent_attempts]
                })
            }

        return None

    def _create_struggle_event(
        self,
        student_id: int,
        session_id: int,
        trigger: StruggleTrigger,
        topic: str,
        severity: float,
        context: str
    ) -> StruggleEvent:
        """Create and persist a struggle event."""
        struggle_event = StruggleEvent(
            student_id=student_id,
            session_id=session_id,
            trigger=trigger,
            topic=topic,
            severity=severity,
            context=context,
            detected_at=datetime.utcnow(),
            teacher_notified=0
        )

        self.db.add(struggle_event)
        self.db.commit()
        self.db.refresh(struggle_event)

        return struggle_event

    @trace_function(name="struggle_detection.get_recent_struggle_events")
    def get_recent_struggle_events(
        self,
        student_id: int,
        hours: int = 24
    ) -> List[StruggleEvent]:
        """Get recent struggle events for a student."""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        events = (
            self.db.query(StruggleEvent)
            .filter(
                StruggleEvent.student_id == student_id,
                StruggleEvent.detected_at >= time_threshold
            )
            .order_by(StruggleEvent.detected_at.desc())
            .all()
        )

        return events

    def resolve_struggle_event(
        self,
        event_id: int
    ) -> bool:
        """Mark a struggle event as resolved."""
        event = self.db.query(StruggleEvent).filter(StruggleEvent.id == event_id).first()

        if event:
            event.resolved_at = datetime.utcnow()
            self.db.commit()
            return True

        return False
