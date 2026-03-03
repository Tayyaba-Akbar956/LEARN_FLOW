import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


class TestProgressAgentHealth:
    """Test health endpoint"""

    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_service_name(self):
        """Health endpoint should identify as progress-agent"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "progress-agent"


class TestProgressAgentInvoke:
    """Test invoke endpoint with mocked dependencies"""

    def test_invoke_calculates_mastery_score(self):
        """Progress agent should calculate mastery using the formula"""
        payload = {
            "action": "calculate_mastery",
            "session_id": "test-session-123",
            "exercise_score": 0.8,
            "quiz_score": 0.9,
            "code_quality": 0.7,
            "streak_days": 5
        }

        response = client.post("/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "mastery_score" in data
        # Formula: (exercise×0.4)+(quiz×0.3)+(quality×0.2)+(streak×0.1)
        expected = (0.8 * 0.4) + (0.9 * 0.3) + (0.7 * 0.2) + (min(5/30, 1.0) * 0.1)
        assert abs(data["mastery_score"] - expected) < 0.01

    def test_invoke_detects_struggle(self):
        """Progress agent should detect struggle (5 failures in 20 min)"""
        payload = {
            "action": "check_struggle",
            "session_id": "test-session-123",
            "recent_failures": 5,
            "time_window_minutes": 20
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "struggle_detected" in data
        assert data["struggle_detected"] is True

    def test_invoke_no_struggle_with_few_failures(self):
        """Progress agent should not detect struggle with <5 failures"""
        payload = {
            "action": "check_struggle",
            "session_id": "test-session-123",
            "recent_failures": 3,
            "time_window_minutes": 20
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "struggle_detected" in data
        assert data["struggle_detected"] is False

    def test_invoke_tracks_learning_velocity(self):
        """Progress agent should track learning velocity"""
        payload = {
            "action": "track_velocity",
            "session_id": "test-session-123",
            "exercises_completed": 10,
            "time_spent_minutes": 120
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "velocity" in data
        assert data["velocity"] == 10 / 120  # exercises per minute

    def test_invoke_generates_progress_report(self):
        """Progress agent should generate progress reports"""
        payload = {
            "action": "generate_report",
            "session_id": "test-session-123",
            "student_id": "student-456"
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "report" in data
        assert "mastery_score" in data["report"]
        assert "topics_covered" in data["report"]
        assert "struggle_areas" in data["report"]

    @patch('main.dapr_client')
    def test_invoke_publishes_struggle_alert(self, mock_dapr):
        """Progress agent should publish struggle alerts to Kafka"""
        payload = {
            "action": "check_struggle",
            "session_id": "test-session-123",
            "recent_failures": 5,
            "time_window_minutes": 20,
            "student_id": "student-456"
        }

        response = client.post("/invoke", json=payload)

        # Verify Dapr pub/sub was called for struggle alert
        mock_dapr.publish_event.assert_called_once()
        call_args = mock_dapr.publish_event.call_args
        assert call_args[1]["topic_name"] == "struggle.alerts"
        assert call_args[1]["data"]["event_type"] == "struggle_detected"

    def test_invoke_calculates_streak(self):
        """Progress agent should calculate learning streaks"""
        payload = {
            "action": "calculate_streak",
            "session_id": "test-session-123",
            "active_days": [1, 2, 3, 4, 5]  # 5 consecutive days
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "streak_days" in data
        assert data["streak_days"] == 5

    def test_invoke_identifies_weak_topics(self):
        """Progress agent should identify topics needing improvement"""
        payload = {
            "action": "identify_weak_topics",
            "session_id": "test-session-123",
            "topic_scores": {
                "functions": 0.9,
                "loops": 0.4,
                "classes": 0.5
            }
        }

        response = client.post("/invoke", json=payload)
        data = response.json()
        assert "weak_topics" in data
        assert "loops" in data["weak_topics"]
        assert "classes" in data["weak_topics"]
        assert "functions" not in data["weak_topics"]

    def test_invoke_requires_action(self):
        """Invoke should fail without action field"""
        payload = {"session_id": "test-session-123"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error

    def test_invoke_requires_session_id(self):
        """Invoke should fail without session_id field"""
        payload = {"action": "calculate_mastery"}

        response = client.post("/invoke", json=payload)
        assert response.status_code == 422  # Validation error
