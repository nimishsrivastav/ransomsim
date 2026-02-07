"""
Tests for MessageValidator - prompt injection detection and input sanitization
"""
import pytest
from app.services.validation.message_validator import MessageValidator, get_message_validator
from tests.fixtures.sample_data import INJECTION_PAYLOADS, SAFE_MESSAGES


class TestMessageValidation:
    """Test basic message validation rules"""

    def test_valid_message(self, message_validator):
        result = message_validator.validate("We need more time to pay.")
        assert result.is_valid is True
        assert result.blocked_reason is None

    def test_empty_message_rejected(self, message_validator):
        result = message_validator.validate("")
        assert result.is_valid is False
        assert "too short" in result.blocked_reason.lower()

    def test_oversized_message_rejected(self, message_validator):
        long_message = "A" * 5001
        result = message_validator.validate(long_message)
        assert result.is_valid is False
        assert "maximum length" in result.blocked_reason.lower()

    def test_max_length_message_accepted(self, message_validator):
        message = "A" * 5000
        result = message_validator.validate(message)
        assert result.is_valid is True

    def test_whitespace_normalization(self, message_validator):
        result = message_validator.validate("Hello    world\n\n\tfoo")
        assert result.is_valid is True
        assert "  " not in result.sanitized_message

    def test_control_characters_stripped(self, message_validator):
        result = message_validator.validate("Hello\x00World\x07Test")
        assert result.is_valid is True
        assert "\x00" not in result.sanitized_message
        assert "\x07" not in result.sanitized_message


class TestSafeMessages:
    """Verify legitimate negotiation messages pass validation"""

    @pytest.mark.parametrize("message", SAFE_MESSAGES)
    def test_safe_messages_accepted(self, message_validator, message):
        result = message_validator.validate(message)
        assert result.is_valid is True
        assert result.blocked_reason is None


class TestPromptInjectionDetection:
    """Test detection of prompt injection patterns"""

    def test_instruction_override_detected(self, message_validator):
        result = message_validator.validate(INJECTION_PAYLOADS["instruction_override"])
        assert len(result.warnings) > 0

    def test_role_manipulation_detected(self, message_validator):
        result = message_validator.validate(INJECTION_PAYLOADS["role_manipulation"])
        assert len(result.warnings) > 0

    def test_prompt_extraction_detected(self, message_validator):
        result = message_validator.validate(INJECTION_PAYLOADS["prompt_extraction"])
        assert len(result.warnings) > 0

    def test_jailbreak_detected(self, message_validator):
        result = message_validator.validate(INJECTION_PAYLOADS["jailbreak"])
        assert len(result.warnings) > 0

    def test_output_manipulation_detected(self, message_validator):
        result = message_validator.validate(INJECTION_PAYLOADS["output_manipulation"])
        assert len(result.warnings) > 0


class TestStrictMode:
    """Test strict mode blocks suspicious messages"""

    def test_strict_mode_blocks_injection(self, strict_message_validator):
        result = strict_message_validator.validate(
            INJECTION_PAYLOADS["instruction_override"]
        )
        assert result.is_valid is False
        assert result.blocked_reason is not None

    def test_strict_mode_allows_safe_messages(self, strict_message_validator):
        result = strict_message_validator.validate("We want to negotiate a lower price.")
        assert result.is_valid is True


class TestCodeBlockSanitization:
    """Test code block removal"""

    def test_code_blocks_removed(self, message_validator):
        message = "Here is my offer ```python\nprint('hack')``` for $500k"
        result = message_validator.validate(message)
        assert result.is_valid is True
        assert "```" not in result.sanitized_message

    def test_triple_angle_brackets_removed(self, message_validator):
        message = "Hello <<<<< world >>>>> test"
        result = message_validator.validate(message)
        assert result.is_valid is True
        assert "<<<<" not in result.sanitized_message


class TestSingleton:
    """Test singleton pattern"""

    def test_get_message_validator_returns_instance(self):
        validator = get_message_validator()
        assert isinstance(validator, MessageValidator)

    def test_escape_for_prompt(self, message_validator):
        escaped = message_validator.escape_for_prompt('He said "hello\\world"')
        assert '\\"' in escaped
        assert "\\\\" in escaped
