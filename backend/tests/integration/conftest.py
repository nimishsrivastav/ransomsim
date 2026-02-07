"""
Shared fixtures for integration tests - handles singleton reset
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from tests.fixtures.sample_data import (
    SAMPLE_SCENARIO_RESPONSE,
    SAMPLE_AI_MESSAGE_CONTENT,
    SAMPLE_ANALYSIS_RESPONSE,
)

import app.services.gemini.client as client_module
import app.services.gemini.scenario_generator as sg_module
import app.services.gemini.analysis_engine as ae_module
import app.services.gemini.persona_engine as pe_module
import app.services.gemini.conversation_manager as cm_module


def _reset_singletons(mock_service):
    """Reset all singleton instances with the mock"""
    client_module._gemini_service = mock_service

    # Reset scenario generator
    if hasattr(sg_module, "_scenario_generator"):
        sg_module._scenario_generator = None

    # Reset analysis engine
    if hasattr(ae_module, "_analysis_engine"):
        ae_module._analysis_engine = None

    # Reset persona engine
    if hasattr(pe_module, "_persona_engine"):
        pe_module._persona_engine = None

    # Reset conversation manager
    if hasattr(cm_module, "_conversation_manager"):
        cm_module._conversation_manager = None

    # Reset session manager
    import app.services.session.session_manager as sm_module
    if "_session_manager" in globals() or hasattr(sm_module, "_session_manager"):
        try:
            del sm_module.__dict__["_session_manager"]
        except KeyError:
            pass
        # Also try the globals pattern used in the code
        if "_session_manager" in dir(sm_module):
            pass


@pytest.fixture
def client():
    """TestClient with mocked Gemini service and fresh singletons"""
    mock_service = MagicMock()
    mock_service.generate_content = AsyncMock(return_value=SAMPLE_AI_MESSAGE_CONTENT)
    mock_service.generate_structured_content = AsyncMock(
        return_value=SAMPLE_SCENARIO_RESPONSE
    )
    mock_service.test_connection = AsyncMock(return_value=True)

    _reset_singletons(mock_service)

    with TestClient(app) as c:
        yield c

    # Cleanup
    client_module._gemini_service = None


@pytest.fixture
def analysis_client():
    """TestClient with mock that handles both scenario and analysis structured calls"""
    mock_service = MagicMock()
    mock_service.generate_content = AsyncMock(return_value=SAMPLE_AI_MESSAGE_CONTENT)
    mock_service.test_connection = AsyncMock(return_value=True)

    call_count = {"n": 0}

    async def smart_structured(*args, **kwargs):
        """Return scenario data for first call, analysis data for subsequent"""
        call_count["n"] += 1
        prompt_text = str(kwargs.get("prompt", "") or (args[0] if args else "")).lower()
        if any(word in prompt_text for word in ("analyze", "analysis", "performance", "evaluate")):
            return SAMPLE_ANALYSIS_RESPONSE
        return SAMPLE_SCENARIO_RESPONSE

    mock_service.generate_structured_content = AsyncMock(side_effect=smart_structured)

    _reset_singletons(mock_service)

    with TestClient(app) as c:
        yield c

    client_module._gemini_service = None
