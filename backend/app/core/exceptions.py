"""
Custom Exception Classes
"""
from typing import Optional, Dict, Any


class CustomException(Exception):
    """Base custom exception"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "server_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class SessionNotFoundError(CustomException):
    """Session not found"""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session {session_id} not found",
            status_code=404,
            error_type="session_not_found",
            details={"session_id": session_id},
        )


class SessionExpiredError(CustomException):
    """Session has expired"""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session {session_id} has expired",
            status_code=410,
            error_type="session_expired",
            details={"session_id": session_id},
        )


class InvalidMessageError(CustomException):
    """Invalid message content"""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid message: {reason}",
            status_code=400,
            error_type="invalid_message",
            details={"reason": reason},
        )


class GeminiAPIError(CustomException):
    """Gemini API error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Gemini API error: {message}",
            status_code=503,
            error_type="gemini_api_error",
            details=details or {},
        )


class RateLimitError(CustomException):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            error_type="rate_limit_exceeded",
            details={"retry_after": retry_after},
        )