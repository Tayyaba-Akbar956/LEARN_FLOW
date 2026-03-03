from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from unittest.mock import Mock
import re

app = FastAPI()

# Mock clients for testing without K8s
openai_client = Mock()
dapr_client = Mock()


class DebugRequest(BaseModel):
    message: str
    session_id: str
    code: Optional[str] = None
    attempt_count: Optional[int] = 1


@app.get("/health")
def health():
    return {"status": "ok", "service": "debug-agent"}


@app.post("/invoke")
async def invoke(request: DebugRequest):
    """
    Debug Python errors using hints and guiding questions.
    Helps students discover solutions rather than giving direct answers.
    """
    try:
        # Identify error type from message
        error_type = "Unknown"
        error_patterns = {
            "IndexError": r"IndexError",
            "TypeError": r"TypeError",
            "ValueError": r"ValueError",
            "AttributeError": r"AttributeError",
            "KeyError": r"KeyError",
            "SyntaxError": r"SyntaxError",
            "NameError": r"NameError",
            "ZeroDivisionError": r"ZeroDivisionError"
        }

        for err_type, pattern in error_patterns.items():
            if re.search(pattern, request.message, re.IGNORECASE):
                error_type = err_type
                break

        # Build context for OpenAI
        context = f"Error message: {request.message}"
        if request.code:
            context += f"\n\nCode:\n{request.code}"

        # Use OpenAI to generate debugging hints (not solutions)
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a debugging tutor. Your goal is to help students discover bugs themselves, not fix them directly.

For debugging questions:
- Ask guiding questions about what they think is happening
- Point to the line or concept causing the issue
- Provide hints, not solutions
- Encourage them to use print statements or debugger
- Only give the answer if they've truly struggled (5+ attempts)

Always be encouraging and patient."""
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
        )

        analysis = response.choices[0].message.content.strip()

        # Detect struggle (5+ attempts on same error)
        struggle_detected = request.attempt_count >= 5

        # Publish debugging event to Kafka via Dapr
        dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="learning.events",
            data={
                "event_type": "error_debugged",
                "session_id": request.session_id,
                "error_type": error_type,
                "attempt_count": request.attempt_count,
                "struggle_detected": struggle_detected,
                "timestamp": "2026-02-21T16:10:25.869Z"
            }
        )

        return {
            "analysis": analysis,
            "error_type": error_type,
            "code_provided": request.code is not None,
            "struggle_detected": struggle_detected,
            "session_id": request.session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debugging failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
