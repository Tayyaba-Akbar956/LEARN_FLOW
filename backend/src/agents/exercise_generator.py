"""Exercise Generator Agent for LearnFlow platform."""
from typing import Dict, Any, Optional, List
import json
from backend.src.agents.client import get_agent_client
from backend.src.observability.tracing import trace_function


class ExerciseGeneratorAgent:
    """
    AI agent that generates personalized Python exercises.

    This agent creates exercises dynamically based on student skill level,
    recent topics, and performance history. Exercises include instructions,
    test cases, and progressive hints.
    """

    def __init__(self):
        """Initialize ExerciseGeneratorAgent."""
        self.client = get_agent_client()
        self.system_prompt = """You are an expert Python exercise generator for LearnFlow.

Your role:
- Generate personalized Python exercises based on student skill level and topic
- Create clear, achievable exercises that challenge without overwhelming
- Include comprehensive test cases for automatic validation
- Generate progressive hints (vague → moderate → specific)
- Ensure exercises are appropriate for the difficulty level

Exercise difficulty guidelines:
- BEGINNER: Basic syntax, simple operations, single concepts
- INTERMEDIATE: Multiple concepts, problem-solving, basic algorithms
- ADVANCED: Complex algorithms, optimization, multiple integrated concepts

Output format (JSON):
{
  "title": "Exercise title",
  "instructions": "Clear, detailed instructions",
  "difficulty": "beginner|intermediate|advanced",
  "topic": "Python topic (e.g., loops, functions, lists)",
  "test_cases": [
    {"input": "test input", "expected_output": "expected result", "description": "what this tests"}
  ],
  "solution_template": "# Optional starter code",
  "expected_output": "Description of expected output",
  "hints": [
    {"level": "vague", "sequence": 1, "content": "General direction hint"},
    {"level": "moderate", "sequence": 2, "content": "More specific hint"},
    {"level": "specific", "sequence": 3, "content": "Very specific hint"}
  ]
}

Remember: Exercises should promote learning through doing, not just copying solutions."""

    @trace_function(name="exercise_generator.generate_exercise")
    async def generate_exercise(
        self,
        topic: str,
        difficulty: str,
        student_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized Python exercise.

        Args:
            topic: Python topic (e.g., "loops", "functions", "lists")
            difficulty: Difficulty level ("beginner", "intermediate", "advanced")
            student_context: Optional context about student's recent work and performance

        Returns:
            Dictionary containing exercise details, test cases, and hints
        """
        # Build the generation prompt
        user_message = f"""Generate a Python exercise on the topic '{topic}' at '{difficulty}' difficulty level.

Student context: {json.dumps(student_context) if student_context else 'No prior context'}

Requirements:
- Clear, achievable instructions
- 3-5 test cases covering edge cases
- 3 progressive hints (vague, moderate, specific)
- Appropriate for {difficulty} level
- Promotes discovery-based learning

Return ONLY valid JSON matching the specified format."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Get response from Groq API
        response = await self.client.create_completion(
            messages=messages,
            temperature=0.8,  # Higher temperature for creative exercise generation
            max_tokens=1500
        )

        # Parse JSON response
        content = response.choices[0].message.content.strip()

        # Extract JSON from markdown code blocks if present
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()

        try:
            exercise_data = json.loads(content)
            return exercise_data
        except json.JSONDecodeError as e:
            # Fallback: return a basic exercise structure
            return {
                "title": f"Python {topic.title()} Exercise",
                "instructions": f"Practice {topic} concepts at {difficulty} level.",
                "difficulty": difficulty,
                "topic": topic,
                "test_cases": [
                    {"input": "", "expected_output": "", "description": "Basic test"}
                ],
                "solution_template": "# Write your solution here\n",
                "expected_output": "Complete the exercise according to instructions",
                "hints": [
                    {"level": "vague", "sequence": 1, "content": f"Think about how {topic} work in Python"},
                    {"level": "moderate", "sequence": 2, "content": f"Consider using Python's {topic} syntax"},
                    {"level": "specific", "sequence": 3, "content": f"Review the {topic} documentation"}
                ]
            }

    async def adapt_exercise_difficulty(
        self,
        original_exercise: Dict[str, Any],
        performance_data: Dict[str, Any],
        direction: str  # "easier" or "harder"
    ) -> Dict[str, Any]:
        """
        Adapt an existing exercise to be easier or harder based on performance.

        Args:
            original_exercise: The original exercise data
            performance_data: Student's performance on the original exercise
            direction: "easier" or "harder"

        Returns:
            Modified exercise with adjusted difficulty
        """
        user_message = f"""Adapt this exercise to be {direction}:

Original exercise:
{json.dumps(original_exercise, indent=2)}

Student performance:
{json.dumps(performance_data, indent=2)}

Make the exercise {direction} while keeping the same topic and learning objectives.
Return ONLY valid JSON matching the exercise format."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = await self.client.create_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from markdown code blocks if present
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()

        try:
            adapted_exercise = json.loads(content)
            return adapted_exercise
        except json.JSONDecodeError:
            # Return original if parsing fails
            return original_exercise

    def get_agent_type(self) -> str:
        """Get agent type identifier."""
        return "exercise_generator"
