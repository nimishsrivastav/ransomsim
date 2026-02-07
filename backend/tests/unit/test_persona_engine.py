"""
Tests for PersonaEngine - persona config and response generation
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.gemini.persona_engine import PersonaEngine
from tests.fixtures.sample_data import SAMPLE_AI_MESSAGE_CONTENT


@pytest.fixture
def persona_engine():
    """PersonaEngine with mocked Gemini client"""
    with patch("app.services.gemini.persona_engine.get_gemini_service") as mock_get:
        mock_service = MagicMock()
        mock_service.generate_content = AsyncMock(
            return_value=SAMPLE_AI_MESSAGE_CONTENT
        )
        mock_get.return_value = mock_service
        engine = PersonaEngine()
        yield engine


class TestPersonaConfig:
    """Test persona configuration"""

    def test_professional_config(self, persona_engine):
        config = persona_engine.get_persona_config("professional")
        assert config is not None
        assert "name" in config or "style" in config or len(config) > 0

    def test_opportunist_config(self, persona_engine):
        config = persona_engine.get_persona_config("opportunist")
        assert config is not None

    def test_script_kiddie_config(self, persona_engine):
        config = persona_engine.get_persona_config("script_kiddie")
        assert config is not None

    def test_available_personas(self, persona_engine):
        personas = persona_engine.get_available_personas()
        assert "professional" in personas
        assert "opportunist" in personas
        assert "script_kiddie" in personas
        assert len(personas) == 3


class TestSystemInstruction:
    """Test system instruction building"""

    def test_build_system_instruction_without_scenario(self, persona_engine):
        instruction = persona_engine.build_system_instruction("professional")
        assert isinstance(instruction, str)
        assert len(instruction) > 0

    def test_build_system_instruction_with_scenario(self, persona_engine):
        scenario = {
            "ransom_amount": 2800000,
            "systems_affected": ["EMR", "Database"],
            "narrative": "Healthcare breach",
        }
        instruction = persona_engine.build_system_instruction(
            "professional", scenario_context=scenario
        )
        assert isinstance(instruction, str)
        assert len(instruction) > 0


class TestPersonaResponse:
    """Test AI response generation"""

    @pytest.mark.asyncio
    async def test_generate_response(self, persona_engine):
        response = await persona_engine.generate_persona_response(
            persona_type="professional",
            user_message="Can you prove you have our data?",
            conversation_history=[],
        )
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_generate_response_with_history(self, persona_engine):
        history = [
            {"sender": "ai", "content": "Your systems are encrypted. Pay $2.8M."},
            {"sender": "user", "content": "We need proof."},
        ]
        response = await persona_engine.generate_persona_response(
            persona_type="professional",
            user_message="We cannot afford that amount.",
            conversation_history=history,
        )
        assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_generate_response_with_scenario(self, persona_engine):
        scenario = {"ransom_amount": 1000000, "systems_affected": ["Server A"]}
        response = await persona_engine.generate_persona_response(
            persona_type="opportunist",
            user_message="Let's negotiate.",
            conversation_history=[],
            scenario_context=scenario,
        )
        assert isinstance(response, str)
