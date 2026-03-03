"""
API Documentation using FastAPI's built-in OpenAPI support.
Provides Swagger UI and ReDoc interfaces for all endpoints.
"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced documentation.

    Args:
        app: FastAPI application instance

    Returns:
        OpenAPI schema dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LearnFlow API",
        version="1.0.0",
        description="""
# LearnFlow API Documentation

LearnFlow is an AI-powered Python tutoring platform that provides personalized learning experiences.

## Features

- **Adaptive Exercises**: Dynamically generated exercises that adapt to student skill level
- **AI Chat Tutoring**: Conversational AI tutors for concepts, debugging, and code review
- **Code Execution**: Sandboxed Python code execution with validation
- **Progress Tracking**: Real-time mastery tracking across Python topics
- **Teacher Intervention**: Struggle detection and teacher alerts for human support

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Obtain a token by authenticating with Better Auth at `/auth/login`.

## Rate Limiting

API requests are rate-limited via Kong API Gateway:
- Student endpoints: 100 requests/minute
- Teacher endpoints: 200 requests/minute
- Code execution: 20 requests/minute

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- 400: Bad Request (invalid input)
- 401: Unauthorized (missing or invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

## Tracing

All requests include OpenTelemetry trace context for distributed tracing.
Include the `traceparent` header to propagate trace context from frontend.
        """,
        routes=app.routes,
        tags=[
            {
                "name": "chat",
                "description": "AI chat tutoring endpoints for conversational learning"
            },
            {
                "name": "code",
                "description": "Code execution and validation endpoints"
            },
            {
                "name": "exercises",
                "description": "Adaptive exercise generation and submission"
            },
            {
                "name": "teacher",
                "description": "Teacher dashboard and intervention endpoints"
            },
            {
                "name": "progress",
                "description": "Student progress and mastery tracking"
            },
            {
                "name": "auth",
                "description": "Authentication and authorization"
            }
        ]
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from Better Auth login"
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Local development"
        },
        {
            "url": "https://api.learnflow.dev",
            "description": "Production"
        }
    ]

    # Add contact and license info
    openapi_schema["info"]["contact"] = {
        "name": "LearnFlow Support",
        "email": "support@learnflow.dev"
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_docs(app: FastAPI) -> None:
    """
    Configure API documentation for FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Override default OpenAPI schema
    app.openapi = lambda: custom_openapi_schema(app)

    # Swagger UI is available at /docs (default)
    # ReDoc is available at /redoc (default)

    # Add custom CSS for Swagger UI
    app.swagger_ui_parameters = {
        "defaultModelsExpandDepth": -1,  # Hide schemas section by default
        "docExpansion": "list",  # Expand tags but not operations
        "filter": True,  # Enable search filter
        "syntaxHighlight.theme": "monokai"  # Dark theme for code
    }


# Example endpoint documentation patterns
"""
Example of well-documented endpoint:

@app.post(
    "/api/exercises/generate",
    tags=["exercises"],
    summary="Generate personalized exercise",
    description=\"\"\"
    Generate a new Python exercise tailored to the student's skill level and learning context.

    The exercise difficulty adapts based on:
    - Recent performance on similar topics
    - Time spent on previous exercises
    - Number of hints used
    - Success rate on test cases

    Returns an exercise with:
    - Problem description
    - Test cases for validation
    - Progressive hints (vague → moderate → specific)
    - Estimated difficulty level
    \"\"\",
    response_description="Generated exercise with test cases and hints",
    responses={
        200: {
            "description": "Exercise generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "exercise_id": "ex_123",
                        "topic": "lists",
                        "difficulty": "intermediate",
                        "description": "Write a function that removes duplicates from a list",
                        "test_cases": [
                            {"input": "[1, 2, 2, 3]", "expected": "[1, 2, 3]"}
                        ],
                        "hints": [
                            {"level": "vague", "text": "Consider using a data structure that doesn't allow duplicates"},
                            {"level": "moderate", "text": "Python's set() can help here"},
                            {"level": "specific", "text": "Convert to set, then back to list: list(set(items))"}
                        ]
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        429: {"description": "Rate limit exceeded"}
    }
)
async def generate_exercise(
    request: ExerciseGenerateRequest,
    user: UserContext = Depends(get_current_student)
):
    pass
"""
