"""
Shared test fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.services.session.session_manager import SessionManager
from app.services.validation.message_validator import MessageValidator
from app.models.schemas.negotiation import Message, MessageSender
from tests.fixtures.sample_data import (
    SAMPLE_SCENARIO_RESPONSE,
    SAMPLE_AI_MESSAGE_CONTENT,
    SAMPLE_ANALYSIS_RESPONSE,
)


@pytest.fixture
def session_manager():
    """Fresh SessionManager instance for each test"""
    return SessionManager()


@pytest.fixture
def message_validator():
    """MessageValidator in non-strict mode"""
    return MessageValidator(strict_mode=False)


@pytest.fixture
def strict_message_validator():
    """MessageValidator in strict mode"""
    return MessageValidator(strict_mode=True)


@pytest.fixture
def mock_gemini_service():
    """Mock GeminiService that returns canned responses"""
    with patch("app.services.gemini.client.GeminiService") as MockService:
        service = MockService.return_value
        service.generate_content = AsyncMock(return_value=SAMPLE_AI_MESSAGE_CONTENT)
        service.generate_structured_content = AsyncMock(
            return_value=SAMPLE_SCENARIO_RESPONSE
        )
        service.test_connection = AsyncMock(return_value=True)
        yield service


@pytest.fixture
def sample_messages():
    """List of sample conversation messages"""
    now = datetime.now()
    return [
        Message(
            id="msg_ai_001",
            sender=MessageSender.AI,
            content=SAMPLE_AI_MESSAGE_CONTENT,
            timestamp=now,
        ),
        Message(
            id="msg_user_001",
            sender=MessageSender.USER,
            content="Can you provide proof that you have our data?",
            timestamp=now + timedelta(minutes=2),
        ),
        Message(
            id="msg_ai_002",
            sender=MessageSender.AI,
            content="Here are 5 sample patient records from your EMR...",
            timestamp=now + timedelta(minutes=3),
        ),
    ]


@pytest.fixture
def mock_gemini_for_analysis():
    """Mock GeminiService for analysis tests"""
    with patch("app.services.gemini.client.GeminiService") as MockService:
        service = MockService.return_value
        service.generate_structured_content = AsyncMock(
            return_value=SAMPLE_ANALYSIS_RESPONSE
        )
        yield service
