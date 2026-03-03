"""Difficulty Adaptation Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.models.exercise_attempt import ExerciseAttempt
from backend.src.models.exercise import Exercise, DifficultyLevel


class DifficultyAdaptationService:
    """
    Service that adapts exercise difficulty based on student performance.

    Tracks success rate, time taken, and hints used to determine
    whether to increase or decrease difficulty for the next exercise.
    """

    def __init__(self, db: Session):
        """
        Initialize DifficultyAdaptationService.

        Args:
            db: Database session
        """
        self.db = db

    def calculate_performance_score(
        self,
        student_id: int,
        topic: str,
        lookback_attempts: int = 5
    ) -> float:
        """
        Calculate student's performance score for a topic.

        Args:
            student_id: Student identifier
            topic: Python topic to analyze
            lookback_attempts: Number of recent attempts to consider

        Returns:
            Performance score (0.0 to 1.0)
        """
        # Get recent attempts for this topic
        recent_attempts = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .filter(
                ExerciseAttempt.student_id == student_id,
                Exercise.topic == topic
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(lookback_attempts)
            .all()
        )

        if not recent_attempts:
            return 0.5  # Neutral score for new topics

        # Calculate weighted score based on multiple factors
        total_score = 0.0
        for attempt in recent_attempts:
            # Correctness (50% weight)
            correctness_score = 1.0 if attempt.is_correct else 0.0

            # Time efficiency (25% weight) - faster is better, but not too fast
            time_score = 0.5
            if attempt.time_spent_seconds:
                if attempt.time_spent_seconds < 60:  # Too fast, might be guessing
                    time_score = 0.3
                elif attempt.time_spent_seconds < 300:  # Good pace (1-5 minutes)
                    time_score = 1.0
                elif attempt.time_spent_seconds < 600:  # Slower but acceptable
                    time_score = 0.7
                else:  # Very slow, struggling
                    time_score = 0.3

            # Hints usage (25% weight) - fewer hints is better
            hints_score = max(0.0, 1.0 - (attempt.hints_used * 0.25))

            # Weighted average
            attempt_score = (
                correctness_score * 0.5 +
                time_score * 0.25 +
                hints_score * 0.25
            )

            total_score += attempt_score

        return total_score / len(recent_attempts)

    def should_increase_difficulty(
        self,
        student_id: int,
        topic: str,
        current_difficulty: str
    ) -> bool:
        """
        Determine if difficulty should increase for next exercise.

        Args:
            student_id: Student identifier
            topic: Python topic
            current_difficulty: Current difficulty level

        Returns:
            True if difficulty should increase
        """
        if current_difficulty == "advanced":
            return False  # Already at max difficulty

        performance_score = self.calculate_performance_score(student_id, topic)

        # Increase difficulty if performance is consistently high
        return performance_score >= 0.75

    def should_decrease_difficulty(
        self,
        student_id: int,
        topic: str,
        current_difficulty: str
    ) -> bool:
        """
        Determine if difficulty should decrease for next exercise.

        Args:
            student_id: Student identifier
            topic: Python topic
            current_difficulty: Current difficulty level

        Returns:
            True if difficulty should decrease
        """
        if current_difficulty == "beginner":
            return False  # Already at min difficulty

        performance_score = self.calculate_performance_score(student_id, topic)

        # Decrease difficulty if performance is consistently low
        return performance_score <= 0.35

    def get_next_difficulty(
        self,
        student_id: int,
        topic: str,
        current_difficulty: Optional[str] = None
    ) -> str:
        """
        Determine the appropriate difficulty for the next exercise.

        Args:
            student_id: Student identifier
            topic: Python topic
            current_difficulty: Current difficulty level (if any)

        Returns:
            Next difficulty level ("beginner", "intermediate", "advanced")
        """
        # If no current difficulty, start at beginner
        if not current_difficulty:
            return "beginner"

        # Check if we should adjust difficulty
        if self.should_increase_difficulty(student_id, topic, current_difficulty):
            if current_difficulty == "beginner":
                return "intermediate"
            elif current_difficulty == "intermediate":
                return "advanced"

        if self.should_decrease_difficulty(student_id, topic, current_difficulty):
            if current_difficulty == "advanced":
                return "intermediate"
            elif current_difficulty == "intermediate":
                return "beginner"

        # Keep current difficulty if no change needed
        return current_difficulty

    def get_adaptation_context(
        self,
        student_id: int,
        topic: str
    ) -> Dict[str, Any]:
        """
        Get context about student's performance for exercise generation.

        Args:
            student_id: Student identifier
            topic: Python topic

        Returns:
            Dictionary with performance context
        """
        recent_attempts = (
            self.db.query(ExerciseAttempt)
            .join(Exercise)
            .filter(
                ExerciseAttempt.student_id == student_id,
                Exercise.topic == topic
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(5)
            .all()
        )

        if not recent_attempts:
            return {
                "total_attempts": 0,
                "success_rate": 0.0,
                "avg_time_seconds": 0.0,
                "avg_hints_used": 0.0,
                "performance_score": 0.5
            }

        total_attempts = len(recent_attempts)
        successful_attempts = sum(1 for a in recent_attempts if a.is_correct)
        total_time = sum(a.time_spent_seconds or 0 for a in recent_attempts)
        total_hints = sum(a.hints_used for a in recent_attempts)

        return {
            "total_attempts": total_attempts,
            "success_rate": successful_attempts / total_attempts,
            "avg_time_seconds": total_time / total_attempts,
            "avg_hints_used": total_hints / total_attempts,
            "performance_score": self.calculate_performance_score(student_id, topic)
        }
