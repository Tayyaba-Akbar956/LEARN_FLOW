"""Hint Provider Agent for LearnFlow platform."""
from typing import List, Dict, Any, Optional
from backend.src.agents.client import get_agent_client


class HintProviderAgent:
    """
    AI agent that provides progressive hints for exercises.

    This agent gives hints that start vague and become more specific,
    helping students make progress without giving away the solution.
    """

    def __init__(self):
        """Initialize HintProviderAgent."""
        self.client = get_agent_client()
        self.system_prompt = """You are a hint provider for Python programming exercises.

Your role:
- Provide progressive hints that guide without solving
- Start with conceptual hints, then strategic hints, then tactical hints
- Never give the complete solution
- Help students make progress when stuck
- Maintain the challenge and learning opportunity

Hint progression levels:
1. Conceptual: What approach or concept might help? (e.g., "Think about using a loop")
2. Strategic: What steps are needed? (e.g., "You'll need to iterate and keep track of a count")
3. Tactical: More specific guidance (e.g., "Initialize a counter before the loop")
4. Near-solution: Very specific but still requires student to write code (e.g., "Use a variable like 'count = 0' before your for loop")

Guidelines:
- Assess how stuck the student is from their question
- Give the minimum hint needed to unstick them
- If they ask for "the answer", explain why discovering it themselves is better
- Encourage them after each hint
- If they've had 3+ hints, suggest they're very close

Remember: The goal is progress, not perfection. A small hint that gets them moving is better than a complete solution."""

    async def provide_hint(
        self,
        exercise_description: str,
        student_code: Optional[str],
        student_question: str,
        previous_hints: List[str],
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Provide a progressive hint for an exercise.

        Args:
            exercise_description: Description of the exercise
            student_code: Student's current code attempt (if any)
            student_question: Student's question or request for help
            previous_hints: List of hints already given
            conversation_history: Previous messages in the conversation
            context: Additional context (test results, error messages)

        Returns:
            Agent's hint as a string
        """
        # Build messages for the API
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current hint request
        user_message = f"Exercise: {exercise_description}\n\n"

        if student_code:
            user_message += f"Student's current code:\n```python\n{student_code}\n```\n\n"

        user_message += f"Student asks: {student_question}\n\n"

        if previous_hints:
            user_message += f"Previous hints given ({len(previous_hints)}):\n"
            for i, hint in enumerate(previous_hints, 1):
                user_message += f"{i}. {hint}\n"
            user_message += "\n"

        if context:
            user_message += f"Additional context: {context}\n\n"

        user_message += f"Provide hint level {len(previous_hints) + 1}."

        messages.append({"role": "user", "content": user_message})

        # Get response from Groq API
        response = await self.client.create_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )

        return response.choices[0].message.content

    async def stream_hint(
        self,
        exercise_description: str,
        student_code: Optional[str],
        student_question: str,
        previous_hints: List[str],
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream hint response for real-time display.

        Args:
            exercise_description: Description of the exercise
            student_code: Student's current code attempt
            student_question: Student's question
            previous_hints: List of hints already given
            conversation_history: Previous messages
            context: Additional context

        Yields:
            Response chunks as they arrive
        """
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        messages.extend(conversation_history)

        user_message = f"Exercise: {exercise_description}\n\n"

        if student_code:
            user_message += f"Student's current code:\n```python\n{student_code}\n```\n\n"

        user_message += f"Student asks: {student_question}\n\n"

        if previous_hints:
            user_message += f"Previous hints given ({len(previous_hints)}):\n"
            for i, hint in enumerate(previous_hints, 1):
                user_message += f"{i}. {hint}\n"
            user_message += "\n"

        if context:
            user_message += f"Additional context: {context}\n\n"

        user_message += f"Provide hint level {len(previous_hints) + 1}."

        messages.append({"role": "user", "content": user_message})

        # Stream response
        async for chunk in self.client.create_streaming_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=400
        ):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return "hint_provider"
