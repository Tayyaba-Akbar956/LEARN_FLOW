"""Chat Service for LearnFlow.

Manages conversation flow, agent handoffs, and context tracking.
"""
from typing import Dict, Any, Optional, List
from backend.src.agents import ConceptExplainerAgent, DebuggerAgent, HintProviderAgent
from backend.src.services.triage_service import TriageService


class ChatService:
    """
    Manages chat conversations between students and AI agents.

    Responsibilities:
    - Route questions to appropriate agents via TriageService
    - Maintain conversation context
    - Handle agent handoffs
    - Track conversation history
    """

    def __init__(self):
        """Initialize ChatService with agents and triage."""
        self.triage = TriageService()
        self.concept_explainer = ConceptExplainerAgent()
        self.debugger = DebuggerAgent()
        self.hint_provider = HintProviderAgent()

    async def process_message(
        self,
        message: str,
        student_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        current_code: Optional[str] = None,
        execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a student message and generate response.

        Args:
            message: Student's message
            student_id: Student identifier
            session_id: Session identifier
            context: Optional context (code, error, exercise, history)
            current_code: Current code in editor (if applicable)
            execution_result: Latest execution result (if applicable)

        Returns:
            Dictionary with response and metadata
        """
        # Enrich context with code editor state
        if context is None:
            context = {}

        if current_code:
            context["code"] = current_code

        if execution_result:
            context["execution_result"] = execution_result
            # Extract error from execution result if present
            if execution_result.get("stderr"):
                context["error"] = execution_result["stderr"]

        # Route to appropriate agent
        routing = self.triage.route_question(message, context)
        agent_type = routing["agent_type"]

        # Get response from agent
        if agent_type == "concept_explainer":
            response = self.concept_explainer.explain(
                question=message,
                student_context=context
            )
            agent_info = self.concept_explainer.get_agent_info()

        elif agent_type == "debugger":
            code = context.get("code", "") if context else ""
            error = context.get("error", "") if context else ""

            debug_result = self.debugger.debug(
                code=code,
                error=error,
                student_context=context
            )
            response = debug_result["response"]
            agent_info = self.debugger.get_agent_info()

            # Add escalation flag if needed
            if debug_result.get("should_escalate"):
                agent_info["should_escalate"] = True
                agent_info["escalation_reason"] = "Student struggling with same error 3+ times"

        elif agent_type == "hint_provider":
            exercise = context.get("exercise", "") if context else ""
            student_code = context.get("code", "") if context else None
            hint_level = context.get("hint_level", 1) if context else 1

            hint_result = self.hint_provider.provide_hint(
                exercise=exercise,
                student_code=student_code,
                hint_level=hint_level,
                student_context=context
            )
            response = hint_result["hint"]
            agent_info = self.hint_provider.get_agent_info()
            agent_info["hint_level"] = hint_result["hint_level"]
            agent_info["next_hint_available"] = hint_result["next_hint_available"]

        else:
            # Fallback
            response = "I'm not sure how to help with that. Can you rephrase your question?"
            agent_info = {"type": "unknown", "name": "Unknown"}

        return {
            "response": response,
            "agent": agent_info,
            "routing": routing,
            "student_id": student_id,
            "session_id": session_id
        }

    def get_conversation_summary(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary of conversation.

        Args:
            messages: List of message dictionaries

        Returns:
            Summary with statistics
        """
        total_messages = len(messages)
        student_messages = sum(1 for m in messages if m.get("role") == "student")
        agent_messages = sum(1 for m in messages if m.get("role") == "agent")

        # Count agent types used
        agent_types = {}
        for m in messages:
            if m.get("role") == "agent" and m.get("agent_type"):
                agent_type = m["agent_type"]
                agent_types[agent_type] = agent_types.get(agent_type, 0) + 1

        return {
            "total_messages": total_messages,
            "student_messages": student_messages,
            "agent_messages": agent_messages,
            "agents_used": agent_types,
            "conversation_active": True
        }
