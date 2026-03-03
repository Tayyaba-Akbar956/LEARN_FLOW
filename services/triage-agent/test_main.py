import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestTriageAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as triage-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "triage-agent"


class TestTriageAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    @patch('main.openai_client')
    def test_invoke_endpoint_accepts_chat_message(self, mock_openai):
        """Invoke should accept chat message and route to appropriate agent"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="concept-explainer"))]
        )

        payload = {
            "message": "What is a Python list?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200

    @patch('main.openai_client')
    def test_invoke_routes_to_concept_explainer(self, mock_openai):
        """Triage should route concept questions to concept-explainer"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="concept-explainer"))]
        )

        payload = {
            "message": "What is a Python list?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert data["routed_to"] == "concept-explainer"

    @patch('main.openai_client')
    def test_invoke_routes_to_debugger(self, mock_openai):
        """Triage should route error questions to debugger"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="debugger"))]
        )

        payload = {
            "message": "I'm getting IndexError: list index out of range",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert data["routed_to"] == "debugger"

    @patch('main.openai_client')
    def test_invoke_routes_to_code_reviewer(self, mock_openai):
        """Triage should route code review requests to code-reviewer"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="code-reviewer"))]
        )

        payload = {
            "message": "Can you review my function?",
            "code": "def add(a, b): return a + b",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert data["routed_to"] == "code-reviewer"

    @patch('main.dapr_client')
    @patch('main.openai_client')
    def test_invoke_publishes_to_kafka(self, mock_openai, mock_dapr):
        """Triage should publish routing event to Kafka via Dapr"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="concept-explainer"))]
        )

        payload = {
            "message": "What is a Python list?",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "learning.events"
        assert call_args[1]["data"]["event_type"] == "message_routed"

    def test_invoke_requires_message(self):
        """Invoke should fail without message field"""
        payload = {"session_id": "test-session-123"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"message": "What is a Python list?"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
