from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from unittest.mock import Mock

app = FastAPI()

# Mock clients for testing without K8s
dapr_client = Mock()


class ProgressRequest(BaseModel):
    action: str
    session_id: str
    exercise_score: Optional[float] = None
    quiz_score: Optional[float] = None
    code_quality: Optional[float] = None
    streak_days: Optional[int] = None
    recent_failures: Optional[int] = None
    time_window_minutes: Optional[int] = None
    student_id: Optional[str] = None
    exercises_completed: Optional[int] = None
    time_spent_minutes: Optional[int] = None
    active_days: Optional[List[int]] = None
    topic_scores: Optional[Dict[str, float]] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "progress-agent"}


@app.post("/invoke")
async def invoke(request: ProgressRequest):
    """
    Track student progress, calculate mastery, detect struggle.
    Mastery formula: (exercise×0.4)+(quiz×0.3)+(quality×0.2)+(streak×0.1)
    Struggle detection: 5 failures in 20 minutes
    """
    try:
        if request.action == "calculate_mastery":
            # Calculate mastery score using the formula
            exercise_component = (request.exercise_score or 0) * 0.4
            quiz_component = (request.quiz_score or 0) * 0.3
            quality_component = (request.code_quality or 0) * 0.2

            # Normalize streak (max 30 days = 1.0)
            streak_normalized = min((request.streak_days or 0) / 30.0, 1.0)
            streak_component = streak_normalized * 0.1

            mastery_score = exercise_component + quiz_component + quality_component + streak_component

            return {
                "mastery_score": mastery_score,
                "components": {
                    "exercise": exercise_component,
                    "quiz": quiz_component,
                    "quality": quality_component,
                    "streak": streak_component
                },
                "session_id": request.session_id
            }

        elif request.action == "check_struggle":
            # Detect struggle: 5 failures in 20 minutes
            struggle_detected = (request.recent_failures or 0) >= 5 and (request.time_window_minutes or 0) <= 20

            # Publish struggle alert if detected
            if struggle_detected:
                dapr_client.publish_event(
                    pubsub_name="kafka-pubsub",
                    topic_name="struggle.alerts",
                    data={
                        "event_type": "struggle_detected",
                        "session_id": request.session_id,
                        "student_id": request.student_id,
                        "recent_failures": request.recent_failures,
                        "time_window_minutes": request.time_window_minutes,
                        "timestamp": "2026-02-21T16:18:21.586Z"
                    }
                )

            return {
                "struggle_detected": struggle_detected,
                "recent_failures": request.recent_failures,
                "session_id": request.session_id
            }

        elif request.action == "track_velocity":
            # Calculate learning velocity (exercises per minute)
            velocity = (request.exercises_completed or 0) / max(request.time_spent_minutes or 1, 1)

            return {
                "velocity": velocity,
                "exercises_completed": request.exercises_completed,
                "time_spent_minutes": request.time_spent_minutes,
                "session_id": request.session_id
            }

        elif request.action == "generate_report":
            # Generate progress report
            report = {
                "mastery_score": 0.75,  # Mock value
                "topics_covered": ["functions", "loops", "classes"],
                "struggle_areas": ["decorators", "generators"],
                "exercises_completed": 25,
                "streak_days": 7
            }

            return {
                "report": report,
                "session_id": request.session_id
            }

        elif request.action == "calculate_streak":
            # Calculate streak from active days
            streak_days = len(request.active_days or [])

            return {
                "streak_days": streak_days,
                "active_days": request.active_days,
                "session_id": request.session_id
            }

        elif request.action == "identify_weak_topics":
            # Identify topics with score < 0.6
            weak_topics = []
            if request.topic_scores:
                for topic, score in request.topic_scores.items():
                    if score < 0.6:
                        weak_topics.append(topic)

            return {
                "weak_topics": weak_topics,
                "topic_scores": request.topic_scores,
                "session_id": request.session_id
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress tracking failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
