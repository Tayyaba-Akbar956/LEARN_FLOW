"""Hint Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.src.models.hint import Hint, HintLevel
from backend.src.models.exercise import Exercise
from backend.src.models.exercise_attempt import ExerciseAttempt


class HintService:
    """
    Service that manages progressive hints for exercises.

    Provides hints in order from vague to specific, ensuring students
    receive appropriate guidance without giving away solutions.
    """

    def __init__(self, db: Session):
        """
        Initialize HintService.

        Args:
            db: Database session
        """
        self.db = db

    def get_next_hint(
        self,
        exercise_id: int,
        student_id: int,
        hints_already_used: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next hint for a student working on an exercise.

        Args:
            exercise_id: Exercise identifier
            student_id: Student identifier
            hints_already_used: Number of hints already revealed

        Returns:
            Next hint dictionary or None if no more hints
        """
        # Get the next hint in sequence
        next_sequence = hints_already_used + 1

        hint = (
            self.db.query(Hint)
            .filter(
                Hint.exercise_id == exercise_id,
                Hint.sequence == next_sequence
            )
            .first()
        )

        if not hint:
            return None

        return hint.to_dict()

    def get_all_hints(
        self,
        exercise_id: int,
        max_hints: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all hints for an exercise in sequence order.

        Args:
            exercise_id: Exercise identifier
            max_hints: Optional maximum number of hints to return

        Returns:
            List of hint dictionaries ordered by sequence
        """
        query = (
            self.db.query(Hint)
            .filter(Hint.exercise_id == exercise_id)
            .order_by(Hint.sequence)
        )

        if max_hints:
            query = query.limit(max_hints)

        hints = query.all()
        return [hint.to_dict() for hint in hints]

    def create_hints_for_exercise(
        self,
        exercise_id: int,
        hints_data: List[Dict[str, Any]]
    ) -> List[Hint]:
        """
        Create hints for an exercise from generated data.

        Args:
            exercise_id: Exercise identifier
            hints_data: List of hint dictionaries with level, sequence, content

        Returns:
            List of created Hint objects
        """
        created_hints = []

        for hint_data in hints_data:
            # Map string level to enum
            level_str = hint_data.get("level", "vague").lower()
            if level_str == "vague":
                level = HintLevel.VAGUE
            elif level_str == "moderate":
                level = HintLevel.MODERATE
            elif level_str == "specific":
                level = HintLevel.SPECIFIC
            else:
                level = HintLevel.VAGUE

            hint = Hint(
                exercise_id=exercise_id,
                level=level,
                sequence=hint_data.get("sequence", 1),
                content=hint_data.get("content", "")
            )

            self.db.add(hint)
            created_hints.append(hint)

        self.db.commit()

        return created_hints

    def should_provide_hint(
        self,
        student_id: int,
        exercise_id: int,
        hints_already_used: int
    ) -> bool:
        """
        Determine if a hint should be provided based on student's attempts.

        Args:
            student_id: Student identifier
            exercise_id: Exercise identifier
            hints_already_used: Number of hints already used

        Returns:
            True if a hint should be provided
        """
        # Check if there are more hints available
        total_hints = (
            self.db.query(Hint)
            .filter(Hint.exercise_id == exercise_id)
            .count()
        )

        if hints_already_used >= total_hints:
            return False  # No more hints available

        # Check student's recent attempts
        recent_attempts = (
            self.db.query(ExerciseAttempt)
            .filter(
                ExerciseAttempt.student_id == student_id,
                ExerciseAttempt.exercise_id == exercise_id
            )
            .order_by(ExerciseAttempt.submitted_at.desc())
            .limit(3)
            .all()
        )

        # Provide hint if student has made multiple incorrect attempts
        if len(recent_attempts) >= 2:
            all_incorrect = all(not attempt.is_correct for attempt in recent_attempts)
            if all_incorrect:
                return True

        return False

    def get_hint_usage_stats(
        self,
        student_id: int,
        exercise_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about hint usage for a student.

        Args:
            student_id: Student identifier
            exercise_id: Optional exercise filter

        Returns:
            Dictionary with hint usage statistics
        """
        query = self.db.query(ExerciseAttempt).filter(
            ExerciseAttempt.student_id == student_id
        )

        if exercise_id:
            query = query.filter(ExerciseAttempt.exercise_id == exercise_id)

        attempts = query.all()

        if not attempts:
            return {
                "total_attempts": 0,
                "total_hints_used": 0,
                "avg_hints_per_attempt": 0.0,
                "attempts_without_hints": 0
            }

        total_hints = sum(attempt.hints_used for attempt in attempts)
        attempts_without_hints = sum(1 for attempt in attempts if attempt.hints_used == 0)

        return {
            "total_attempts": len(attempts),
            "total_hints_used": total_hints,
            "avg_hints_per_attempt": total_hints / len(attempts),
            "attempts_without_hints": attempts_without_hints
        }
