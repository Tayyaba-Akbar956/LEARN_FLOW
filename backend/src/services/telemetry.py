"""OpenTelemetry tracing configuration for chat service."""
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from typing import Optional, Dict, Any

# Get tracer
tracer = trace.get_tracer(__name__)


def trace_chat_flow(
    session_id: int,
    student_id: int,
    question: str,
    agent_type: Optional[str] = None
):
    """
    Trace the complete chat flow: question → triage → agent → response.

    Args:
        session_id: Session identifier
        student_id: Student identifier
        question: Student's question
        agent_type: Selected agent type (if known)

    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        "chat.process_message",
        attributes={
            "session.id": session_id,
            "student.id": student_id,
            "question.length": len(question),
            "agent.type": agent_type or "unknown",
        }
    )


def trace_triage(question: str, context: Optional[Dict[str, Any]] = None):
    """
    Trace triage/routing decision.

    Args:
        question: Student's question
        context: Additional context

    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        "chat.triage",
        attributes={
            "question.length": len(question),
            "has_code": bool(context and context.get("code")),
            "has_error": bool(context and context.get("error")),
        }
    )


def trace_agent_response(agent_type: str, question: str):
    """
    Trace agent response generation.

    Args:
        agent_type: Type of agent
        question: Student's question

    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        f"chat.agent.{agent_type}",
        attributes={
            "agent.type": agent_type,
            "question.length": len(question),
        }
    )


def record_routing_decision(
    span: trace.Span,
    agent_type: str,
    confidence: float,
    reasoning: str
):
    """
    Record routing decision in span.

    Args:
        span: Current span
        agent_type: Selected agent type
        confidence: Routing confidence (0-1)
        reasoning: Routing reasoning
    """
    span.set_attributes({
        "routing.agent": agent_type,
        "routing.confidence": confidence,
        "routing.reasoning": reasoning,
    })


def record_agent_metrics(
    span: trace.Span,
    response_length: int,
    processing_time_ms: float
):
    """
    Record agent response metrics.

    Args:
        span: Current span
        response_length: Length of response
        processing_time_ms: Processing time in milliseconds
    """
    span.set_attributes({
        "response.length": response_length,
        "processing.time_ms": processing_time_ms,
    })


def record_error(span: trace.Span, error: Exception):
    """
    Record error in span.

    Args:
        span: Current span
        error: Exception that occurred
    """
    span.set_status(Status(StatusCode.ERROR, str(error)))
    span.record_exception(error)
