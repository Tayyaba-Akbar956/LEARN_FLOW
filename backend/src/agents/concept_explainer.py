"""Concept Explainer Agent for LearnFlow platform."""
from typing import List, Dict, Any, Optional
from backend.src.agents.client import get_agent_client


class ConceptExplainerAgent:
    """
    AI agent that explains programming concepts using Socratic method.

    This agent helps students understand concepts through guided questions
    rather than direct answers, promoting discovery-based learning.
    """

    def __init__(self):
        """Initialize ConceptExplainerAgent."""
        self.client = get_agent_client()
        self.system_prompt = """You are a patient Python tutor using the Socratic method.

Your role:
- Help students discover concepts through guided questions
- Never give direct answers - ask leading questions instead
- Break complex concepts into smaller, manageable pieces
- Encourage students to think critically and make connections
- Provide hints when students are stuck, but let them reach conclusions

Guidelines:
- Ask 1-2 questions at a time, not overwhelming lists
- Build on student's current understanding
- Use analogies and real-world examples
- Celebrate small victories and progress
- If student is completely lost, provide a tiny hint and ask again

Remember: Your goal is understanding, not just correct answers."""

    async def explain_concept(
        self,
        concept: str,
        student_question: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Explain a programming concept using Socratic questioning.

        Args:
            concept: The concept to explain (e.g., "loops", "functions")
            student_question: Student's original question
            conversation_history: Previous messages in the conversation
            context: Additional context (code snippets, previous attempts)

        Returns:
            Agent's response as a string
        """
        # Build messages for the API
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current question with context
        user_message = f"Student asks about '{concept}': {student_question}"
        if context:
            user_message += f"\n\nContext: {context}"

        messages.append({"role": "user", "content": user_message})

        # Get response from Groq API
        response = await self.client.create_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    async def stream_explanation(
        self,
        concept: str,
        student_question: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream explanation response for real-time display.

        Args:
            concept: The concept to explain
            student_question: Student's original question
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

        user_message = f"Student asks about '{concept}': {student_question}"
        if context:
            user_message += f"\n\nContext: {context}"

        messages.append({"role": "user", "content": user_message})

        # Stream response
        async for chunk in self.client.create_streaming_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        ):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return "concept_explainer"
