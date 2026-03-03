"""Exercise API endpoints for LearnFlow platform."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.src.models.base import get_db
from backend.src.models.exercise import Exercise, DifficultyLevel
from backend.src.agents.exercise_generator import ExerciseGeneratorAgent
from backend.src.services.difficulty_service import DifficultyAdaptationService
from backend.src.services.exercise_validation_service import ExerciseValidationService
from backend.src.services.hint_service import HintService
from backend.src.events.exercise_events import get_exercise_event_publisher
from backend.src.observability.tracing import tracer


router = APIRouter(prefix="/api/exercises", tags=["exercises"])


# Request/Response models
class GenerateExerciseRequest(BaseModel):
    """Request model for generating an exercise."""
    student_id: int = Field(..., description="Student identifier")
    topic: str = Field(..., min_length=1, description="Python topic (e.g., loops, functions)")
    difficulty: Optional[str] = Field(None, description="Difficulty level (beginner, intermediate, advanced)")
    session_id: int = Field(..., description="Session identifier")


class GenerateExerciseResponse(BaseModel):
    """Response model for generated exercise."""
    exercise_id: int
    title: str
    instructions: str
    difficulty: str
    topic: str
    solution_template: Optional[str]
    expected_output: Optional[str]
    total_hints: int


class SubmitSolutionRequest(BaseModel):
    """Request model for submitting an exercise solution."""
    student_id: int = Field(..., description="Student identifier")
    exercise_id: int = Field(..., description="Exercise identifier")
    session_id: int = Field(..., description="Session identifier")
    solution_code: str = Field(..., min_length=1, description="Student's solution code")
    hints_used: int = Field(0, ge=0, description="Number of hints used")
    time_spent_seconds: Optional[float] = Field(None, ge=0, description="Time spent on exercise")


class SubmitSolutionResponse(BaseModel):
    """Response model for solution submission."""
    attempt_id: int
    is_correct: bool
    test_results: List[Dict[str, Any]]
    total_tests: int
    passed_tests: int
    feedback: str
    next_difficulty: Optional[str]


class GetHintsRequest(BaseModel):
    """Request model for getting hints."""
    student_id: int = Field(..., description="Student identifier")
    exercise_id: int = Field(..., description="Exercise identifier")
    hints_already_used: int = Field(0, ge=0, description="Number of hints already revealed")


class GetHintsResponse(BaseModel):
    """Response model for hints."""
    hint: Optional[Dict[str, Any]]
    has_more_hints: bool
    total_hints_available: int


# Endpoints
@router.post("/generate", response_model=GenerateExerciseResponse)
async def generate_exercise(
    request: GenerateExerciseRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a personalized exercise for a student.

    This endpoint generates a new exercise based on the student's skill level,
    topic, and performance history. Difficulty adapts automatically if not specified.

    Args:
        request: Exercise generation request with student_id, topic, optional difficulty
        db: Database session

    Returns:
        GenerateExerciseResponse with exercise details

    Raises:
        HTTPException: If generation fails
    """
    with tracer.start_as_current_span(
        "api.exercises.generate",
        attributes={
            "student_id": request.student_id,
            "topic": request.topic,
            "difficulty": request.difficulty or "auto"
        }
    ):
        try:
        # Initialize services
        exercise_agent = ExerciseGeneratorAgent()
        difficulty_service = DifficultyAdaptationService(db)
        hint_service = HintService(db)

        # Determine difficulty level
        if request.difficulty:
            difficulty = request.difficulty.lower()
        else:
            # Get adaptive difficulty based on student performance
            difficulty = difficulty_service.get_next_difficulty(
                student_id=request.student_id,
                topic=request.topic
            )

        # Get student context for personalization
        student_context = difficulty_service.get_adaptation_context(
            student_id=request.student_id,
            topic=request.topic
        )

        # Generate exercise using AI agent
        exercise_data = await exercise_agent.generate_exercise(
            topic=request.topic,
            difficulty=difficulty,
            student_context=student_context
        )

        # Map difficulty string to enum
        if difficulty == "beginner":
            difficulty_enum = DifficultyLevel.BEGINNER
        elif difficulty == "intermediate":
            difficulty_enum = DifficultyLevel.INTERMEDIATE
        elif difficulty == "advanced":
            difficulty_enum = DifficultyLevel.ADVANCED
        else:
            difficulty_enum = DifficultyLevel.BEGINNER

        # Create exercise in database
        import json
        exercise = Exercise(
            title=exercise_data.get("title", f"Python {request.topic.title()} Exercise"),
            instructions=exercise_data.get("instructions", ""),
            difficulty=difficulty_enum,
            topic=request.topic,
            test_cases=json.dumps(exercise_data.get("test_cases", [])),
            solution_template=exercise_data.get("solution_template"),
            expected_output=exercise_data.get("expected_output"),
            generated_for_student_id=request.student_id
        )

        db.add(exercise)
        db.commit()
        db.refresh(exercise)

        # Create hints for the exercise
        hints_data = exercise_data.get("hints", [])
        hint_service.create_hints_for_exercise(
            exercise_id=exercise.id,
            hints_data=hints_data
        )

        return GenerateExerciseResponse(
            exercise_id=exercise.id,
            title=exercise.title,
            instructions=exercise.instructions,
            difficulty=exercise.difficulty.value,
            topic=exercise.topic,
            solution_template=exercise.solution_template,
            expected_output=exercise.expected_output,
            total_hints=len(hints_data)
        )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate exercise: {str(e)}")


@router.post("/submit", response_model=SubmitSolutionResponse)
async def submit_solution(
    request: SubmitSolutionRequest,
    db: Session = Depends(get_db)
):
    """
    Submit and validate an exercise solution.

    This endpoint validates the student's solution against test cases,
    records the attempt, and provides feedback with next difficulty recommendation.

    Args:
        request: Solution submission request with exercise_id, solution_code, etc.
        db: Database session

    Returns:
        SubmitSolutionResponse with validation results and feedback

    Raises:
        HTTPException: If validation fails
    """
    with tracer.start_as_current_span(
        "api.exercises.submit",
        attributes={
            "student_id": request.student_id,
            "exercise_id": request.exercise_id,
            "hints_used": request.hints_used
        }
    ):
        try:
        # Initialize services
        validation_service = ExerciseValidationService(db)
        difficulty_service = DifficultyAdaptationService(db)

        # Validate solution
        validation_result = validation_service.validate_solution(
            exercise_id=request.exercise_id,
            solution_code=request.solution_code,
            student_id=request.student_id,
            session_id=request.session_id,
            hints_used=request.hints_used,
            time_spent_seconds=request.time_spent_seconds
        )

        if not validation_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=validation_result.get("error", "Validation failed")
            )

        # Get exercise for topic
        exercise = db.query(Exercise).filter(Exercise.id == request.exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Determine next difficulty
        next_difficulty = difficulty_service.get_next_difficulty(
            student_id=request.student_id,
            topic=exercise.topic,
            current_difficulty=exercise.difficulty.value
        )

        # Publish exercise completion event
        event_publisher = get_exercise_event_publisher()
        await event_publisher.publish_exercise_completion(
            student_id=request.student_id,
            exercise_id=request.exercise_id,
            attempt_id=validation_result.get("attempt_id"),
            is_correct=validation_result.get("is_correct", False),
            hints_used=request.hints_used,
            time_spent_seconds=request.time_spent_seconds or 0.0,
            test_results=validation_result.get("test_results", []),
            difficulty=exercise.difficulty.value,
            topic=exercise.topic
        )

        # Generate feedback
        is_correct = validation_result.get("is_correct", False)
        passed_tests = validation_result.get("passed_tests", 0)
        total_tests = validation_result.get("total_tests", 0)

        if is_correct:
            feedback = f"Excellent work! You passed all {total_tests} test cases. "
            if next_difficulty != exercise.difficulty.value:
                feedback += f"Ready for a {next_difficulty} challenge?"
            else:
                feedback += "Keep practicing to master this topic!"
        else:
            feedback = f"You passed {passed_tests} out of {total_tests} test cases. "
            if request.hints_used < 3:
                feedback += "Try requesting a hint if you're stuck!"
            else:
                feedback += "Review the test results and try again."

        return SubmitSolutionResponse(
            attempt_id=validation_result.get("attempt_id"),
            is_correct=is_correct,
            test_results=validation_result.get("test_results", []),
            total_tests=total_tests,
            passed_tests=passed_tests,
            feedback=feedback,
            next_difficulty=next_difficulty if is_correct else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit solution: {str(e)}")


@router.get("/hints", response_model=GetHintsResponse)
async def get_hints(
    student_id: int,
    exercise_id: int,
    hints_already_used: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get the next hint for an exercise.

    This endpoint provides progressive hints (vague → moderate → specific)
    to guide students without giving away the solution.

    Args:
        student_id: Student identifier
        exercise_id: Exercise identifier
        hints_already_used: Number of hints already revealed
        db: Database session

    Returns:
        GetHintsResponse with next hint and availability info

    Raises:
        HTTPException: If exercise not found
    """
    try:
        # Initialize hint service
        hint_service = HintService(db)

        # Check if exercise exists
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # Get next hint
        next_hint = hint_service.get_next_hint(
            exercise_id=exercise_id,
            student_id=student_id,
            hints_already_used=hints_already_used
        )

        # Get total hints available
        all_hints = hint_service.get_all_hints(exercise_id=exercise_id)
        total_hints = len(all_hints)

        return GetHintsResponse(
            hint=next_hint,
            has_more_hints=(hints_already_used + 1) < total_hints,
            total_hints_available=total_hints
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hints: {str(e)}")
