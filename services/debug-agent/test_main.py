import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestDebugAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as debug-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "debug-agent"


class TestDebugAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    @patch('main.openai_client')
    def test_invoke_analyzes_error_message(self, mock_openai):
        """Debug agent should analyze error messages"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="This error occurs when you try to access an index that doesn't exist in the list."))]
        )

        payload = {
            "message": "I'm getting IndexError: list index out of range",
            "session_id": "test-session-123",
            "code": "my_list = [1, 2, 3]\nprint(my_list[5])"
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert len(data["analysis"]) > 0

    @patch('main.openai_client')
    def test_invoke_provides_hints_not_solutions(self, mock_openai):
        """Debug agent should provide hints, not direct solutions"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="What is the length of your list? What index are you trying to access?"))]
        )

        payload = {
            "message": "IndexError on line 5",
            "session_id": "test-session-123",
            "code": "items = [1, 2, 3]\nprint(items[10])"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "analysis" in data
        # Should contain questions (hints, not solutions)
        assert "?" in data["analysis"]

    @patch('main.openai_client')
    def test_invoke_identifies_error_type(self, mock_openai):
        """Debug agent should identify the type of error"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="This is an IndexError."))]
        )

        payload = {
            "message": "IndexError: list index out of range",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "error_type" in data
        assert data["error_type"] in ["IndexError", "TypeError", "ValueError", "AttributeError", "KeyError", "SyntaxError", "NameError", "ZeroDivisionError", "Unknown"]

    @patch('main.openai_client')
    def test_invoke_analyzes_code_context(self, mock_openai):
        """Debug agent should analyze code when provided"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Check the list length before accessing the index."))]
        )

        payload = {
            "message": "Why does this crash?",
            "session_id": "test-session-123",
            "code": "def get_item(lst, idx):\n    return lst[idx]\n\nget_item([1, 2], 5)"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "analysis" in data
        assert "code_provided" in data
        assert data["code_provided"] is True

    @patch('main.dapr_client')
    @patch('main.openai_client')
    def test_invoke_publishes_to_kafka(self, mock_openai, mock_dapr):
        """Debug agent should publish debugging event to Kafka"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Check your list bounds."))]
        )

        payload = {
            "message": "IndexError",
            "session_id": "test-session-123"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "learning.events"
        assert call_args[1]["data"]["event_type"] == "error_debugged"

    @patch('main.openai_client')
    def test_invoke_tracks_struggle_on_repeated_errors(self, mock_openai):
        """Debug agent should flag struggle when same error repeats"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Let's look at this again."))]
        )

        payload = {
            "message": "Still getting IndexError",
            "session_id": "test-session-123",
            "attempt_count": 5
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "struggle_detected" in data
        # 5 attempts should trigger struggle detection
        assert data["struggle_detected"] is True

    def test_invoke_requires_message(self):
        """Invoke should fail without message field"""
        payload = {"session_id": "test-session-123"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"message": "IndexError"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
