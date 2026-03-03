import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestExerciseAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as exercise-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "exercise-agent"


class TestExerciseAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    @patch('main.openai_client')
    def test_invoke_generates_exercise(self, mock_openai):
        """Exercise agent should generate practice exercises"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Write a function that returns the sum of two numbers."))]
        )

        payload = {
            "action": "generate",
            "session_id": "test-session-123",
            "topic": "functions",
            "difficulty": "beginner"
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "exercise" in data
        assert len(data["exercise"]) > 0

    @patch('main.openai_client')
    def test_invoke_adapts_difficulty(self, mock_openai):
        """Exercise agent should adapt difficulty based on student performance"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Advanced: Implement a decorator that caches function results."))]
        )

        payload = {
            "action": "generate",
            "session_id": "test-session-123",
            "topic": "decorators",
            "difficulty": "advanced",
            "success_rate": 0.85
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "exercise" in data
        assert "difficulty" in data
        assert data["difficulty"] in ["beginner", "intermediate", "advanced"]

    @patch('main.openai_client')
    def test_invoke_validates_solution(self, mock_openai):
        """Exercise agent should validate student solutions"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Correct! Your solution works for all test cases."))]
        )

        payload = {
            "action": "validate",
            "session_id": "test-session-123",
            "exercise_id": "ex-123",
            "solution": "def add(a, b):\n    return a + b"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "validation" in data
        assert "is_correct" in data
        assert isinstance(data["is_correct"], bool)

    @patch('main.openai_client')
    def test_invoke_provides_hints(self, mock_openai):
        """Exercise agent should provide progressive hints"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Hint: Think about what happens when you iterate over a list."))]
        )

        payload = {
            "action": "hint",
            "session_id": "test-session-123",
            "exercise_id": "ex-123",
            "hint_level": 1
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "hint" in data
        assert "hint_level" in data
        assert data["hint_level"] >= 1

    @patch('main.openai_client')
    def test_invoke_generates_test_cases(self, mock_openai):
        """Exercise agent should generate test cases for exercises"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test: add(2, 3) should return 5"))]
        )

        payload = {
            "action": "generate",
            "session_id": "test-session-123",
            "topic": "functions",
            "difficulty": "beginner"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "test_cases" in data
        assert isinstance(data["test_cases"], list)
        assert len(data["test_cases"]) > 0

    @patch('main.dapr_client')
    @patch('main.openai_client')
    def test_invoke_publishes_to_kafka(self, mock_openai, mock_dapr):
        """Exercise agent should publish exercise events to Kafka"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Write a function to reverse a string."))]
        )

        payload = {
            "action": "generate",
            "session_id": "test-session-123",
            "topic": "strings",
            "difficulty": "beginner"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "learning.events"
        assert call_args[1]["data"]["event_type"] == "exercise_generated"

    @patch('main.openai_client')
    def test_invoke_tracks_mastery(self, mock_openai):
        """Exercise agent should track mastery progress"""
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Correct!"))]
        )

        payload = {
            "action": "validate",
            "session_id": "test-session-123",
            "exercise_id": "ex-123",
            "solution": "def add(a, b):\n    return a + b",
            "attempts": 1
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "mastery_contribution" in data
        # Mastery formula: (exercise×0.4)+(quiz×0.3)+(quality×0.2)+(streak×0.1)
        assert 0 <= data["mastery_contribution"] <= 1

    def test_invoke_requires_action(self):
        """Invoke should fail without action field"""
        payload = {"session_id": "test-session-123", "topic": "functions"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"action": "generate", "topic": "functions"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
