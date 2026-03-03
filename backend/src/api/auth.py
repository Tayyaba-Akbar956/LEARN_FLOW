"""Authentication and account management API for LearnFlow."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from backend.src.services.student_service import StudentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency to get student service
def get_student_service():
    return StudentService()

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    student_id: int,
    student_service: StudentService = Depends(get_student_service)
):
    """
    Delete a user account and all associated data.
    
    This endpoint triggers a full cleanup of student data, including:
    - Profile information
    - Session history
    - Code submissions
    - Exercise attempts
    """
    logger.info(f"Account deletion requested for student_id: {student_id}")
    
    success = await student_service.delete_student(student_id)
    
    if not success:
        logger.warning(f"Failed to delete account for student_id: {student_id} - student not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found"
        )
        
    logger.info(f"Successfully deleted account for student_id: {student_id}")
    return None

@router.post("/logout")
async def logout():
    """Sign out the current user and invalidate the session."""
    return {"message": "Successfully logged out"}
