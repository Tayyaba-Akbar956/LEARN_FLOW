"""Sandbox service for secure Python code execution."""
import subprocess
import tempfile
import os
import time
from typing import Dict, Any, Optional
from backend.src.sandbox.config import SANDBOX_CONFIG, get_docker_run_command
from backend.src.sandbox.security import validate_code_safety, sanitize_output, get_seccomp_profile
import json


class SandboxService:
    """
    Service for executing Python code in a secure Docker sandbox.

    Provides isolated execution with resource limits, no network access,
    and restricted filesystem access.
    """

    def __init__(self):
        """Initialize SandboxService."""
        self.timeout = SANDBOX_CONFIG["timeout_seconds"]
        self.max_output_bytes = SANDBOX_CONFIG["max_output_bytes"]

    async def execute_code(self, code: str, student_id: int) -> Dict[str, Any]:
        """
        Execute Python code in a secure sandbox.

        Args:
            code: Python code to execute
            student_id: Student identifier (for logging)

        Returns:
            Dictionary with execution results:
            {
                "stdout": str,
                "stderr": str,
                "exit_code": int,
                "execution_time_ms": float,
                "timed_out": bool,
                "error_message": str | None
            }
        """
        # Validate code safety
        is_safe, error_msg = validate_code_safety(code)
        if not is_safe:
            return {
                "stdout": "",
                "stderr": error_msg,
                "exit_code": 1,
                "execution_time_ms": 0.0,
                "timed_out": False,
                "error_message": error_msg,
            }

        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            code_file_path = f.name

        try:
            # Build Docker command
            docker_cmd = get_docker_run_command(code_file_path)

            # Execute in Docker container
            start_time = time.time()

            try:
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False
                )

                execution_time_ms = (time.time() - start_time) * 1000
                timed_out = False

            except subprocess.TimeoutExpired:
                execution_time_ms = self.timeout * 1000
                timed_out = True
                result = subprocess.CompletedProcess(
                    args=docker_cmd,
                    returncode=124,  # Timeout exit code
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout} seconds"
                )

            # Sanitize output
            stdout = sanitize_output(result.stdout, self.max_output_bytes)
            stderr = sanitize_output(result.stderr, self.max_output_bytes)

            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "execution_time_ms": execution_time_ms,
                "timed_out": timed_out,
                "error_message": stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time_ms": 0.0,
                "timed_out": False,
                "error_message": f"Sandbox execution failed: {str(e)}",
            }

        finally:
            # Clean up temporary file
            try:
                os.unlink(code_file_path)
            except Exception:
                pass

    def check_docker_available(self) -> bool:
        """
        Check if Docker is available and running.

        Returns:
            True if Docker is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    async def pull_docker_image(self) -> bool:
        """
        Pull the Docker image for sandbox execution.

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "pull", SANDBOX_CONFIG["docker_image"]],
                capture_output=True,
                timeout=300,  # 5 minutes
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_sandbox_info(self) -> Dict[str, Any]:
        """
        Get sandbox configuration information.

        Returns:
            Dictionary with sandbox configuration
        """
        return {
            "timeout_seconds": SANDBOX_CONFIG["timeout_seconds"],
            "memory_limit_mb": SANDBOX_CONFIG["memory_limit_mb"],
            "cpu_limit_percent": SANDBOX_CONFIG["cpu_limit_percent"],
            "network_enabled": SANDBOX_CONFIG["network_enabled"],
            "filesystem_enabled": SANDBOX_CONFIG["filesystem_enabled"],
            "python_version": SANDBOX_CONFIG["python_version"],
            "docker_available": self.check_docker_available(),
        }
