from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from unittest.mock import Mock

app = FastAPI()

# Mock clients for testing without K8s
openai_client = Mock()
dapr_client = Mock()


class ConceptRequest(BaseModel):
    message: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "concepts-agent"}


@app.post("/invoke")
async def invoke(request: ConceptRequest):
    """
    Explain Python concepts using Socratic method.
    Guides students to understanding rather than giving direct answers.
    """
    try:
        # Use OpenAI to generate concept explanation with Socratic method
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a Python tutor using the Socratic method. Your goal is to guide students to understanding, not give direct answers.

For concept questions:
- Explain clearly with examples
- Ask guiding questions to check understanding
- Use analogies and real-world examples
- Provide code snippets when helpful

For debugging questions:
- Ask what they think is happening
- Guide them to discover the issue themselves
- Only give hints, not solutions

Always be encouraging and patient."""
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )

        explanation = response.choices[0].message.content.strip()

        # Determine difficulty level based on keywords
        difficulty = "beginner"
        advanced_keywords = ["decorator", "generator", "metaclass", "async", "context manager", "descriptor"]
        intermediate_keywords = ["class", "inheritance", "exception", "module", "package", "comprehension"]

        message_lower = request.message.lower()
        if any(keyword in message_lower for keyword in advanced_keywords):
            difficulty = "advanced"
        elif any(keyword in message_lower for keyword in intermediate_keywords):
            difficulty = "intermediate"

        # Publish concept explanation event to Kafka via Dapr
        dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="learning.events",
            data={
                "event_type": "concept_explained",
                "session_id": request.session_id,
                "message": request.message,
                "difficulty": difficulty,
                "timestamp": "2026-02-21T16:07:13.657Z"
            }
        )

        return {
            "explanation": explanation,
            "difficulty": difficulty,
            "session_id": request.session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
