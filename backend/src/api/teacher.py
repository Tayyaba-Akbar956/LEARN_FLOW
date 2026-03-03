"""Teacher API endpoints for LearnFlow platform."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.src.models.base import get_db
from backend.src.services.alert_service import AlertService
from backend.src.services.teacher_intervention_service import TeacherInterventionService
from backend.src.observability.tracing import tracer, trace_function


router = APIRouter(prefix="/api/teacher", tags=["teacher"])


# Request/Response models
class AcknowledgeAlertRequest(BaseModel):
    """Request model for acknowledging an alert."""
    alert_id: int = Field(..., description="Alert identifier")
    teacher_id: int = Field(..., description="Teacher identifier")


class ResolveAlertRequest(BaseModel):
    """Request model for resolving an alert."""
    alert_id: int = Field(..., description="Alert identifier")
    teacher_id: int = Field(..., description="Teacher identifier")
    resolution_notes: Optional[str] = Field(None, description="Notes about resolution")


class SendMessageRequest(BaseModel):
    """Request model for sending a message to student."""
    teacher_id: int = Field(..., description="Teacher identifier")
    student_id: int = Field(..., description="Student identifier")
    session_id: int = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="Message content")


class AlertResponse(BaseModel):
    """Response model for alert."""
    id: int
    student_id: int
    priority: str
    status: str
    message: str
    student_context: Optional[str]
    created_at: str


class StudentContextResponse(BaseModel):
    """Response model for student context."""
    student: Dict[str, Any]
    session: Dict[str, Any]
    recent_messages: List[Dict[str, Any]]
    recent_code: List[Dict[str, Any]]
    recent_exercises: List[Dict[str, Any]]
    struggle_indicators: Dict[str, Any]


class MetricsResponse(BaseModel):
    """Response model for teacher metrics."""
    students_online: int
    pending_alerts: int
    intervention_rate: float
    avg_response_time_seconds: float


# Endpoints
@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    teacher_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get alerts for a teacher.

    This endpoint retrieves alerts for a teacher, optionally filtered by status.

    Args:
        teacher_id: Teacher identifier
        status: Optional status filter (pending, acknowledged, resolved, dismissed)
        limit: Maximum number of alerts to return
        db: Database session

    Returns:
        List of alerts

    Raises:
        HTTPException: If retrieval fails
    """
    with tracer.start_as_current_span(
        "api.teacher.get_alerts",
        attributes={
            "teacher_id": teacher_id,
            "status": status or "all"
        }
    ):
        try:
            alert_service = AlertService(db)

            if status == "pending" or status is None:
                alerts = alert_service.get_pending_alerts(teacher_id, limit)
            else:
                # For other statuses, we'd need to add methods to AlertService
                alerts = alert_service.get_pending_alerts(teacher_id, limit)

            return [
                AlertResponse(
                    id=alert.id,
                    student_id=alert.student_id,
                    priority=alert.priority.value,
                    status=alert.status.value,
                    message=alert.message,
                    student_context=alert.student_context,
                    created_at=alert.created_at.isoformat()
                )
                for alert in alerts
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/alerts/acknowledge")
async def acknowledge_alert(
    request: AcknowledgeAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.

    This endpoint marks an alert as acknowledged by the teacher.

    Args:
        request: Acknowledge request with alert_id and teacher_id
        db: Database session

    Returns:
        Success status

    Raises:
        HTTPException: If acknowledgment fails
    """
    try:
        alert_service = AlertService(db)
        success = alert_service.acknowledge_alert(request.alert_id, request.teacher_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found or already acknowledged")

        return {"success": True, "message": "Alert acknowledged"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/alerts/resolve")
async def resolve_alert(
    request: ResolveAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Resolve an alert.

    This endpoint marks an alert as resolved with optional notes.

    Args:
        request: Resolve request with alert_id, teacher_id, and optional notes
        db: Database session

    Returns:
        Success status

    Raises:
        HTTPException: If resolution fails
    """
    try:
        alert_service = AlertService(db)
        success = alert_service.resolve_alert(
            request.alert_id,
            request.teacher_id,
            request.resolution_notes
        )

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"success": True, "message": "Alert resolved"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/student/{student_id}/context", response_model=StudentContextResponse)
async def get_student_context(
    student_id: int,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive context about a student.

    This endpoint provides code, chat history, and struggle indicators
    to help teachers make intervention decisions.

    Args:
        student_id: Student identifier
        session_id: Optional specific session to focus on
        db: Database session

    Returns:
        Student context with code, chat, and struggle indicators

    Raises:
        HTTPException: If student not found or retrieval fails
    """
    with tracer.start_as_current_span(
        "api.teacher.get_student_context",
        attributes={
            "student_id": student_id,
            "session_id": session_id or "current"
        }
    ):
        try:
            intervention_service = TeacherInterventionService(db)
            context = intervention_service.get_student_context(student_id, session_id)

            if "error" in context:
                raise HTTPException(status_code=404, detail=context["error"])

            return StudentContextResponse(**context)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get student context: {str(e)}")


@router.post("/message")
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to a student.

    This endpoint allows teachers to send messages directly to students
    in their chat interface.

    Args:
        request: Message request with teacher_id, student_id, session_id, and message
        db: Database session

    Returns:
        Created message

    Raises:
        HTTPException: If message sending fails
    """
    try:
        intervention_service = TeacherInterventionService(db)
        message = intervention_service.send_message_to_student(
            teacher_id=request.teacher_id,
            student_id=request.student_id,
            session_id=request.session_id,
            message_content=request.message
        )

        return {
            "success": True,
            "message_id": message.id,
            "created_at": message.created_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    teacher_id: int,
    db: Session = Depends(get_db)
):
    """
    Get teacher dashboard metrics.

    This endpoint provides aggregate metrics including students online,
    intervention rate, and average response time.

    Args:
        teacher_id: Teacher identifier
        db: Database session

    Returns:
        Dashboard metrics

    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        alert_service = AlertService(db)
        intervention_service = TeacherInterventionService(db)

        # Get alert statistics
        alert_stats = alert_service.get_alert_statistics(teacher_id, days=7)

        # Get students online
        students_online = intervention_service.get_students_online()

        # Get intervention metrics
        intervention_metrics = intervention_service.get_intervention_metrics(teacher_id)

        return MetricsResponse(
            students_online=len(students_online),
            pending_alerts=alert_stats.get("pending", 0),
            intervention_rate=alert_stats.get("intervention_rate", 0.0),
            avg_response_time_seconds=alert_stats.get("avg_response_time_seconds", 0.0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
