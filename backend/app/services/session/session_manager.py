"""
Session Manager - In-Memory Storage Only
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

from app.models.domain.session import Session, SessionStatus
from app.models.schemas.negotiation import Message, MessageSender
from app.models.schemas.scenario import Scenario
from app.core.exceptions import SessionNotFoundError, SessionExpiredError
from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages negotiation sessions in memory"""
    
    def __init__(self):
        # In-memory storage
        self.sessions: Dict[str, Session] = {}
        self.scenarios: Dict[str, Scenario] = {}
        self.messages: Dict[str, List[Message]] = defaultdict(list)
        
        logger.info("Session manager initialized with in-memory storage")
    
    async def create_session(
        self,
        scenario_id: str,
        persona_type: str,
        client_token: Optional[str] = None,
    ) -> Session:
        """
        Create new negotiation session

        Args:
            scenario_id: Scenario identifier
            persona_type: Threat actor persona
            client_token: Optional client token for session ownership

        Returns:
            Created session
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        # Generate client token if not provided
        if not client_token:
            client_token = f"client_{uuid.uuid4().hex}"

        session = Session(
            id=session_id,
            scenario_id=scenario_id,
            persona_type=persona_type,
            status=SessionStatus.ACTIVE,
            started_at=datetime.now(),
            deadline=datetime.now() + timedelta(hours=settings.SESSION_EXPIRATION_HOURS),
            metadata={
                "pressure_level": 5,
                "concessions_made": 0,
                "user_tactics": [],
            },
            client_token=client_token,
        )

        self.sessions[session_id] = session
        self.messages[session_id] = []

        logger.info(f"Session created: {session_id}")
        return session
    
    async def get_session(
        self,
        session_id: str,
        client_token: Optional[str] = None,
        validate_ownership: bool = False,
    ) -> Optional[Session]:
        """
        Get session by ID

        Args:
            session_id: Session identifier
            client_token: Client token for ownership validation
            validate_ownership: If True, validate client_token matches

        Returns:
            Session if found and valid, None otherwise
        """
        session = self.sessions.get(session_id)

        if session:
            # Check if expired
            if datetime.now() > session.deadline:
                session.status = SessionStatus.EXPIRED
                self.sessions[session_id] = session

            # Validate ownership if requested
            if validate_ownership and session.client_token:
                if not client_token or client_token != session.client_token:
                    logger.warning(
                        f"Session ownership validation failed for {session_id}"
                    )
                    return None

        return session

    def validate_session_ownership(
        self,
        session: Session,
        client_token: Optional[str],
    ) -> bool:
        """
        Validate that client_token matches session owner

        Args:
            session: Session to validate
            client_token: Client token to check

        Returns:
            True if ownership is valid or no token required
        """
        if not session.client_token:
            # No token required for this session
            return True

        if not client_token:
            return False

        return session.client_token == client_token
    
    async def add_message(
        self,
        session_id: str,
        message: Message,
    ) -> Message:
        """Add message to session"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        self.messages[session_id].append(message)
        
        logger.debug(f"Message added to session {session_id}: {message.id}")
        return message
    
    async def add_user_message(
        self,
        session_id: str,
        content: str,
    ) -> Message:
        """Add user message to session"""
        message = Message(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            sender=MessageSender.USER,
            content=content,
            timestamp=datetime.now(),
        )
        
        return await self.add_message(session_id, message)
    
    async def get_messages(self, session_id: str) -> List[Message]:
        """Get all messages for session"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        return self.messages.get(session_id, [])
    
    async def update_session_metadata(
        self,
        session_id: str,
        **kwargs,
    ) -> Dict:
        """Update session metadata"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        session = self.sessions[session_id]
        
        # Update metadata
        for key, value in kwargs.items():
            session.metadata[key] = value
        
        # Auto-calculate some metadata
        messages = self.messages.get(session_id, [])
        session.metadata['total_messages'] = len(messages)
        session.metadata['duration_minutes'] = int(
            (datetime.now() - session.started_at).total_seconds() / 60
        )
        
        self.sessions[session_id] = session
        
        return session.metadata
    
    async def complete_session(self, session_id: str) -> Session:
        """Mark session as completed"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        session = self.sessions[session_id]
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now()
        
        self.sessions[session_id] = session
        
        logger.info(f"Session completed: {session_id}")
        return session
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions (call periodically)"""
        now = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            if now > session.deadline + timedelta(hours=24):
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
            if session_id in self.messages:
                del self.messages[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        logger.info(f"Cleaned up {len(expired)} expired sessions")


def get_session_manager() -> SessionManager:
    """Get session manager singleton"""
    global _session_manager
    if '_session_manager' not in globals():
        globals()['_session_manager'] = SessionManager()
    return globals()['_session_manager']