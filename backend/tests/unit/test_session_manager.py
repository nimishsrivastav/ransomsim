"""
Tests for SessionManager - session lifecycle and ownership
"""
import pytest
from datetime import datetime, timedelta

from app.services.session.session_manager import SessionManager
from app.models.domain.session import SessionStatus
from app.models.schemas.negotiation import Message, MessageSender
from app.core.exceptions import SessionNotFoundError


class TestSessionCreation:
    """Test session creation"""

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        session = await session_manager.create_session(
            scenario_id="scenario_123",
            persona_type="professional",
        )
        assert session.id.startswith("session_")
        assert session.scenario_id == "scenario_123"
        assert session.persona_type == "professional"
        assert session.status == SessionStatus.ACTIVE
        assert session.client_token is not None

    @pytest.mark.asyncio
    async def test_create_session_with_custom_token(self, session_manager):
        session = await session_manager.create_session(
            scenario_id="scenario_123",
            persona_type="professional",
            client_token="custom_token_abc",
        )
        assert session.client_token == "custom_token_abc"

    @pytest.mark.asyncio
    async def test_create_session_generates_token(self, session_manager):
        session = await session_manager.create_session(
            scenario_id="scenario_123",
            persona_type="opportunist",
        )
        assert session.client_token.startswith("client_")

    @pytest.mark.asyncio
    async def test_session_has_deadline(self, session_manager):
        session = await session_manager.create_session(
            scenario_id="scenario_123",
            persona_type="professional",
        )
        assert session.deadline > datetime.now()

    @pytest.mark.asyncio
    async def test_session_metadata_initialized(self, session_manager):
        session = await session_manager.create_session(
            scenario_id="scenario_123",
            persona_type="professional",
        )
        assert session.metadata["pressure_level"] == 5
        assert session.metadata["concessions_made"] == 0
        assert session.metadata["user_tactics"] == []


class TestSessionRetrieval:
    """Test getting sessions"""

    @pytest.mark.asyncio
    async def test_get_existing_session(self, session_manager):
        created = await session_manager.create_session("s1", "professional")
        fetched = await session_manager.get_session(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_session_returns_none(self, session_manager):
        result = await session_manager.get_session("session_doesnotexist")
        assert result is None

    @pytest.mark.asyncio
    async def test_expired_session_status_updated(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        # Force expiration
        session.deadline = datetime.now() - timedelta(hours=1)
        session_manager.sessions[session.id] = session

        fetched = await session_manager.get_session(session.id)
        assert fetched.status == SessionStatus.EXPIRED


class TestSessionOwnership:
    """Test client token ownership validation"""

    @pytest.mark.asyncio
    async def test_valid_ownership(self, session_manager):
        session = await session_manager.create_session(
            "s1", "professional", client_token="token_abc"
        )
        assert session_manager.validate_session_ownership(session, "token_abc") is True

    @pytest.mark.asyncio
    async def test_invalid_ownership(self, session_manager):
        session = await session_manager.create_session(
            "s1", "professional", client_token="token_abc"
        )
        assert session_manager.validate_session_ownership(session, "wrong_token") is False

    @pytest.mark.asyncio
    async def test_missing_token_fails(self, session_manager):
        session = await session_manager.create_session(
            "s1", "professional", client_token="token_abc"
        )
        assert session_manager.validate_session_ownership(session, None) is False

    @pytest.mark.asyncio
    async def test_no_token_required(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        session.client_token = None
        assert session_manager.validate_session_ownership(session, None) is True

    @pytest.mark.asyncio
    async def test_get_session_with_ownership_validation(self, session_manager):
        session = await session_manager.create_session(
            "s1", "professional", client_token="token_abc"
        )
        # Valid token
        result = await session_manager.get_session(
            session.id, client_token="token_abc", validate_ownership=True
        )
        assert result is not None

        # Invalid token
        result = await session_manager.get_session(
            session.id, client_token="wrong", validate_ownership=True
        )
        assert result is None


class TestMessages:
    """Test message management"""

    @pytest.mark.asyncio
    async def test_add_user_message(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        msg = await session_manager.add_user_message(session.id, "Hello")
        assert msg.sender == MessageSender.USER
        assert msg.content == "Hello"
        assert msg.id.startswith("msg_")

    @pytest.mark.asyncio
    async def test_add_ai_message(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        ai_msg = Message(
            id="msg_ai_001",
            sender=MessageSender.AI,
            content="Your systems are encrypted.",
            timestamp=datetime.now(),
        )
        result = await session_manager.add_message(session.id, ai_msg)
        assert result.sender == MessageSender.AI

    @pytest.mark.asyncio
    async def test_get_messages(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        await session_manager.add_user_message(session.id, "Msg 1")
        await session_manager.add_user_message(session.id, "Msg 2")
        messages = await session_manager.get_messages(session.id)
        assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_add_message_invalid_session_raises(self, session_manager):
        with pytest.raises(SessionNotFoundError):
            await session_manager.add_user_message("nonexistent", "Hello")

    @pytest.mark.asyncio
    async def test_get_messages_invalid_session_raises(self, session_manager):
        with pytest.raises(SessionNotFoundError):
            await session_manager.get_messages("nonexistent")


class TestSessionCompletion:
    """Test session completion"""

    @pytest.mark.asyncio
    async def test_complete_session(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        completed = await session_manager.complete_session(session.id)
        assert completed.status == SessionStatus.COMPLETED
        assert completed.completed_at is not None

    @pytest.mark.asyncio
    async def test_complete_nonexistent_session_raises(self, session_manager):
        with pytest.raises(SessionNotFoundError):
            await session_manager.complete_session("nonexistent")


class TestSessionMetadata:
    """Test metadata updates"""

    @pytest.mark.asyncio
    async def test_update_metadata(self, session_manager):
        session = await session_manager.create_session("s1", "professional")
        await session_manager.add_user_message(session.id, "Hello")
        meta = await session_manager.update_session_metadata(session.id)
        assert meta["total_messages"] == 1
        assert "duration_minutes" in meta

    @pytest.mark.asyncio
    async def test_update_metadata_nonexistent_raises(self, session_manager):
        with pytest.raises(SessionNotFoundError):
            await session_manager.update_session_metadata("nonexistent")


class TestCleanup:
    """Test expired session cleanup"""

    def test_cleanup_expired_sessions(self, session_manager):
        # Manually add an expired session
        from app.models.domain.session import Session

        expired_session = Session(
            id="session_expired",
            scenario_id="s1",
            persona_type="professional",
            status=SessionStatus.EXPIRED,
            started_at=datetime.now() - timedelta(days=5),
            deadline=datetime.now() - timedelta(days=3),
        )
        session_manager.sessions["session_expired"] = expired_session
        session_manager.messages["session_expired"] = []

        session_manager.cleanup_expired_sessions()
        assert "session_expired" not in session_manager.sessions
