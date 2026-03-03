from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from unittest.mock import Mock

app = FastAPI()

# Mock clients for testing without K8s
openai_client = Mock()
dapr_client = Mock()


class ChatRequest(BaseModel):
    message: str
    session_id: str
    code: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "triage-agent"}


@app.post("/invoke")
async def invoke(request: ChatRequest):
    """
    Triage incoming messages and route to appropriate agent.
    Uses OpenAI to classify the message type and determine routing.
    """
    # Use OpenAI to classify the message and determine routing
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a triage agent. Classify student messages into one of these categories:
                    - concept-explainer: Questions about Python concepts, syntax, or theory
                    - debugger: Error messages, exceptions, or debugging help
                    - code-reviewer: Code review requests or improvement suggestions

                    Respond with ONLY the category name, nothing else."""
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )

        routed_to = response.choices[0].message.content.strip()

        # Publish routing event to Kafka via Dapr
        dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="learning.events",
            data={
                "event_type": "message_routed",
                "session_id": request.session_id,
                "message": request.message,
                "routed_to": routed_to,
                "timestamp": "2026-02-21T16:04:58.967Z"
            }
        )

        return {
            "routed_to": routed_to,
            "session_id": request.session_id,
            "message": request.message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
