"""
Domain Model for Session
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Session(BaseModel):
    """Negotiation session domain model"""
    id: str
    scenario_id: str
    persona_type: str
    status: SessionStatus
    started_at: datetime
    deadline: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    # Client token for basic session ownership validation (not a replacement for auth)
    client_token: Optional[str] = None
    
    class Config:
        use_enum_values = True