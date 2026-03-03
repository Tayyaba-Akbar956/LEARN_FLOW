"""
Authentication middleware for FastAPI endpoints.
Validates JWT tokens and extracts user context.
"""
from functools import wraps
from typing import Optional, Callable
import jwt
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()


class UserContext(BaseModel):
    """User context extracted from JWT token."""
    id: str
    email: str
    name: str
    role: str  # 'student' or 'teacher'


class AuthenticationError(HTTPException):
    """Custom authentication error."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error."""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def decode_token(token: str) -> UserContext:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        UserContext with user information

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return UserContext(
            id=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name"),
            role=payload.get("role", "student")
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    except Exception as e:
        raise AuthenticationError(f"Token validation failed: {str(e)}")


def get_current_user(credentials: HTTPAuthorizationCredentials) -> UserContext:
    """
    Extract current user from authorization header.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        UserContext with user information

    Raises:
        AuthenticationError: If authentication fails
    """
    if not credentials:
        raise AuthenticationError("Missing authorization header")

    token = credentials.credentials
    return decode_token(token)


async def get_user_from_request(request: Request) -> Optional[UserContext]:
    """
    Extract user context from request headers.

    Args:
        request: FastAPI request object

    Returns:
        UserContext if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")
    try:
        return decode_token(token)
    except AuthenticationError:
        return None


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for endpoint.
    Injects user context as first parameter.

    Usage:
        @require_auth
        async def my_endpoint(user: UserContext, ...):
            pass
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = await get_user_from_request(request)
        if not user:
            raise AuthenticationError("Authentication required")

        return await func(user, request, *args, **kwargs)

    return wrapper


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific role(s) for endpoint.
    Injects user context as first parameter.

    Usage:
        @require_role("teacher")
        async def teacher_endpoint(user: UserContext, ...):
            pass

        @require_role("student", "teacher")
        async def shared_endpoint(user: UserContext, ...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = await get_user_from_request(request)
            if not user:
                raise AuthenticationError("Authentication required")

            if user.role not in allowed_roles:
                raise AuthorizationError(
                    f"Access denied. Required role: {', '.join(allowed_roles)}"
                )

            return await func(user, request, *args, **kwargs)

        return wrapper

    return decorator


def optional_auth(func: Callable) -> Callable:
    """
    Decorator for optional authentication.
    Injects user context as first parameter (may be None).

    Usage:
        @optional_auth
        async def my_endpoint(user: Optional[UserContext], ...):
            if user:
                # Authenticated user
            else:
                # Anonymous user
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = await get_user_from_request(request)
        return await func(user, request, *args, **kwargs)

    return wrapper


# FastAPI dependency for use with Depends()
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = security
) -> UserContext:
    """
    FastAPI dependency for authentication.

    Usage:
        @app.get("/protected")
        async def protected_endpoint(
            user: UserContext = Depends(get_current_user_dependency)
        ):
            return {"user_id": user.id}
    """
    return get_current_user(credentials)


async def get_current_teacher(
    user: UserContext = get_current_user_dependency
) -> UserContext:
    """
    FastAPI dependency for teacher-only endpoints.

    Usage:
        @app.get("/teacher/dashboard")
        async def teacher_dashboard(
            user: UserContext = Depends(get_current_teacher)
        ):
            return {"teacher_id": user.id}
    """
    if user.role != "teacher":
        raise AuthorizationError("Teacher access required")
    return user


async def get_current_student(
    user: UserContext = get_current_user_dependency
) -> UserContext:
    """
    FastAPI dependency for student-only endpoints.

    Usage:
        @app.get("/student/progress")
        async def student_progress(
            user: UserContext = Depends(get_current_student)
        ):
            return {"student_id": user.id}
    """
    if user.role != "student":
        raise AuthorizationError("Student access required")
    return user
