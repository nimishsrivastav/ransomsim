"""
Tests for ConversationManager - message generation
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.gemini.conversation_manager import ConversationManager
from app.models.schemas.negotiation import Message, MessageSender
from tests.fixtures.sample_data import SAMPLE_AI_MESSAGE_CONTENT


@pytest.fixture
def conversation_manager():
    """ConversationManager with mocked dependencies"""
    with patch(
        "app.services.gemini.conversation_manager.get_persona_engine"
    ) as mock_persona:
        mock_engine = MagicMock()
        mock_engine.generate_persona_response = AsyncMock(
            return_value=SAMPLE_AI_MESSAGE_CONTENT
        )
        mock_engine.build_system_instruction = MagicMock(return_value="You are a threat actor.")
        mock_persona.return_value = mock_engine

        with patch(
            "app.services.gemini.conversation_manager.get_gemini_service"
        ) as mock_gemini:
            mock_service = MagicMock()
            mock_service.generate_content = AsyncMock(
                return_value=SAMPLE_AI_MESSAGE_CONTENT
            )
            mock_gemini.return_value = mock_service

            manager = ConversationManager()
            yield manager


class TestInitialMessage:
    """Test initial message generation"""

    @pytest.mark.asyncio
    async def test_generate_initial_message(self, conversation_manager):
        msg = await conversation_manager.generate_initial_message(
            session_id="session_123",
            persona_type="professional",
        )
        assert isinstance(msg, Message)
        assert msg.sender == MessageSender.AI
        assert len(msg.content) > 0
        assert msg.id.startswith("msg_")

    @pytest.mark.asyncio
    async def test_initial_message_with_scenario(self, conversation_manager):
        scenario = {
            "ransom_amount": 2800000,
            "narrative": "Healthcare breach scenario",
        }
        msg = await conversation_manager.generate_initial_message(
            session_id="session_123",
            persona_type="professional",
            scenario=scenario,
        )
        assert isinstance(msg, Message)
        assert msg.sender == MessageSender.AI


class TestResponseGeneration:
    """Test response to user messages"""

    @pytest.mark.asyncio
    async def test_generate_response(self, conversation_manager):
        history = [
            Message(
                id="msg_ai_001",
                sender=MessageSender.AI,
                content="Your systems are encrypted.",
                timestamp=datetime.now(),
            )
        ]
        response = await conversation_manager.generate_response(
            session_id="session_123",
            user_message="Can you prove it?",
            conversation_history=history,
            persona_type="professional",
        )
        assert isinstance(response, Message)
        assert response.sender == MessageSender.AI
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_response_with_scenario_context(self, conversation_manager):
        history = []
        scenario = {"ransom_amount": 500000, "systems_affected": ["DB"]}
        response = await conversation_manager.generate_response(
            session_id="session_123",
            user_message="We want to negotiate.",
            conversation_history=history,
            persona_type="opportunist",
            scenario=scenario,
        )
        assert isinstance(response, Message)
