import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestConceptsAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as concepts-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "concepts-agent"


class TestConceptsAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    @patch('main.openai_client')
    def test_invoke_explains_python_concept(self, mock_openai):
        """Concepts agent should explain Python concepts clearly"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="A Python list is an ordered, mutable collection of items."))]
        )

        payload = {
            "message": "What is a Python list?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 0

    @patch('main.openai_client')
    def test_invoke_uses_socratic_method(self, mock_openai):
        """Concepts agent should ask guiding questions, not give direct answers"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="What do you think happens when you try to access an index that doesn't exist?"))]
        )

        payload = {
            "message": "How do I fix IndexError?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "explanation" in data
        # Should contain a question mark (Socratic method)
        assert "?" in data["explanation"]

    @patch('main.openai_client')
    def test_invoke_provides_examples(self, mock_openai):
        """Concepts agent should provide code examples"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Here's an example:\n```python\nmy_list = [1, 2, 3]\n```"))]
        )

        payload = {
            "message": "Show me how to create a list",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "explanation" in data
        assert "```" in data["explanation"] or "example" in data["explanation"].lower()

    @patch('main.dapr_client')
    @patch('main.openai_client')
    def test_invoke_publishes_to_kafka(self, mock_openai, mock_dapr):
        """Concepts agent should publish explanation event to Kafka"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="A list is a collection."))]
        )

        payload = {
            "message": "What is a list?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "learning.events"
        assert call_args[1]["data"]["event_type"] == "concept_explained"

    @patch('main.openai_client')
    def test_invoke_tracks_concept_difficulty(self, mock_openai):
        """Concepts agent should track difficulty level of concepts"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Decorators are advanced Python features."))]
        )

        payload = {
            "message": "Explain decorators",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "difficulty" in data
        assert data["difficulty"] in ["beginner", "intermediate", "advanced"]

    def test_invoke_requires_message(self):
        """Invoke should fail without message field"""
        payload = {"session_id": "test-session-123"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"message": "What is a list?"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
