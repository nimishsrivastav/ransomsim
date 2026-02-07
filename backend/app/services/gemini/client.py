"""
Gemini AI Service Client

Provides interface to Google Gemini API for:
- Text generation (negotiation responses)
- Structured output (analysis generation)
- Health checks
"""
import logging
import json
import asyncio
from typing import Dict, Optional, Any
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)

# Singleton instance
_gemini_service: Optional["GeminiService"] = None


class GeminiService:
    """Service for interacting with Google Gemini API"""

    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 2  # seconds

    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.default_temperature = settings.GEMINI_TEMPERATURE
        logger.info(f"GeminiService initialized with model: {self.model}")

    async def _call_with_retry(self, func, *args, **kwargs):
        """Call a function with exponential backoff retry on transient errors"""
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_str = str(e)
                is_retryable = "503" in error_str or "overloaded" in error_str.lower() or "UNAVAILABLE" in error_str
                if not is_retryable or attempt == self.MAX_RETRIES - 1:
                    raise
                delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(f"Gemini API call failed (attempt {attempt + 1}/{self.MAX_RETRIES}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        raise last_exception

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text content from Gemini

        Args:
            prompt: User prompt to generate response for
            system_instruction: System instruction for persona/context
            temperature: Generation temperature (0.0-1.0)

        Returns:
            Generated text response
        """
        try:
            temp = temperature if temperature is not None else self.default_temperature

            # Build generation config
            config = types.GenerateContentConfig(
                temperature=temp,
                system_instruction=system_instruction,
            )

            # Generate response with retry
            response = await self._call_with_retry(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config,
            )

            # Extract text from response
            if response.text:
                return response.text

            # Handle empty response
            logger.warning("Empty response from Gemini API")
            return "I apologize, but I cannot generate a response at this time."

        except Exception as e:
            logger.error(f"Gemini API error ({type(e).__name__}): {e}")
            raise GeminiAPIError(f"Failed to generate content: {str(e)}")

    async def generate_structured_content(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        temperature: Optional[float] = None,
        system_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON content from Gemini

        Args:
            prompt: User prompt including instructions
            response_schema: Expected JSON structure description
            temperature: Generation temperature
            system_instruction: Optional system instruction

        Returns:
            Parsed JSON response as dictionary
        """
        try:
            temp = temperature if temperature is not None else 0.7

            # Build prompt with schema instructions
            schema_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON matching this structure:
{json.dumps(response_schema, indent=2)}

Do not include any text before or after the JSON. Just the JSON object."""

            # Build system instruction for structured output
            structured_system = """You are an expert analyst. Always respond with valid JSON only.
No explanations, no markdown code blocks, just the raw JSON object."""

            if system_instruction:
                structured_system = f"{system_instruction}\n\n{structured_system}"

            config = types.GenerateContentConfig(
                temperature=temp,
                system_instruction=structured_system,
            )

            response = await self._call_with_retry(
                self.client.models.generate_content,
                model=self.model,
                contents=schema_prompt,
                config=config,
            )

            if not response.text:
                logger.warning("Empty structured response from Gemini")
                return self._get_default_analysis()

            # Parse JSON response
            return self._parse_json_response(response.text)

        except Exception as e:
            logger.error(f"Gemini structured generation error ({type(e).__name__}): {e}")
            raise GeminiAPIError(f"Failed to generate structured content: {str(e)}")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from response text, handling common issues"""
        # Clean up response
        cleaned = text.strip()

        # Remove markdown code blocks if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, text: {cleaned[:500]}")
            # Return default structure if parsing fails
            return self._get_default_analysis()

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis structure when parsing fails"""
        return {
            "performance_score": 5.0,
            "outcome_summary": "Analysis could not be fully generated",
            "key_mistakes": [],
            "successful_tactics": [],
            "tactical_insights": [],
            "recommendations": [
                {
                    "skill": "Practice more scenarios",
                    "description": "Continue practicing with different threat actor types",
                    "priority": "medium",
                }
            ],
            "benchmark_comparison": {
                "estimated_avg_payment_percent": 70,
                "estimated_avg_time_minutes": 45,
            },
        }

    async def test_connection(self) -> bool:
        """
        Test connection to Gemini API

        Returns:
            True if connection successful, False otherwise
        """
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=50,
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents="Reply with exactly: OK",
                config=config,
            )

            return response.text is not None and len(response.text) > 0

        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

    async def generate_streaming_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Generate content with streaming for real-time responses

        Args:
            prompt: User prompt
            system_instruction: System instruction
            temperature: Generation temperature

        Yields:
            Text chunks as they are generated
        """
        try:
            temp = temperature if temperature is not None else self.default_temperature

            config = types.GenerateContentConfig(
                temperature=temp,
                system_instruction=system_instruction,
            )

            # Use streaming
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config,
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise GeminiAPIError(f"Streaming failed: {str(e)}")


def get_gemini_service() -> GeminiService:
    """
    Get singleton GeminiService instance

    Returns:
        GeminiService instance
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
