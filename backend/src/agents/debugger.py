"""Debugger Agent for LearnFlow platform."""
from typing import List, Dict, Any, Optional
from backend.src.agents.client import get_agent_client


class DebuggerAgent:
    """
    AI agent that helps students debug code through guided problem-solving.

    This agent teaches debugging skills by asking diagnostic questions
    rather than pointing out errors directly.
    """

    def __init__(self):
        """Initialize DebuggerAgent."""
        self.client = get_agent_client()
        self.system_prompt = """You are a debugging coach for Python students.

Your role:
- Help students find and fix bugs through systematic debugging
- Ask diagnostic questions to guide their investigation
- Teach debugging strategies (print statements, reading errors, testing assumptions)
- Never point directly to the bug - help them discover it
- Build debugging confidence and independence

Debugging process:
1. Ask what they expected vs. what happened
2. Guide them to isolate the problem area
3. Help them form hypotheses about the cause
4. Suggest ways to test their hypotheses
5. Celebrate when they find the bug themselves

Guidelines:
- Read error messages together and explain what they mean
- Encourage adding print statements to inspect values
- Ask about edge cases and assumptions
- If completely stuck, give a tiny hint about WHERE to look, not WHAT the bug is
- Teach the skill of debugging, not just fixing this one bug

Remember: A student who learns to debug is a student who can solve future problems independently."""

    async def help_debug(
        self,
        code: str,
        error_message: Optional[str],
        student_description: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Help student debug their code through guided questions.

        Args:
            code: Student's code that has a bug
            error_message: Error message if any
            student_description: Student's description of the problem
            conversation_history: Previous messages in the conversation
            context: Additional context (previous attempts, test cases)

        Returns:
            Agent's response as a string
        """
        # Build messages for the API
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current debugging request
        user_message = f"Student needs help debugging:\n\nCode:\n```python\n{code}\n```\n\n"
        if error_message:
            user_message += f"Error: {error_message}\n\n"
        user_message += f"Student says: {student_description}"

        if context:
            user_message += f"\n\nAdditional context: {context}"

        messages.append({"role": "user", "content": user_message})

        # Get response from Groq API
        response = await self.client.create_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        return response.choices[0].message.content

    async def stream_debug_help(
        self,
        code: str,
        error_message: Optional[str],
        student_description: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream debugging help for real-time display.

        Args:
            code: Student's code that has a bug
            error_message: Error message if any
            student_description: Student's description of the problem
            conversation_history: Previous messages in the conversation
            context: Additional context

        Yields:
            Response chunks as they arrive
        """
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        messages.extend(conversation_history)

        user_message = f"Student needs help debugging:\n\nCode:\n```python\n{code}\n```\n\n"
        if error_message:
            user_message += f"Error: {error_message}\n\n"
        user_message += f"Student says: {student_description}"

        if context:
            user_message += f"\n\nAdditional context: {context}"

        messages.append({"role": "user", "content": user_message})

        # Stream response
        async for chunk in self.client.create_streaming_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=600
        ):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return "debugger"
