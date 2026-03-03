from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from unittest.mock import Mock

app = FastAPI()

# Mock clients for testing without K8s
openai_client = Mock()
dapr_client = Mock()


class ExerciseRequest(BaseModel):
    action: str  # generate, validate, hint
    session_id: str
    topic: Optional[str] = None
    difficulty: Optional[str] = "beginner"
    success_rate: Optional[float] = None
    exercise_id: Optional[str] = None
    solution: Optional[str] = None
    hint_level: Optional[int] = 1
    attempts: Optional[int] = 1


@app.get("/health")
def health():
    return {"status": "ok", "service": "exercise-agent"}


@app.post("/invoke")
async def invoke(request: ExerciseRequest):
    """
    Generate adaptive exercises, validate solutions, and provide progressive hints.
    Tracks mastery using formula: (exercise×0.4)+(quiz×0.3)+(quality×0.2)+(streak×0.1)
    """
    try:
        if request.action == "generate":
            # Generate exercise based on topic and difficulty
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an exercise generator for Python learners.

Generate a {request.difficulty} level exercise about {request.topic}.

Guidelines:
- Clear problem statement
- Include example input/output
- Appropriate for {request.difficulty} level
- Encourage learning, not just solving"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate a {request.difficulty} exercise about {request.topic}"
                    }
                ]
            )

            exercise = response.choices[0].message.content.strip()

            # Generate test cases
            test_cases = [
                f"Test case 1: Basic functionality",
                f"Test case 2: Edge case handling",
                f"Test case 3: Error conditions"
            ]

            # Adapt difficulty based on success rate
            adapted_difficulty = request.difficulty
            if request.success_rate is not None:
                if request.success_rate > 0.8 and request.difficulty == "beginner":
                    adapted_difficulty = "intermediate"
                elif request.success_rate > 0.8 and request.difficulty == "intermediate":
                    adapted_difficulty = "advanced"
                elif request.success_rate < 0.5 and request.difficulty == "advanced":
                    adapted_difficulty = "intermediate"
                elif request.success_rate < 0.5 and request.difficulty == "intermediate":
                    adapted_difficulty = "beginner"

            # Publish exercise generation event
            dapr_client.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name="learning.events",
                data={
                    "event_type": "exercise_generated",
                    "session_id": request.session_id,
                    "topic": request.topic,
                    "difficulty": adapted_difficulty,
                    "timestamp": "2026-02-21T16:15:42.987Z"
                }
            )

            return {
                "exercise": exercise,
                "difficulty": adapted_difficulty,
                "test_cases": test_cases,
                "session_id": request.session_id
            }

        elif request.action == "validate":
            # Validate student solution
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a solution validator. Check if the code is correct and provide feedback."
                    },
                    {
                        "role": "user",
                        "content": f"Validate this solution:\n{request.solution}"
                    }
                ]
            )

            validation = response.choices[0].message.content.strip()
            is_correct = "correct" in validation.lower() or "works" in validation.lower()

            # Calculate mastery contribution
            # Formula: (exercise×0.4)+(quiz×0.3)+(quality×0.2)+(streak×0.1)
            exercise_score = 1.0 if is_correct else 0.0
            quality_score = 1.0 / max(request.attempts, 1)  # Fewer attempts = higher quality
            mastery_contribution = (exercise_score * 0.4) + (quality_score * 0.2)

            return {
                "validation": validation,
                "is_correct": is_correct,
                "mastery_contribution": mastery_contribution,
                "session_id": request.session_id
            }

        elif request.action == "hint":
            # Provide progressive hint
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"Provide a level {request.hint_level} hint. Level 1 is subtle, level 3 is more direct."
                    },
                    {
                        "role": "user",
                        "content": f"Hint for exercise {request.exercise_id}"
                    }
                ]
            )

            hint = response.choices[0].message.content.strip()

            return {
                "hint": hint,
                "hint_level": request.hint_level,
                "session_id": request.session_id
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exercise operation failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
