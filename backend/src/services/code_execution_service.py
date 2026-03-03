"""Code execution service for LearnFlow platform."""
from typing import Dict, Any, Optional
from datetime import datetime
from backend.src.sandbox.sandbox_service import SandboxService
from backend.src.observability.tracing import tracer


class CodeExecutionService:
    """
    Service for managing code execution requests.

    Validates code, executes in sandbox, captures output, and stores results.
    """

    def __init__(self, sandbox_service: Optional[SandboxService] = None, db_client=None):
        """
        Initialize CodeExecutionService.

        Args:
            sandbox_service: Sandbox service for code execution
            db_client: Database client for storing submissions
        """
        self.sandbox = sandbox_service or SandboxService()
        self.db = db_client

    async def execute_code(
        self,
        code: str,
        student_id: int,
        session_id: int
    ) -> Dict[str, Any]:
        """
        Execute student code and return results.

        Args:
            code: Python code to execute
            student_id: Student identifier
            session_id: Session identifier

        Returns:
            Dictionary with submission and execution result
        """
        with tracer.start_as_current_span(
            "code_execution.execute",
            attributes={
                "student_id": student_id,
                "session_id": session_id,
                "code_length": len(code)
            }
        ) as span:
            # Create code submission record
            submission = await self.create_submission(
                code=code,
                student_id=student_id,
                session_id=session_id
            )

            # Update status to running
            await self.update_submission_status(submission["id"], "running")

            # Execute code in sandbox
            with tracer.start_as_current_span("code_execution.sandbox_execute"):
                execution_result = await self.sandbox.execute_code(code, student_id)

            span.set_attribute("execution.exit_code", execution_result["exit_code"])
            span.set_attribute("execution.timed_out", execution_result["timed_out"])
            span.set_attribute("execution.time_ms", execution_result["execution_time_ms"])

            # Create execution result record
            result = await self.create_execution_result(
                submission_id=submission["id"],
                **execution_result
            )

            # Update submission status
            final_status = "completed" if not execution_result["timed_out"] else "timeout"
            if execution_result["exit_code"] != 0 and not execution_result["timed_out"]:
                final_status = "failed"

            await self.update_submission_status(submission["id"], final_status)

            span.set_attribute("submission.status", final_status)

            return {
                "submission": submission,
                "result": result,
                "success": execution_result["exit_code"] == 0 and not execution_result["timed_out"]
            }

    async def create_submission(
        self,
        code: str,
        student_id: int,
        session_id: int
    ) -> Dict[str, Any]:
        """
        Create a code submission record.

        Args:
            code: Python code
            student_id: Student identifier
            session_id: Session identifier

        Returns:
            Submission data
        """
        submission_data = {
            "student_id": student_id,
            "session_id": session_id,
            "code": code,
            "language": "python",
            "status": "pending",
            "submitted_at": datetime.utcnow().isoformat(),
        }

        # TODO: Save to database via Dapr state store
        # submission_id = await self.db.save_state("code_submissions", None, submission_data)
        # submission_data["id"] = submission_id

        return submission_data

    async def update_submission_status(
        self,
        submission_id: int,
        status: str
    ) -> None:
        """
        Update submission status.

        Args:
            submission_id: Submission identifier
            status: New status (running, completed, failed, timeout)
        """
        # TODO: Update in database via Dapr state store
        pass

    async def create_execution_result(
        self,
        submission_id: int,
        stdout: str,
        stderr: str,
        exit_code: int,
        execution_time_ms: float,
        timed_out: bool,
        error_message: Optional[str] = None,
        memory_used_mb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create an execution result record.

        Args:
            submission_id: Submission identifier
            stdout: Standard output
            stderr: Standard error
            exit_code: Process exit code
            execution_time_ms: Execution time in milliseconds
            timed_out: Whether execution timed out
            error_message: Error message if any
            memory_used_mb: Memory used in megabytes

        Returns:
            Execution result data
        """
        result_data = {
            "submission_id": submission_id,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time_ms": execution_time_ms,
            "memory_used_mb": memory_used_mb,
            "timed_out": timed_out,
            "error_message": error_message,
            "created_at": datetime.utcnow().isoformat(),
        }

        # TODO: Save to database via Dapr state store
        # result_id = await self.db.save_state("execution_results", None, result_data)
        # result_data["id"] = result_id

        return result_data

    async def get_submission_history(
        self,
        student_id: int,
        session_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """
        Get code submission history for a student.

        Args:
            student_id: Student identifier
            session_id: Optional session identifier to filter by
            limit: Maximum number of submissions
            offset: Number of submissions to skip

        Returns:
            List of submissions with results
        """
        # TODO: Query database via Dapr state store
        # filter_params = {"student_id": student_id}
        # if session_id:
        #     filter_params["session_id"] = session_id
        #
        # return await self.db.query_state(
        #     "code_submissions",
        #     filter=filter_params,
        #     limit=limit,
        #     offset=offset,
        #     order_by="submitted_at DESC"
        # )
        return []

    async def get_submission_with_result(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """
        Get submission with its execution result.

        Args:
            submission_id: Submission identifier

        Returns:
            Submission with result or None if not found
        """
        # TODO: Query database via Dapr state store
        # submission = await self.db.get_state("code_submissions", str(submission_id))
        # if not submission:
        #     return None
        #
        # result = await self.db.query_state(
        #     "execution_results",
        #     filter={"submission_id": submission_id}
        # )
        #
        # return {
        #     "submission": submission,
        #     "result": result[0] if result else None
        # }
        return None
