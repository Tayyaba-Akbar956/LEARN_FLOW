"""Code execution API endpoints for LearnFlow platform."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from backend.src.services.code_execution_service import CodeExecutionService
from backend.src.observability.tracing import tracer


router = APIRouter(prefix="/api/code", tags=["code"])

# Initialize service
code_execution_service = CodeExecutionService()


# Request/Response models
class CodeExecuteRequest(BaseModel):
    """Request model for code execution."""
    session_id: int = Field(..., description="Session identifier")
    student_id: int = Field(..., description="Student identifier")
    code: str = Field(..., min_length=1, description="Python code to execute")


class CodeExecuteResponse(BaseModel):
    """Response model for code execution."""
    submission: Dict[str, Any]
    result: Dict[str, Any]
    success: bool


class CodeHistoryResponse(BaseModel):
    """Response model for code history."""
    submissions: List[Dict[str, Any]]
    total: int


# Endpoints
@router.post("/execute", response_model=CodeExecuteResponse)
async def execute_code(request: CodeExecuteRequest):
    """
    Execute Python code in a secure sandbox.

    This endpoint accepts Python code, executes it in an isolated Docker
    container with resource limits, and returns the execution results.

    Security features:
    - 5 second timeout
    - 256MB memory limit
    - No network access
    - No filesystem access (except /tmp)
    - Seccomp and AppArmor profiles

    Args:
        request: Code execution request with session_id, student_id, and code

    Returns:
        CodeExecuteResponse with submission, result, and success flag

    Raises:
        HTTPException: If execution fails or validation fails
    """
    with tracer.start_as_current_span(
        "api.code.execute",
        attributes={
            "student_id": request.student_id,
            "session_id": request.session_id,
            "code_length": len(request.code)
        }
    ):
        try:
            result = await code_execution_service.execute_code(
                code=request.code,
                student_id=request.student_id,
                session_id=request.session_id
            )
            return CodeExecuteResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")


@router.get("/history", response_model=CodeHistoryResponse)
async def get_code_history(
    student_id: int,
    session_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get code execution history for a student.

    Retrieves paginated history of all code submissions and their results.

    Args:
        student_id: Student identifier
        session_id: Optional session identifier to filter by
        limit: Maximum number of submissions to return (default: 50)
        offset: Number of submissions to skip (default: 0)

    Returns:
        CodeHistoryResponse with submissions and pagination info

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        submissions = await code_execution_service.get_submission_history(
            student_id=student_id,
            session_id=session_id,
            limit=limit,
            offset=offset
        )

        return CodeHistoryResponse(
            submissions=submissions,
            total=len(submissions)  # TODO: Get actual total count from database
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve code history: {str(e)}")


@router.get("/sandbox/info")
async def get_sandbox_info():
    """
    Get sandbox configuration information.

    Returns information about the sandbox environment including
    resource limits and security settings.

    Returns:
        Dictionary with sandbox configuration
    """
    try:
        sandbox = code_execution_service.sandbox
        return sandbox.get_sandbox_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sandbox info: {str(e)}")
