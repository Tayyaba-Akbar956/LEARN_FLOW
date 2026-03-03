"""Code submission event publishers for LearnFlow platform."""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class CodeEventPublisher:
    """
    Publisher for code submission events to Kafka.

    Publishes code execution events for analytics, struggle detection,
    and teacher dashboard updates.
    """

    def __init__(self):
        """Initialize CodeEventPublisher."""
        # TODO: Initialize Dapr client when Kafka is deployed
        self.pubsub_name = "learnflow-pubsub"
        self.topic = "code.submissions"

    async def publish_code_submission(
        self,
        student_id: int,
        submission_id: int,
        code: str,
        language: str,
        execution_time_ms: float,
        output: Optional[str],
        error: Optional[str],
        exit_code: int,
        session_id: Optional[int] = None
    ) -> bool:
        """
        Publish a code submission event to Kafka.

        Args:
            student_id: Student identifier
            submission_id: Submission identifier
            code: Submitted code
            language: Programming language (e.g., "python")
            execution_time_ms: Execution time in milliseconds
            output: Standard output from execution
            error: Error message if execution failed
            exit_code: Process exit code
            session_id: Optional session identifier

        Returns:
            True if published successfully
        """
        event_data = {
            "event_type": "code_submission",
            "student_id": student_id,
            "submission_id": submission_id,
            "code": code,
            "language": language,
            "execution_time_ms": execution_time_ms,
            "output": output,
            "error": error,
            "exit_code": exit_code,
            "session_id": session_id,
            "success": exit_code == 0 and error is None,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            from dapr.clients import DaprClient
            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=self.topic,
                    data=json.dumps(event_data),
                    data_content_type="application/json"
                )

            # For now, just log the event
            print(f"[EVENT] code.submissions: {json.dumps(event_data, indent=2)}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to publish code submission event: {e}")
            return False

    async def publish_execution_failure(
        self,
        student_id: int,
        submission_id: int,
        error_type: str,
        error_message: str,
        code_snippet: str,
        consecutive_failures: int = 1
    ) -> bool:
        """
        Publish an execution failure event for struggle detection.

        Args:
            student_id: Student identifier
            submission_id: Submission identifier
            error_type: Type of error (e.g., "SyntaxError", "RuntimeError")
            error_message: Error message
            code_snippet: Code that caused the error
            consecutive_failures: Number of consecutive failures

        Returns:
            True if published successfully
        """
        event_data = {
            "event_type": "execution_failure",
            "student_id": student_id,
            "submission_id": submission_id,
            "error_type": error_type,
            "error_message": error_message,
            "code_snippet": code_snippet,
            "consecutive_failures": consecutive_failures,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            from dapr.clients import DaprClient
            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name="learning.events",
                    data=json.dumps(event_data),
                    data_content_type="application/json"
                )

            # For now, just log the event
            print(f"[EVENT] learning.events: {json.dumps(event_data, indent=2)}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to publish execution failure event: {e}")
            return False


# Global publisher instance
_publisher_instance = None


def get_code_event_publisher() -> CodeEventPublisher:
    """
    Get or create the global CodeEventPublisher instance.

    Returns:
        CodeEventPublisher instance
    """
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = CodeEventPublisher()
    return _publisher_instance
