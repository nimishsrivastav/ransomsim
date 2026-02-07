"""
Persona Engine - Manages threat actor personas for negotiations

Handles:
- Loading and managing persona configurations
- Building system instructions per persona type
- Generating in-character responses
- Maintaining persona consistency across conversation
"""
import logging
from typing import Dict, List, Optional, Any

from app.services.gemini.client import get_gemini_service
from app.prompts.personas.professional import (
    PROFESSIONAL_SYSTEM_PROMPT,
    PROFESSIONAL_CONFIG,
    PROFESSIONAL_INITIAL_MESSAGE_TEMPLATE,
)
from app.prompts.personas.opportunist import (
    OPPORTUNIST_SYSTEM_PROMPT,
    OPPORTUNIST_CONFIG,
    OPPORTUNIST_INITIAL_MESSAGE_TEMPLATE,
)
from app.prompts.personas.script_kiddie import (
    SCRIPT_KIDDIE_SYSTEM_PROMPT,
    SCRIPT_KIDDIE_CONFIG,
    SCRIPT_KIDDIE_INITIAL_MESSAGE_TEMPLATE,
)
from app.prompts.adaptive_behaviors import get_adaptive_behavior_prompt
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)

# Singleton instance
_persona_engine: Optional["PersonaEngine"] = None

# Persona registry
PERSONAS = {
    "professional": {
        "system_prompt": PROFESSIONAL_SYSTEM_PROMPT,
        "config": PROFESSIONAL_CONFIG,
        "initial_template": PROFESSIONAL_INITIAL_MESSAGE_TEMPLATE,
    },
    "opportunist": {
        "system_prompt": OPPORTUNIST_SYSTEM_PROMPT,
        "config": OPPORTUNIST_CONFIG,
        "initial_template": OPPORTUNIST_INITIAL_MESSAGE_TEMPLATE,
    },
    "script_kiddie": {
        "system_prompt": SCRIPT_KIDDIE_SYSTEM_PROMPT,
        "config": SCRIPT_KIDDIE_CONFIG,
        "initial_template": SCRIPT_KIDDIE_INITIAL_MESSAGE_TEMPLATE,
    },
}


class PersonaEngine:
    """Manages threat actor personas for ransomware negotiation simulations"""

    def __init__(self):
        """Initialize persona engine"""
        self.gemini_service = get_gemini_service()
        self.personas = PERSONAS
        logger.info("PersonaEngine initialized with personas: %s", list(self.personas.keys()))

    def get_persona_config(self, persona_type: str) -> Dict[str, Any]:
        """
        Get configuration for a persona type

        Args:
            persona_type: Type of persona (professional, opportunist, script_kiddie)

        Returns:
            Persona configuration dictionary
        """
        if persona_type not in self.personas:
            logger.warning(f"Unknown persona type: {persona_type}, defaulting to professional")
            persona_type = "professional"

        return self.personas[persona_type]["config"]

    def build_system_instruction(
        self,
        persona_type: str,
        scenario_context: Optional[Dict] = None,
    ) -> str:
        """
        Build system instruction for a persona

        Args:
            persona_type: Type of persona
            scenario_context: Optional scenario context to incorporate

        Returns:
            Complete system instruction string
        """
        if persona_type not in self.personas:
            logger.warning(f"Unknown persona type: {persona_type}, defaulting to professional")
            persona_type = "professional"

        # Get base system prompt
        base_prompt = self.personas[persona_type]["system_prompt"]

        # Add scenario context if provided
        if scenario_context:
            context_section = self._build_context_section(scenario_context)
            base_prompt = f"{base_prompt}\n\nSCENARIO CONTEXT:\n{context_section}"

        # Add training simulation reminder
        base_prompt += """

REMINDER: This is a TRAINING SIMULATION for cybersecurity professionals.
- Never provide actual criminal advice or real cryptocurrency addresses
- Stay in character to provide realistic training
- The goal is educational - help trainees learn negotiation skills
"""

        return base_prompt

    def _build_context_section(self, scenario: Dict) -> str:
        """Build context section from scenario data"""
        parts = []

        if "industry" in scenario:
            parts.append(f"- Victim Industry: {scenario['industry']}")
        if "ransom_amount" in scenario:
            parts.append(f"- Your Ransom Demand: ${scenario['ransom_amount']:,.0f}")
        if "systems_affected" in scenario:
            systems = scenario["systems_affected"]
            if isinstance(systems, list):
                parts.append(f"- Encrypted Systems: {', '.join(systems[:5])}")
        if "data_at_risk" in scenario:
            data = scenario["data_at_risk"]
            if isinstance(data, list):
                parts.append(f"- Exfiltrated Data: {', '.join(data[:5])}")
        if "deadline" in scenario:
            parts.append(f"- Payment Deadline: {scenario['deadline']}")

        return "\n".join(parts) if parts else "No specific context provided."

    async def generate_persona_response(
        self,
        persona_type: str,
        user_message: str,
        conversation_history: List[Dict],
        scenario_context: Optional[Dict] = None,
    ) -> str:
        """
        Generate an in-character response from the threat actor

        Args:
            persona_type: Type of persona
            user_message: User's message to respond to
            conversation_history: Previous messages in conversation
            scenario_context: Scenario context

        Returns:
            Generated in-character response
        """
        try:
            logger.info(f"Generating {persona_type} persona response")

            # Get persona config
            config = self.get_persona_config(persona_type)

            # Build system instruction
            system_instruction = self.build_system_instruction(
                persona_type=persona_type,
                scenario_context=scenario_context,
            )

            # Analyze conversation for adaptive behaviors
            adaptive_prompt = self._get_adaptive_prompt(
                conversation_history=conversation_history,
                user_message=user_message,
                persona_type=persona_type,
            )

            # Build conversation prompt
            conversation_prompt = self._build_conversation_prompt(
                user_message=user_message,
                conversation_history=conversation_history,
                adaptive_prompt=adaptive_prompt,
            )

            # Generate response
            response = await self.gemini_service.generate_content(
                prompt=conversation_prompt,
                system_instruction=system_instruction,
                temperature=config.get("temperature", 0.8),
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating persona response: {e}")
            raise GeminiAPIError(f"Failed to generate response: {str(e)}")

    def _build_conversation_prompt(
        self,
        user_message: str,
        conversation_history: List[Dict],
        adaptive_prompt: str = "",
    ) -> str:
        """Build prompt including conversation history"""

        prompt_parts = []

        # Add conversation history
        if conversation_history:
            prompt_parts.append("CONVERSATION SO FAR:")
            for msg in conversation_history[-10:]:  # Last 10 messages
                sender = "VICTIM" if msg["sender"] == "user" else "YOU (THREAT ACTOR)"
                prompt_parts.append(f"{sender}: {msg['content']}")
            prompt_parts.append("")

        # Add adaptive behavior instructions if any
        if adaptive_prompt:
            prompt_parts.append(f"BEHAVIORAL GUIDANCE:\n{adaptive_prompt}\n")

        # Add current message
        prompt_parts.append(f"VICTIM'S LATEST MESSAGE:\n{user_message}")

        # Add response instruction
        prompt_parts.append("""
YOUR TASK:
Respond to the victim's message in character. Consider:
- What they said and what they're really trying to achieve
- Your persona's negotiation style
- The current state of negotiations
- Any tactics they're trying to use

Respond naturally as the threat actor would. Stay in character.""")

        return "\n".join(prompt_parts)

    def _get_adaptive_prompt(
        self,
        conversation_history: List[Dict],
        user_message: str,
        persona_type: str,
    ) -> str:
        """Get adaptive behavior prompt based on conversation analysis"""

        # Analyze conversation patterns
        patterns = self._analyze_conversation_patterns(
            conversation_history=conversation_history,
            user_message=user_message,
        )

        # Get adaptive behavior prompt
        return get_adaptive_behavior_prompt(
            patterns=patterns,
            persona_type=persona_type,
        )

    def _analyze_conversation_patterns(
        self,
        conversation_history: List[Dict],
        user_message: str,
    ) -> Dict[str, Any]:
        """Analyze conversation for negotiation patterns"""

        patterns = {
            "stalling": False,
            "lowball": False,
            "authority_claim": False,
            "law_enforcement": False,
            "technical_questions": False,
            "sympathy_play": False,
            "message_count": len(conversation_history),
        }

        # Analyze current message
        message_lower = user_message.lower()

        # Check for stalling patterns
        stall_keywords = ["need time", "discuss", "board", "committee", "review", "few days", "week"]
        patterns["stalling"] = any(kw in message_lower for kw in stall_keywords)

        # Check for lowball offers
        if any(c.isdigit() for c in user_message):
            # Has numbers - might be an offer
            patterns["lowball"] = "%" in user_message or "thousand" in message_lower

        # Check for authority claims
        authority_keywords = ["ceo", "ciso", "authorized", "decision maker", "executive", "board"]
        patterns["authority_claim"] = any(kw in message_lower for kw in authority_keywords)

        # Check for law enforcement mentions
        le_keywords = ["fbi", "police", "law enforcement", "authorities", "federal", "investigation"]
        patterns["law_enforcement"] = any(kw in message_lower for kw in le_keywords)

        # Check for technical questions
        tech_keywords = ["decrypt", "algorithm", "encryption", "how did you", "vulnerability", "technical"]
        patterns["technical_questions"] = any(kw in message_lower for kw in tech_keywords)

        # Check for sympathy plays
        sympathy_keywords = ["children", "hospital", "patients", "lives", "please", "beg", "mercy", "nonprofit"]
        patterns["sympathy_play"] = any(kw in message_lower for kw in sympathy_keywords)

        return patterns

    def get_available_personas(self) -> List[str]:
        """Get list of available persona types"""
        return list(self.personas.keys())


def get_persona_engine() -> PersonaEngine:
    """
    Get singleton PersonaEngine instance

    Returns:
        PersonaEngine instance
    """
    global _persona_engine
    if _persona_engine is None:
        _persona_engine = PersonaEngine()
    return _persona_engine
