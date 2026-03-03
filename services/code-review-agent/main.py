from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from unittest.mock import Mock
import re

app = FastAPI()

# Mock clients for testing without K8s
openai_client = Mock()
dapr_client = Mock()


class CodeReviewRequest(BaseModel):
    message: str
    session_id: str
    code: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "code-review-agent"}


@app.post("/invoke")
async def invoke(request: CodeReviewRequest):
    """
    Review Python code for quality, style, and best practices.
    Provides constructive feedback and improvement suggestions.
    """
    try:
        # Use OpenAI to generate code review
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a code review tutor. Your goal is to help students write better Python code.

For code reviews:
- Start with positive feedback (what they did well)
- Identify areas for improvement
- Suggest Pythonic alternatives
- Point out best practice violations
- Explain WHY changes would be better
- Be encouraging and constructive

Focus on:
- Code readability and clarity
- Pythonic idioms
- Error handling
- Performance considerations
- Best practices (PEP 8, naming conventions)"""
                },
                {
                    "role": "user",
                    "content": f"{request.message}\n\nCode to review:\n{request.code}"
                }
            ]
        )

        review = response.choices[0].message.content.strip()

        # Extract suggestions (lines that suggest improvements)
        suggestions = []
        for line in review.split('\n'):
            if any(keyword in line.lower() for keyword in ['consider', 'suggest', 'could', 'try', 'instead']):
                suggestions.append(line.strip())

        # Calculate Pythonic score (simple heuristic)
        pythonic_score = 7  # Default score

        # Deduct points for anti-patterns
        if 'for' in request.code and 'append' in request.code:
            pythonic_score -= 1  # Could use comprehension
        if 'range(len(' in request.code:
            pythonic_score -= 1  # Could use enumerate
        if '[]' in request.code and 'def' in request.code and '=' in request.code.split('def')[1].split(':')[0]:
            pythonic_score -= 2  # Mutable default argument

        # Add points for good practices
        if 'if __name__' in request.code:
            pythonic_score += 1
        if any(word in request.code for word in ['try:', 'except']):
            pythonic_score += 1

        pythonic_score = max(0, min(10, pythonic_score))  # Clamp to 0-10

        # Identify best practices
        best_practices = []
        if 'def' in request.code:
            if re.search(r'def [a-z_][a-z0-9_]*\(', request.code):
                best_practices.append("Good: Function uses snake_case naming")
        if 'try:' in request.code and 'except' in request.code:
            best_practices.append("Good: Includes error handling")
        if len(request.code.split('\n')) > 0 and not request.code.strip().startswith('def'):
            if 'if __name__' not in request.code:
                best_practices.append("Consider: Add if __name__ == '__main__' guard")

        # Publish code review event to Kafka via Dapr
        dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="learning.events",
            data={
                "event_type": "code_reviewed",
                "session_id": request.session_id,
                "pythonic_score": pythonic_score,
                "suggestions_count": len(suggestions),
                "timestamp": "2026-02-21T16:13:14.772Z"
            }
        )

        return {
            "review": review,
            "suggestions": suggestions,
            "pythonic_score": pythonic_score,
            "best_practices": best_practices,
            "session_id": request.session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
