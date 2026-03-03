"""Exercise Validation Service for LearnFlow platform."""
from typing import Dict, Any, List, Optional
import subprocess
import json
import tempfile
import os
from datetime import datetime
from sqlalchemy.orm import Session
from backend.src.models.exercise import Exercise
from backend.src.models.exercise_attempt import ExerciseAttempt
from backend.src.observability.tracing import trace_function


class ExerciseValidationService:
    """
    Service that validates student solutions against exercise test cases.

    Executes student code in a sandbox and compares output against
    expected results from test cases.
    """

    def __init__(self, db: Session):
        """
        Initialize ExerciseValidationService.

        Args:
            db: Database session
        """
        self.db = db
        self.timeout_seconds = 5
        self.max_memory_mb = 256

    @trace_function(name="exercise_validation.validate_solution")
    def validate_solution(
        self,
        exercise_id: int,
        solution_code: str,
        student_id: int,
        session_id: int,
        hints_used: int = 0,
        time_spent_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate a student's solution against exercise test cases.

        Args:
            exercise_id: Exercise identifier
            solution_code: Student's solution code
            student_id: Student identifier
            session_id: Session identifier
            hints_used: Number of hints used
            time_spent_seconds: Time spent on exercise

        Returns:
            Dictionary with validation results
        """
        # Get exercise from database
        exercise = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            return {
                "success": False,
                "error": "Exercise not found",
                "is_correct": False
            }

        # Parse test cases
        try:
            test_cases = json.loads(exercise.test_cases)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid test cases format",
                "is_correct": False
            }

        # Run test cases
        test_results = []
        all_passed = True

        for i, test_case in enumerate(test_cases):
            result = self._run_test_case(solution_code, test_case)
            test_results.append(result)
            if not result["passed"]:
                all_passed = False

        # Create exercise attempt record
        attempt = ExerciseAttempt(
            student_id=student_id,
            exercise_id=exercise_id,
            session_id=session_id,
            solution_code=solution_code,
            is_correct=all_passed,
            test_results=json.dumps(test_results),
            hints_used=hints_used,
            time_spent_seconds=time_spent_seconds,
            submitted_at=datetime.utcnow(),
            validated_at=datetime.utcnow()
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "success": True,
            "is_correct": all_passed,
            "test_results": test_results,
            "attempt_id": attempt.id,
            "total_tests": len(test_cases),
            "passed_tests": sum(1 for r in test_results if r["passed"])
        }

    @trace_function(name="exercise_validation.run_test_case")
    def _run_test_case(
        self,
        solution_code: str,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single test case against the solution code.

        Args:
            solution_code: Student's solution code
            test_case: Test case with input and expected output

        Returns:
            Dictionary with test result
        """
        test_input = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "")
        description = test_case.get("description", "Test case")

        # Create test code that includes the solution and test input
        test_code = f"""
{solution_code}

# Test input
test_input = {repr(test_input)}

# Execute test
try:
    result = main(test_input) if 'main' in dir() else eval(test_input)
    print(result)
except Exception as e:
    print(f"ERROR: {{e}}")
"""

        # Execute in sandbox
        execution_result = self._execute_in_sandbox(test_code)

        # Check if output matches expected
        actual_output = execution_result.get("output", "").strip()
        expected_str = str(expected_output).strip()

        passed = (
            execution_result.get("exit_code") == 0 and
            not execution_result.get("error") and
            actual_output == expected_str
        )

        return {
            "description": description,
            "input": test_input,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "passed": passed,
            "error": execution_result.get("error"),
            "execution_time_ms": execution_result.get("execution_time_ms", 0)
        }

    @trace_function(name="exercise_validation.execute_in_sandbox")
    def _execute_in_sandbox(self, code: str) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment.

        Args:
            code: Python code to execute

        Returns:
            Dictionary with execution results
        """
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            start_time = datetime.utcnow()

            # Execute with resource limits
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env={
                    "PYTHONPATH": "",
                    "PATH": "/usr/bin:/bin"
                }
            )

            end_time = datetime.utcnow()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            # Clean up temp file
            os.unlink(temp_file)

            return {
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "exit_code": result.returncode,
                "execution_time_ms": execution_time_ms
            }

        except subprocess.TimeoutExpired:
            # Clean up temp file
            if 'temp_file' in locals():
                os.unlink(temp_file)

            return {
                "output": "",
                "error": f"Execution timed out (limit: {self.timeout_seconds}s)",
                "exit_code": 1,
                "execution_time_ms": self.timeout_seconds * 1000
            }

        except Exception as e:
            # Clean up temp file
            if 'temp_file' in locals():
                os.unlink(temp_file)

            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": 1,
                "execution_time_ms": 0
            }

    def get_attempt_history(
        self,
        student_id: int,
        exercise_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get student's exercise attempt history.

        Args:
            student_id: Student identifier
            exercise_id: Optional exercise filter
            limit: Maximum number of attempts to return

        Returns:
            List of attempt dictionaries
        """
        query = self.db.query(ExerciseAttempt).filter(
            ExerciseAttempt.student_id == student_id
        )

        if exercise_id:
            query = query.filter(ExerciseAttempt.exercise_id == exercise_id)

        attempts = query.order_by(
            ExerciseAttempt.submitted_at.desc()
        ).limit(limit).all()

        return [attempt.to_dict() for attempt in attempts]
