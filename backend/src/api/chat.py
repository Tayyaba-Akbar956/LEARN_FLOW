"""Chat API endpoints for LearnFlow platform."""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from backend.src.services.chat_service import ChatService
from backend.src.services.session_service import SessionService


router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize services
chat_service = ChatService()
session_service = SessionService()


# Request/Response models
class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    session_id: int = Field(..., description="Session identifier")
    student_id: int = Field(..., description="Student identifier")
    message: str = Field(..., min_length=1, description="Message content")
    code: Optional[str] = Field(None, description="Student's code (if any)")
    error_message: Optional[str] = Field(None, description="Error message (if any)")
    execution_result: Optional[Dict[str, Any]] = Field(None, description="Latest code execution result")


class ChatMessageResponse(BaseModel):
    """Response model for chat message."""
    student_message: Dict[str, Any]
    agent_response: Dict[str, Any]
    agent_type: str
    routing_confidence: float


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[Dict[str, Any]]
    total: int
    session_id: int


# Endpoints
@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a message and get AI agent response.

    This endpoint processes a student message, routes it to the appropriate
    AI agent, and returns the agent's response.

    Args:
        request: Chat message request with session_id, student_id, message, optional code/error/execution_result

    Returns:
        ChatMessageResponse with student message, agent response, and routing info

    Raises:
        HTTPException: If session not found or processing fails
    """
    try:
        # Build context from request
        context = {}
        if request.code:
            context["code"] = request.code
        if request.error_message:
            context["error"] = request.error_message
        if request.execution_result:
            context["execution_result"] = request.execution_result

        result = await chat_service.process_message(
            message=request.message,
            student_id=str(request.student_id),
            session_id=str(request.session_id),
            context=context if context else None,
            current_code=request.code,
            execution_result=request.execution_result
        )

        return ChatMessageResponse(
            student_message={
                "role": "student",
                "content": request.message,
                "code": request.code,
                "error": request.error_message
            },
            agent_response={
                "role": "agent",
                "content": result["response"],
                "agent": result["agent"]
            },
            agent_type=result["agent"]["type"],
            routing_confidence=result["routing"].get("confidence", 1.0)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: int,
    limit: int = 50,
    offset: int = 0
):
    """
    Get chat history for a session.

    Retrieves paginated chat history including all messages between
    student and AI agents.

    Args:
        session_id: Session identifier
        limit: Maximum number of messages to return (default: 50)
        offset: Number of messages to skip (default: 0)

    Returns:
        ChatHistoryResponse with messages and pagination info

    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        # Verify session exists
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Get messages
        messages = await chat_service.get_chat_history(
            session_id=session_id,
            limit=limit,
            offset=offset
        )

        return ChatHistoryResponse(
            messages=messages,
            total=len(messages),  # TODO: Get actual total count from database
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")


@router.websocket("/stream")
async def websocket_chat_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming chat responses.

    Accepts student messages via WebSocket and streams AI agent responses
    in real-time for better user experience.

    Protocol:
        Client sends: {"session_id": int, "student_id": int, "message": str, "code": str?, "error_message": str?, "execution_result": dict?}
        Server streams: {"type": "chunk", "content": str} or {"type": "done", "agent_type": str}
        Server sends error: {"type": "error", "message": str}

    Args:
        websocket: WebSocket connection

    Raises:
        WebSocketDisconnect: When client disconnects
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            session_id = data.get("session_id")
            student_id = data.get("student_id")
            message = data.get("message")
            code = data.get("code")
            error_message = data.get("error_message")
            execution_result = data.get("execution_result")

            if not session_id or not student_id or not message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Missing required fields: session_id, student_id, message"
                })
                continue

            try:
                # Build context
                context = {}
                if code:
                    context["code"] = code
                if error_message:
                    context["error"] = error_message
                if execution_result:
                    context["execution_result"] = execution_result

                # Process message
                result = await chat_service.process_message(
                    message=message,
                    student_id=str(student_id),
                    session_id=str(session_id),
                    context=context if context else None,
                    current_code=code,
                    execution_result=execution_result
                )

                # Send response
                await websocket.send_json({
                    "type": "message",
                    "content": result["response"],
                    "agent": result["agent"]
                })

                # Send completion signal
                await websocket.send_json({
                    "type": "done",
                    "agent_type": result["agent"]["type"]
                })

            except ValueError as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Failed to process message: {str(e)}"
                })

    except WebSocketDisconnect:
        pass  # Client disconnected, clean up handled by FastAPI
