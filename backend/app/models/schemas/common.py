"""
Common Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None