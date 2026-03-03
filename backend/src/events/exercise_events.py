"""Exercise event publishers for LearnFlow platform."""
from typing import Dict, Any
from datetime import datetime
import json


class ExerciseEventPublisher:
    """
    Publisher for exercise-related events to Kafka.

    Publishes exercise completion events for analytics, struggle detection,
    and teacher dashboard updates.
    """

    def __init__(self):
        """Initialize ExerciseEventPublisher."""
        # TODO: Initialize Dapr client when Kafka is deployed
        self.pubsub_name = "learnflow-pubsub"
        self.topic = "exercise.completions"

    async def publish_exercise_completion(
        self,
        student_id: int,
        exercise_id: int,
        attempt_id: int,
        is_correct: bool,
        hints_used: int,
        time_spent_seconds: float,
        test_results: Dict[str, Any],
        difficulty: str,
        topic: str
    ) -> bool:
        """
        Publish an exercise completion event to Kafka.

        Args:
            student_id: Student identifier
            exercise_id: Exercise identifier
            attempt_id: Attempt identifier
            is_correct: Whether solution was correct
            hints_used: Number of hints used
            time_spent_seconds: Time spent on exercise
            test_results: Test validation results
            difficulty: Exercise difficulty level
            topic: Python topic

        Returns:
            True if published successfully
        """
        event_data = {
            "event_type": "exercise_completion",
            "student_id": student_id,
            "exercise_id": exercise_id,
            "attempt_id": attempt_id,
            "is_correct": is_correct,
            "hints_used": hints_used,
            "time_spent_seconds": time_spent_seconds,
            "test_results": test_results,
            "difficulty": difficulty,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # TODO: Uncomment when Dapr/Kafka is deployed
            # from dapr.clients import DaprClient
            # with DaprClient() as client:
            #     client.publish_event(
            #         pubsub_name=self.pubsub_name,
            #         topic_name=self.topic,
            #         data=json.dumps(event_data),
            #         data_content_type="application/json"
            #     )

            # For now, just log the event
            print(f"[EVENT] exercise.completions: {json.dumps(event_data, indent=2)}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to publish exercise completion event: {e}")
            return False

    async def publish_struggle_alert(
        self,
        student_id: int,
        student_name: str,
        exercise_id: int,
        topic: str,
        consecutive_failures: int,
        total_time_spent: float
    ) -> bool:
        """
        Publish a struggle alert when student fails multiple times.

        Args:
            student_id: Student identifier
            student_name: Student name
            exercise_id: Exercise identifier
            topic: Python topic
            consecutive_failures: Number of consecutive failures
            total_time_spent: Total time spent on exercise

        Returns:
            True if published successfully
        """
        alert_data = {
            "event_type": "struggle_alert",
            "student_id": student_id,
            "student_name": student_name,
            "trigger": "exercise_repeated_failure",
            "topic": topic,
            "exercise_id": exercise_id,
            "consecutive_failures": consecutive_failures,
            "total_time_spent_seconds": total_time_spent,
            "timestamp": datetime.utcnow().isoformat(),
            "details": f"Student failed exercise {consecutive_failures} times in {total_time_spent:.1f} seconds"
        }

        try:
            # TODO: Uncomment when Dapr/Kafka is deployed
            # from dapr.clients import DaprClient
            # with DaprClient() as client:
            #     client.publish_event(
            #         pubsub_name=self.pubsub_name,
            #         topic_name="struggle.alerts",
            #         data=json.dumps(alert_data),
            #         data_content_type="application/json"
            #     )

            # For now, just log the alert
            print(f"[ALERT] struggle.alerts: {json.dumps(alert_data, indent=2)}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to publish struggle alert: {e}")
            return False


# Global publisher instance
_publisher_instance = None


def get_exercise_event_publisher() -> ExerciseEventPublisher:
    """
    Get or create the global ExerciseEventPublisher instance.

    Returns:
        ExerciseEventPublisher instance
    """
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = ExerciseEventPublisher()
    return _publisher_instance
