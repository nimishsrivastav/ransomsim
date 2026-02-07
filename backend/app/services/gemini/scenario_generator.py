"""
Scenario Generator - Creates realistic ransomware breach scenarios
"""
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta

from app.services.gemini.client import get_gemini_service
from app.models.schemas.scenario import Scenario, OrganizationProfile
from app.prompts.scenario_templates import get_scenario_prompt, DEMO_SCENARIOS
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)

# Singleton instance
_scenario_generator: Optional["ScenarioGenerator"] = None


class ScenarioGenerator:
    """Generates ransomware breach scenarios using Gemini"""

    def __init__(self):
        """Initialize scenario generator"""
        self.gemini_service = get_gemini_service()
        self.scenarios_cache: Dict[str, Scenario] = {}
        logger.info("ScenarioGenerator initialized")

    async def generate_scenario(
        self,
        organization: OrganizationProfile,
        persona_type: str,
        difficulty: int = 5,
    ) -> Scenario:
        """
        Generate a realistic ransomware scenario

        Args:
            organization: Organization profile (size, industry, sensitivity)
            persona_type: Threat actor type
            difficulty: Difficulty level 1-10

        Returns:
            Generated Scenario object
        """
        try:
            logger.info(
                f"Generating scenario: {organization.industry}, "
                f"size={organization.size}, difficulty={difficulty}"
            )

            # Map difficulty to preset
            difficulty_preset = self._map_difficulty(difficulty)

            # Build prompt
            prompt = get_scenario_prompt(
                org_size=organization.size.value,
                industry=organization.industry,
                data_sensitivity=organization.data_sensitivity.value,
                difficulty=difficulty_preset,
            )

            # Define response schema for structured output
            response_schema = self._get_response_schema()

            # Generate scenario using Gemini
            scenario_data = await self.gemini_service.generate_structured_content(
                prompt=prompt,
                response_schema=response_schema,
                temperature=0.8,
            )

            # Create scenario object
            scenario = self._build_scenario(
                organization=organization,
                scenario_data=scenario_data,
            )

            # Cache scenario
            self.scenarios_cache[scenario.id] = scenario

            logger.info(f"Scenario generated: {scenario.id}")
            return scenario

        except Exception as e:
            logger.error(f"Error generating scenario: {e}")
            raise GeminiAPIError(f"Failed to generate scenario: {str(e)}")

    async def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """
        Get cached scenario by ID

        Args:
            scenario_id: Scenario identifier

        Returns:
            Scenario if found, None otherwise
        """
        return self.scenarios_cache.get(scenario_id)

    async def generate_demo_scenario(self, demo_type: str = "healthcare_critical") -> Scenario:
        """
        Generate a pre-configured demo scenario

        Args:
            demo_type: Type of demo scenario

        Returns:
            Demo Scenario
        """
        demo_config = DEMO_SCENARIOS.get(demo_type, DEMO_SCENARIOS["healthcare_critical"])

        # Create organization profile
        org = OrganizationProfile(
            size=demo_config["org_size"],
            industry=demo_config["industry"],
            data_sensitivity=demo_config["data_sensitivity"],
        )

        return await self.generate_scenario(
            organization=org,
            persona_type="professional",
            difficulty=7,
        )

    def _map_difficulty(self, difficulty: int) -> str:
        """Map numeric difficulty to preset name"""
        if difficulty <= 3:
            return "easy"
        elif difficulty <= 7:
            return "realistic"
        else:
            return "expert"

    def _get_response_schema(self) -> Dict:
        """Get expected JSON schema for scenario generation"""
        return {
            "breach_narrative": {
                "entry_vector": "string",
                "attack_timeline": {
                    "initial_access": "string",
                    "lateral_movement": "string",
                    "data_exfiltration": "string",
                    "encryption_triggered": "string",
                    "discovered_by_victim": "string",
                },
                "attacker_dwell_time_days": "number",
            },
            "systems_affected": ["string"],
            "backup_status": "string",
            "data_at_risk": ["string"],
            "data_volume_estimate": "string",
            "regulatory_implications": ["string"],
            "business_impact": {
                "operations_down": "string",
                "estimated_daily_revenue_loss": "number",
                "customer_exposure_count": "number",
            },
            "ransom_amount": "number",
            "payment_deadline_hours": "number",
            "threat_actor_ultimatum": "string",
        }

    def _build_scenario(
        self,
        organization: OrganizationProfile,
        scenario_data: Dict,
    ) -> Scenario:
        """Build Scenario object from generated data"""

        # Generate unique ID
        scenario_id = f"scenario_{uuid.uuid4().hex[:12]}"

        # Extract breach narrative
        breach = scenario_data.get("breach_narrative", {})
        timeline = breach.get("attack_timeline", {})

        # Build narrative text
        narrative = self._build_narrative_text(organization, scenario_data)

        # Build timeline string
        timeline_str = self._build_timeline_string(timeline)

        # Calculate deadline
        deadline_hours = scenario_data.get("payment_deadline_hours", 72)
        deadline = datetime.now() + timedelta(hours=deadline_hours)

        # Create scenario
        return Scenario(
            id=scenario_id,
            organization=organization,
            narrative=narrative,
            entry_vector=breach.get("entry_vector", "Unknown attack vector"),
            timeline=timeline_str,
            systems_affected=scenario_data.get("systems_affected", []),
            data_at_risk=scenario_data.get("data_at_risk", []),
            ransom_amount=float(scenario_data.get("ransom_amount", 1000000)),
            ransom_currency="USD",
            deadline=deadline,
            created_at=datetime.now(),
        )

    def _build_narrative_text(
        self,
        organization: OrganizationProfile,
        scenario_data: Dict,
    ) -> str:
        """Build readable narrative from scenario data"""

        breach = scenario_data.get("breach_narrative", {})
        impact = scenario_data.get("business_impact", {})

        narrative = f"""INCIDENT BRIEFING

Your {organization.industry} organization has been hit by a ransomware attack.

ATTACK SUMMARY:
The threat actors gained initial access via {breach.get('entry_vector', 'unknown means')}.
They remained undetected for approximately {breach.get('attacker_dwell_time_days', 'unknown')} days
before triggering the encryption payload.

CURRENT STATUS:
- Backup Status: {scenario_data.get('backup_status', 'Unknown')}
- Operations Impact: {impact.get('operations_down', 'Multiple systems offline')}
- Estimated Daily Revenue Loss: ${impact.get('estimated_daily_revenue_loss', 0):,.0f}
- Potentially Affected Individuals: {impact.get('customer_exposure_count', 0):,}

DATA EXFILTRATION:
The attackers claim to have exfiltrated approximately {scenario_data.get('data_volume_estimate', 'unknown volume')} of data.

REGULATORY CONCERNS:
{', '.join(scenario_data.get('regulatory_implications', ['Under assessment']))}

RANSOM DEMAND:
The threat actors are demanding ${scenario_data.get('ransom_amount', 0):,.0f} USD.
Deadline: {scenario_data.get('payment_deadline_hours', 72)} hours.
Ultimatum: {scenario_data.get('threat_actor_ultimatum', 'Data will be published if demands not met.')}

You have been tasked with handling communications with the threat actors."""

        return narrative

    def _build_timeline_string(self, timeline: Dict) -> str:
        """Build timeline string from timeline data"""

        parts = []
        if timeline.get("initial_access"):
            parts.append(f"Initial Access: {timeline['initial_access']}")
        if timeline.get("lateral_movement"):
            parts.append(f"Lateral Movement: {timeline['lateral_movement']}")
        if timeline.get("data_exfiltration"):
            parts.append(f"Data Exfiltration: {timeline['data_exfiltration']}")
        if timeline.get("encryption_triggered"):
            parts.append(f"Encryption: {timeline['encryption_triggered']}")
        if timeline.get("discovered_by_victim"):
            parts.append(f"Discovery: {timeline['discovered_by_victim']}")

        return " | ".join(parts) if parts else "Timeline under investigation"


def get_scenario_generator() -> ScenarioGenerator:
    """
    Get singleton ScenarioGenerator instance

    Returns:
        ScenarioGenerator instance
    """
    global _scenario_generator
    if _scenario_generator is None:
        _scenario_generator = ScenarioGenerator()
    return _scenario_generator
