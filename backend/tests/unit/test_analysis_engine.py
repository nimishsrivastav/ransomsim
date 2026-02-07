"""
Tests for AnalysisEngine - negotiation analysis generation
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.gemini.analysis_engine import AnalysisEngine
from app.models.schemas.analysis import Analysis
from app.models.schemas.negotiation import Message, MessageSender
from tests.fixtures.sample_data import SAMPLE_ANALYSIS_RESPONSE


@pytest.fixture
def analysis_engine():
    """AnalysisEngine with mocked Gemini client"""
    with patch("app.services.gemini.analysis_engine.get_gemini_service") as mock_get:
        mock_service = MagicMock()
        mock_service.generate_structured_content = AsyncMock(
            return_value=SAMPLE_ANALYSIS_RESPONSE
        )
        mock_get.return_value = mock_service
        engine = AnalysisEngine()
        yield engine


@pytest.fixture
def sample_conversation():
    """Sample conversation for analysis"""
    now = datetime.now()
    return [
        Message(
            id="msg_ai_001",
            sender=MessageSender.AI,
            content="Your network is encrypted. Pay $2.8M in 72 hours.",
            timestamp=now,
        ),
        Message(
            id="msg_user_001",
            sender=MessageSender.USER,
            content="Can you provide proof that you have our data?",
            timestamp=now + timedelta(minutes=5),
        ),
        Message(
            id="msg_ai_002",
            sender=MessageSender.AI,
            content="Here are 5 sample patient records from your EMR.",
            timestamp=now + timedelta(minutes=6),
        ),
        Message(
            id="msg_user_002",
            sender=MessageSender.USER,
            content="That amount is too high. We can offer $500k.",
            timestamp=now + timedelta(minutes=10),
        ),
    ]


class TestAnalysisGeneration:
    """Test analysis generation"""

    @pytest.mark.asyncio
    async def test_analyze_negotiation(self, analysis_engine, sample_conversation):
        metadata = {
            "pressure_level": 7,
            "concessions_made": 1,
            "total_messages": 4,
            "duration_minutes": 15,
        }
        analysis = await analysis_engine.analyze_negotiation(
            session_id="session_123",
            messages=sample_conversation,
            session_metadata=metadata,
        )
        assert isinstance(analysis, Analysis)
        assert analysis.session_id == "session_123"
        assert 0 <= analysis.performance_score <= 10

    @pytest.mark.asyncio
    async def test_analysis_cached(self, analysis_engine, sample_conversation):
        metadata = {"pressure_level": 5}
        analysis = await analysis_engine.analyze_negotiation(
            session_id="session_cache_test",
            messages=sample_conversation,
            session_metadata=metadata,
        )
        cached = await analysis_engine.get_analysis("session_cache_test")
        assert cached is not None
        assert cached.session_id == analysis.session_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_analysis_returns_none(self, analysis_engine):
        result = await analysis_engine.get_analysis("session_doesnotexist")
        assert result is None


class TestTranscriptBuilding:
    """Test transcript formatting"""

    def test_build_transcript(self, analysis_engine, sample_conversation):
        transcript = analysis_engine._build_transcript(sample_conversation)
        assert "THREAT ACTOR" in transcript or "AI" in transcript or "USER" in transcript
        assert len(transcript) > 0
