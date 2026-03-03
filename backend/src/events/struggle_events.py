"""Struggle event subscribers for LearnFlow platform."""
from typing import Dict, Any
import json


class StruggleEventSubscriber:
    """
    Subscriber for struggle.alerts Kafka topic.

    Listens for struggle alerts and triggers teacher notifications.
    """

    def __init__(self):
        """Initialize StruggleEventSubscriber."""
        # TODO: Initialize Dapr client when Kafka is deployed
        self.pubsub_name = "learnflow-pubsub"
        self.topic = "struggle.alerts"

    async def subscribe_to_struggle_alerts(self, callback):
        """
        Subscribe to struggle alerts topic.

        Args:
            callback: Function to call when alert received
        """
        # TODO: Uncomment when Dapr/Kafka is deployed
        # from dapr.ext.grpc import App
        # app = App()
        #
        # @app.subscribe(pubsub_name=self.pubsub_name, topic=self.topic)
        # def struggle_alert_handler(event):
        #     try:
        #         alert_data = json.loads(event.Data())
        #         callback(alert_data)
        #     except Exception as e:
        #         print(f"[ERROR] Failed to process struggle alert: {e}")
        #
        # app.run(50051)

        print(f"[INFO] Struggle alert subscriber initialized for topic: {self.topic}")

    def process_struggle_alert(self, alert_data: Dict[str, Any]):
        """
        Process a struggle alert event.

        Args:
            alert_data: Alert data from Kafka event
        """
        print(f"[ALERT] Struggle detected: {json.dumps(alert_data, indent=2)}")

        # Extract alert information
        student_id = alert_data.get("student_id")
        trigger = alert_data.get("trigger")
        topic = alert_data.get("topic")

        # TODO: Create teacher alert using AlertService
        # This would be called from the subscriber callback
        # alert_service = AlertService(db)
        # struggle_event = db.query(StruggleEvent).filter(...).first()
        # alert_service.create_alert(struggle_event, teacher_id)

        return {
            "processed": True,
            "student_id": student_id,
            "trigger": trigger,
            "topic": topic
        }


# Global subscriber instance
_subscriber_instance = None


def get_struggle_event_subscriber() -> StruggleEventSubscriber:
    """
    Get or create the global StruggleEventSubscriber instance.

    Returns:
        StruggleEventSubscriber instance
    """
    global _subscriber_instance
    if _subscriber_instance is None:
        _subscriber_instance = StruggleEventSubscriber()
    return _subscriber_instance
