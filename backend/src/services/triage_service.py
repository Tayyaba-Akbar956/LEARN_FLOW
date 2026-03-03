"""Triage service for routing student questions to appropriate agents."""
from typing import Dict, Any, Optional
from backend.src.agents.client import get_agent_client


class TriageService:
    """
    Service that analyzes student questions and routes them to the appropriate AI agent.

    Uses AI to classify the type of help needed and select the best agent.
    """

    def __init__(self):
        """Initialize TriageService."""
        self.client = get_agent_client()
        self.system_prompt = """You are a triage system for a Python tutoring platform.

Your job: Analyze student questions and determine which agent should handle them.

Available agents:
1. concept_explainer - For understanding concepts, theory, "what is X?", "how does Y work?"
2. debugger - For fixing broken code, errors, "why doesn't this work?", "I get an error"
3. hint_provider - For exercise help, "I'm stuck", "give me a hint", working on specific problems

Classification rules:
- If asking about concepts/theory → concept_explainer
- If code has errors or bugs → debugger
- If working on exercise and stuck → hint_provider
- If unclear, default to concept_explainer (safest choice)

Respond with ONLY a JSON object:
{
  "agent": "agent_name",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""

    async def route_question(
        self,
        question: str,
        code: Optional[str] = None,
        error_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a student question to the appropriate agent.

        Args:
            question: Student's question
            code: Student's code (if any)
            error_message: Error message (if any)
            context: Additional context (exercise description, session history)

        Returns:
            Dictionary with agent selection and routing info:
            {
                "agent": "agent_name",
                "confidence": float,
                "reasoning": str
            }
        """
        # Build triage request
        user_message = f"Student question: {question}\n\n"

        if code:
            user_message += f"Student's code:\n```python\n{code}\n```\n\n"

        if error_message:
            user_message += f"Error message: {error_message}\n\n"

        if context:
            if context.get("exercise_description"):
                user_message += f"Working on exercise: {context['exercise_description']}\n\n"
            if context.get("current_topic"):
                user_message += f"Current topic: {context['current_topic']}\n\n"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Get routing decision from AI
        response = await self.client.create_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent routing
            max_tokens=200
        )

        # Parse response
        import json
        try:
            routing = json.loads(response.choices[0].message.content)
            return routing
        except json.JSONDecodeError:
            # Fallback to concept_explainer if parsing fails
            return {
                "agent": "concept_explainer",
                "confidence": 0.5,
                "reasoning": "Failed to parse routing decision, defaulting to concept explainer"
            }

    def get_agent_by_name(self, agent_name: str):
        """
        Get agent instance by name.

        Args:
            agent_name: Name of the agent (concept_explainer, debugger, hint_provider)

        Returns:
            Agent instance

        Raises:
            ValueError: If agent name is invalid
        """
        from backend.src.agents.concept_explainer import ConceptExplainerAgent
        from backend.src.agents.debugger import DebuggerAgent
        from backend.src.agents.hint_provider import HintProviderAgent

        agents = {
            "concept_explainer": ConceptExplainerAgent,
            "debugger": DebuggerAgent,
            "hint_provider": HintProviderAgent,
        }

        if agent_name not in agents:
            raise ValueError(f"Unknown agent: {agent_name}")

        return agents[agent_name]()

    async def route_and_respond(
        self,
        question: str,
        conversation_history: list,
        code: Optional[str] = None,
        error_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route question and get response from selected agent.

        Args:
            question: Student's question
            conversation_history: Previous messages
            code: Student's code (if any)
            error_message: Error message (if any)
            context: Additional context

        Returns:
            Dictionary with agent info and response:
            {
                "agent_type": str,
                "confidence": float,
                "reasoning": str,
                "response": str
            }
        """
        # Route to appropriate agent
        routing = await self.route_question(question, code, error_message, context)

        # Get agent instance
        agent = self.get_agent_by_name(routing["agent"])

        # Get response based on agent type
        if routing["agent"] == "concept_explainer":
            response = await agent.explain_concept(
                concept=context.get("current_topic", "Python") if context else "Python",
                student_question=question,
                conversation_history=conversation_history,
                context=context
            )
        elif routing["agent"] == "debugger":
            response = await agent.help_debug(
                code=code or "",
                error_message=error_message,
                student_description=question,
                conversation_history=conversation_history,
                context=context
            )
        elif routing["agent"] == "hint_provider":
            response = await agent.provide_hint(
                exercise_description=context.get("exercise_description", "") if context else "",
                student_code=code,
                student_question=question,
                previous_hints=context.get("previous_hints", []) if context else [],
                conversation_history=conversation_history,
                context=context
            )
        else:
            response = "I'm not sure how to help with that. Could you rephrase your question?"

        return {
            "agent_type": routing["agent"],
            "confidence": routing["confidence"],
            "reasoning": routing["reasoning"],
            "response": response
        }
