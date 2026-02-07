"""
Negotiation Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageSender(str, Enum):
    """Message sender types"""
    USER = "user"
    AI = "ai"


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Message(BaseModel):
    """Chat message in a negotiation"""
    id: str = Field(..., description="Unique message identifier")
    sender: MessageSender = Field(..., description="Who sent the message (user or ai)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_abc123def456",
                "sender": "ai",
                "content": "We have encrypted your systems. Pay $2.8M in Bitcoin within 72 hours or your data will be published.",
                "timestamp": "2026-02-06T10:30:00Z",
                "metadata": {"persona_type": "professional"}
            }
        }


class NegotiationStart(BaseModel):
    """Request to start a new negotiation session"""
    scenario_id: str = Field(..., description="ID of a previously generated scenario")
    persona_type: str = Field(
        ...,
        pattern="^(professional|opportunist|script_kiddie)$",
        description="Threat actor persona type"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scenario_abc123",
                "persona_type": "professional"
            }
        }


class NegotiationStartResponse(BaseModel):
    """Response when starting a new negotiation"""
    session_id: str = Field(..., description="Unique session identifier for this negotiation")
    initial_message: Message = Field(..., description="First message from the threat actor")
    deadline: datetime = Field(..., description="Session expiration deadline")
    client_token: str = Field(
        ...,
        description="Client token for session ownership - include in X-Client-Token header for subsequent requests"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_xyz789",
                "initial_message": {
                    "id": "msg_initial001",
                    "sender": "ai",
                    "content": "ATTENTION: Your network has been compromised...",
                    "timestamp": "2026-02-06T10:30:00Z"
                },
                "deadline": "2026-02-08T10:30:00Z",
                "client_token": "client_abc123def456"
            }
        }


class SendMessage(BaseModel):
    """Request to send a message in the negotiation"""
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Your message to the threat actor"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "We need proof that you actually have our data. Can you provide a sample file?"
            }
        }


class SendMessageResponse(BaseModel):
    """Response containing the AI threat actor's reply"""
    message_id: str = Field(..., description="ID of the AI response message")
    ai_response: Message = Field(..., description="The threat actor's response")
    session_status: SessionStatus = Field(..., description="Current session status")
    pressure_level: int = Field(
        ...,
        ge=0,
        le=10,
        description="Current pressure/threat level (0-10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_response002",
                "ai_response": {
                    "id": "msg_response002",
                    "sender": "ai",
                    "content": "Here is proof. We have 500GB of your patient records...",
                    "timestamp": "2026-02-06T10:35:00Z"
                },
                "session_status": "active",
                "pressure_level": 6
            }
        }


class ConversationHistory(BaseModel):
    """Full conversation history for a negotiation session"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[Message] = Field(..., description="All messages in chronological order")
    total_messages: int = Field(..., description="Total number of messages")
    session_status: SessionStatus = Field(..., description="Current session status")