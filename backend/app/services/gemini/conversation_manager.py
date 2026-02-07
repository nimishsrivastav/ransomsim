"""
Conversation Manager - Handles multi-turn negotiations
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid

from app.services.gemini.client import get_gemini_service
from app.services.gemini.persona_engine import get_persona_engine
from app.models.schemas.negotiation import Message, MessageSender
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages multi-turn conversations with AI personas"""
    
    def __init__(self):
        self.gemini_service = get_gemini_service()
        self.persona_engine = get_persona_engine()
    
    async def generate_initial_message(
        self,
        session_id: str,
        persona_type: str,
        scenario: Optional[Dict] = None,
    ) -> Message:
        """
        Generate initial threat actor message
        
        Args:
            session_id: Session identifier
            persona_type: Type of threat actor
            scenario: Scenario context
            
        Returns:
            Initial AI message
        """
        try:
            logger.info(f"Generating initial message for session {session_id}")
            
            # Build initial message prompt
            prompt = self._build_initial_prompt(persona_type, scenario)
            
            # Get persona config
            persona_config = self.persona_engine.get_persona_config(persona_type)
            
            # Build system instruction
            system_instruction = self.persona_engine.build_system_instruction(
                persona_type=persona_type,
                scenario_context=scenario,
            )
            
            # Generate response
            response_text = await self.gemini_service.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=persona_config.get('temperature', 0.8),
            )
            
            # Create message object
            message = Message(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                sender=MessageSender.AI,
                content=response_text.strip(),
                timestamp=datetime.now(),
                metadata={"persona_type": persona_type},
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating initial message: {e}")
            raise GeminiAPIError(f"Failed to generate initial message: {str(e)}")
    
    async def generate_response(
        self,
        session_id: str,
        user_message: str,
        conversation_history: List[Message],
        persona_type: str,
        scenario: Optional[Dict] = None,
    ) -> Message:
        """
        Generate AI response to user message
        
        Args:
            session_id: Session identifier
            user_message: User's message
            conversation_history: Full conversation history
            persona_type: Type of threat actor
            scenario: Scenario context
            
        Returns:
            AI response message
        """
        try:
            logger.info(f"Generating response for session {session_id}")
            
            # Convert messages to dict format for persona engine
            history_dicts = [
                {
                    "sender": msg.sender.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in conversation_history
            ]
            
            # Generate response using persona engine
            response_text = await self.persona_engine.generate_persona_response(
                persona_type=persona_type,
                user_message=user_message,
                conversation_history=history_dicts,
                scenario_context=scenario,
            )
            
            # Create message object
            message = Message(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                sender=MessageSender.AI,
                content=response_text,
                timestamp=datetime.now(),
                metadata={
                    "persona_type": persona_type,
                    "user_message_length": len(user_message),
                },
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise GeminiAPIError(f"Failed to generate response: {str(e)}")
    
    def _build_initial_prompt(
        self,
        persona_type: str,
        scenario: Optional[Dict] = None,
    ) -> str:
        """Build initial message prompt"""
        
        if not scenario:
            prompt = """Generate your initial contact message to the victim organization. 
This is the first message they receive from you after discovering the ransomware attack.

Include:
1. Brief statement that you've encrypted their systems
2. Your ransom demand
3. A deadline for payment
4. Threat of what happens if they don't pay
5. Instructions for how to contact you further

Be in character. This is the opening move."""
        else:
            ransom_formatted = f"${scenario.get('ransom_amount', 0):,.2f}"
            
            prompt = f"""Generate your initial contact message to the victim organization.

SCENARIO DETAILS:
- Organization: {scenario.get('industry', 'Unknown')} company
- Systems you encrypted: {', '.join(scenario.get('systems_affected', [])[:3])}
- Data you stole: {', '.join(scenario.get('data_at_risk', [])[:3])}
- Your ransom demand: {ransom_formatted}
- Your deadline: 72 hours

Generate the FIRST MESSAGE they receive from you. Include:
1. Statement that you've breached their systems
2. Brief proof (mention specific systems/data)
3. Ransom demand amount
4. Payment deadline
5. Consequences if they don't pay
6. How to proceed with negotiation

Be in character. Make it realistic and intimidating but professional."""
        
        return prompt


def get_conversation_manager() -> ConversationManager:
    """Get conversation manager instance"""
    return ConversationManager()