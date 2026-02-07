"""
Tests for ScenarioGenerator - scenario creation with mocked Gemini
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.gemini.scenario_generator import ScenarioGenerator
from app.models.schemas.scenario import OrganizationProfile, Scenario
from tests.fixtures.sample_data import SAMPLE_SCENARIO_RESPONSE


@pytest.fixture
def scenario_generator():
    """ScenarioGenerator with mocked Gemini client"""
    with patch("app.services.gemini.scenario_generator.get_gemini_service") as mock_get:
        mock_service = MagicMock()
        mock_service.generate_structured_content = AsyncMock(
            return_value=SAMPLE_SCENARIO_RESPONSE
        )
        mock_get.return_value = mock_service
        gen = ScenarioGenerator()
        yield gen


class TestScenarioGeneration:
    """Test scenario generation"""

    @pytest.mark.asyncio
    async def test_generate_scenario_returns_scenario(self, scenario_generator):
        org = OrganizationProfile(
            size="medium", industry="Healthcare", data_sensitivity="critical"
        )
        scenario = await scenario_generator.generate_scenario(
            organization=org, persona_type="professional", difficulty=7
        )
        assert isinstance(scenario, Scenario)
        assert scenario.id.startswith("scenario_")
        assert scenario.ransom_amount > 0

    @pytest.mark.asyncio
    async def test_generate_scenario_stores_in_cache(self, scenario_generator):
        org = OrganizationProfile(
            size="large", industry="Finance", data_sensitivity="high"
        )
        scenario = await scenario_generator.generate_scenario(
            organization=org, persona_type="opportunist", difficulty=5
        )
        cached = await scenario_generator.get_scenario(scenario.id)
        assert cached is not None
        assert cached.id == scenario.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_scenario_returns_none(self, scenario_generator):
        result = await scenario_generator.get_scenario("scenario_doesnotexist")
        assert result is None

    @pytest.mark.asyncio
    async def test_scenario_has_required_fields(self, scenario_generator):
        org = OrganizationProfile(
            size="small", industry="Retail", data_sensitivity="medium"
        )
        scenario = await scenario_generator.generate_scenario(
            organization=org, persona_type="script_kiddie", difficulty=3
        )
        assert scenario.narrative is not None
        assert scenario.entry_vector is not None
        assert scenario.systems_affected is not None
        assert scenario.data_at_risk is not None
        assert scenario.ransom_currency is not None

    def test_difficulty_mapping(self, scenario_generator):
        assert scenario_generator._map_difficulty(1) == "easy"
        assert scenario_generator._map_difficulty(5) == "realistic"
        assert scenario_generator._map_difficulty(9) == "expert"
