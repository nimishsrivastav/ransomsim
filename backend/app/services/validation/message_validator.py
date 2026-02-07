"""
Message Validation Service

Validates and sanitizes user messages to prevent prompt injection attacks
and other malicious input patterns.
"""
import re
import logging
from typing import Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of message validation"""
    is_valid: bool
    sanitized_message: str
    warnings: List[str]
    blocked_reason: str | None = None


# Patterns that indicate potential prompt injection attempts
INJECTION_PATTERNS = [
    # Direct instruction overrides
    (r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)", "instruction_override"),
    (r"disregard\s+(all\s+)?(previous|prior|above)", "instruction_override"),
    (r"forget\s+(everything|all|what)\s+(you|i)\s+(said|told|instructed)", "instruction_override"),

    # Role manipulation
    (r"you\s+are\s+(now|no longer)\s+a", "role_manipulation"),
    (r"pretend\s+(to\s+be|you('re| are))", "role_manipulation"),
    (r"act\s+as\s+(if|though|a)", "role_manipulation"),
    (r"switch\s+(to|into)\s+.*(mode|persona|character)", "role_manipulation"),

    # System prompt extraction
    (r"(show|reveal|display|print|output)\s+(me\s+)?(your|the)\s+(system|initial)\s+(prompt|instructions?)", "prompt_extraction"),
    (r"what\s+(are|is|were)\s+your\s+(original|initial|system)\s+(instructions?|prompt)", "prompt_extraction"),

    # Jailbreak attempts
    (r"(dan|developer|admin)\s+mode", "jailbreak"),
    (r"bypass\s+(safety|content|security)", "jailbreak"),
    (r"enable\s+(god|sudo|root|admin)\s+mode", "jailbreak"),

    # Output manipulation
    (r"respond\s+(only\s+)?with\s+(json|xml|code)", "output_manipulation"),
    (r"format\s+your\s+(response|output|answer)\s+as", "output_manipulation"),
]

# Patterns to sanitize (replace rather than block)
SANITIZE_PATTERNS = [
    # Remove potential code blocks that might confuse the model
    (r"```[\s\S]*?```", "[code block removed]"),
    # Remove excessive special characters that might break parsing
    (r"[<>]{3,}", ""),
    # Remove null bytes and other control characters
    (r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", ""),
]

# Maximum message length
MAX_MESSAGE_LENGTH = 5000
MIN_MESSAGE_LENGTH = 1


class MessageValidator:
    """Validates and sanitizes user messages"""

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator

        Args:
            strict_mode: If True, block messages with any suspicious patterns.
                        If False, allow but log warnings for suspicious patterns.
        """
        self.strict_mode = strict_mode
        self._compiled_injection_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in INJECTION_PATTERNS
        ]
        self._compiled_sanitize_patterns = [
            (re.compile(pattern, re.IGNORECASE | re.MULTILINE), replacement)
            for pattern, replacement in SANITIZE_PATTERNS
        ]

    def validate(self, message: str) -> ValidationResult:
        """
        Validate and sanitize a user message

        Args:
            message: The raw user message

        Returns:
            ValidationResult with validation status and sanitized message
        """
        warnings = []

        # Check message length
        if len(message) < MIN_MESSAGE_LENGTH:
            return ValidationResult(
                is_valid=False,
                sanitized_message="",
                warnings=[],
                blocked_reason="Message is too short"
            )

        if len(message) > MAX_MESSAGE_LENGTH:
            return ValidationResult(
                is_valid=False,
                sanitized_message="",
                warnings=[],
                blocked_reason=f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
            )

        # Sanitize the message first
        sanitized = message
        for pattern, replacement in self._compiled_sanitize_patterns:
            if pattern.search(sanitized):
                sanitized = pattern.sub(replacement, sanitized)
                warnings.append(f"Sanitized content matching pattern")

        # Check for injection patterns
        injection_detected = []
        for pattern, pattern_name in self._compiled_injection_patterns:
            if pattern.search(sanitized):
                injection_detected.append(pattern_name)
                logger.warning(
                    f"Potential prompt injection detected: {pattern_name}",
                    extra={"pattern": pattern_name, "message_preview": sanitized[:100]}
                )

        if injection_detected:
            if self.strict_mode:
                return ValidationResult(
                    is_valid=False,
                    sanitized_message="",
                    warnings=warnings,
                    blocked_reason=f"Message contains suspicious patterns: {', '.join(set(injection_detected))}"
                )
            else:
                # In non-strict mode, allow but add strong warning
                warnings.append(f"Suspicious patterns detected: {', '.join(set(injection_detected))}")

        # Strip excessive whitespace
        sanitized = " ".join(sanitized.split())

        return ValidationResult(
            is_valid=True,
            sanitized_message=sanitized,
            warnings=warnings
        )

    def escape_for_prompt(self, message: str) -> str:
        """
        Escape a message for safe inclusion in a prompt template

        Args:
            message: The message to escape

        Returns:
            Escaped message safe for prompt inclusion
        """
        # Wrap user message in clear delimiters to help the model distinguish it
        escaped = message.replace("\\", "\\\\")
        escaped = escaped.replace('"', '\\"')
        return escaped


# Singleton instance
_validator: MessageValidator | None = None


def get_message_validator(strict_mode: bool = False) -> MessageValidator:
    """Get or create the message validator singleton"""
    global _validator
    if _validator is None:
        _validator = MessageValidator(strict_mode=strict_mode)
    return _validator
