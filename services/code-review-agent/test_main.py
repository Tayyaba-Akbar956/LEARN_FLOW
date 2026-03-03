import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestCodeReviewAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as code-review-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "code-review-agent"


class TestCodeReviewAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    @patch('main.openai_client')
    def test_invoke_reviews_code_quality(self, mock_openai):
        """Code review agent should assess code quality"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Good use of descriptive variable names."))]
        )

        payload = {
            "message": "Review my code",
            "session_id": "test-session-123",
            "code": "def calculate_total(items):\n    return sum(items)"
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "review" in data
        assert len(data["review"]) > 0

    @patch('main.openai_client')
    def test_invoke_provides_improvement_suggestions(self, mock_openai):
        """Code review agent should suggest improvements"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Consider adding error handling for empty lists."))]
        )

        payload = {
            "message": "How can I improve this?",
            "session_id": "test-session-123",
            "code": "def get_first(lst):\n    return lst[0]"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "review" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    @patch('main.openai_client')
    def test_invoke_checks_pythonic_style(self, mock_openai):
        """Code review agent should check for Pythonic style"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Use list comprehension instead of loop."))]
        )

        payload = {
            "message": "Is this Pythonic?",
            "session_id": "test-session-123",
            "code": "result = []\nfor i in range(10):\n    result.append(i * 2)"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "review" in data
        assert "pythonic_score" in data
        assert 0 <= data["pythonic_score"] <= 10

    @patch('main.openai_client')
    def test_invoke_identifies_best_practices(self, mock_openai):
        """Code review agent should identify best practice violations"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Avoid using mutable default arguments."))]
        )

        payload = {
            "message": "Review this function",
            "session_id": "test-session-123",
            "code": "def add_item(item, lst=[]):\n    lst.append(item)\n    return lst"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "review" in data
        assert "best_practices" in data
        assert isinstance(data["best_practices"], list)

    @patch('main.openai_client')
    def test_invoke_provides_positive_feedback(self, mock_openai):
        """Code review agent should provide positive feedback for good code"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Excellent! Clear function name and proper error handling."))]
        )

        payload = {
            "message": "Review my code",
            "session_id": "test-session-123",
            "code": "def safe_divide(a, b):\n    if b == 0:\n        return None\n    return a / b"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "review" in data
        # Should contain positive words
        assert any(word in data["review"].lower() for word in ["good", "excellent", "great", "well"])

    @patch('main.dapr_client')
    @patch('main.openai_client')
    def test_invoke_publishes_to_kafka(self, mock_openai, mock_dapr):
        """Code review agent should publish review event to Kafka"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Good code structure."))]
        )

        payload = {
            "message": "Review this",
            "session_id": "test-session-123",
            "code": "def hello():\n    print('Hello')"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "learning.events"
        assert call_args[1]["data"]["event_type"] == "code_reviewed"

    def test_invoke_requires_message(self):
        """Invoke should fail without message field"""
        payload = {"session_id": "test-session-123", "code": "print('hi')"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"message": "Review this", "code": "print('hi')"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_code(self):
        """Invoke should fail without code field"""
        payload = {"message": "Review this", "session_id": "test-session-123"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
