"""
Integration tests for /api/v1/analysis endpoints
"""
import pytest
from tests.fixtures.sample_data import SAMPLE_SCENARIO_REQUEST


def _create_full_session(client):
    """Create scenario -> start negotiation -> send messages -> return session_id + token"""
    resp = client.post("/api/v1/scenarios/generate", json=SAMPLE_SCENARIO_REQUEST)
    scenario_id = resp.json()["id"]

    resp = client.post(
        "/api/v1/negotiations/start",
        json={"scenario_id": scenario_id, "persona_type": "professional"},
    )
    data = resp.json()
    session_id = data["session_id"]
    token = data.get("client_token")

    for msg in ["Can you prove it?", "We want to negotiate."]:
        client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": msg},
            headers={"X-Client-Token": token} if token else {},
        )

    return session_id


class TestGenerateAnalysis:
    """Test POST /api/v1/analysis/{session_id}"""

    def test_generate_analysis_success(self, analysis_client):
        session_id = _create_full_session(analysis_client)

        resp = analysis_client.post(f"/api/v1/analysis/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert "performance_score" in data
        assert 0 <= data["performance_score"] <= 10

    def test_generate_analysis_nonexistent_session(self, analysis_client):
        resp = analysis_client.post("/api/v1/analysis/session_fake")
        assert resp.status_code in (404, 500)


class TestGetAnalysis:
    """Test GET /api/v1/analysis/{session_id}"""

    def test_get_analysis_after_generation(self, analysis_client):
        session_id = _create_full_session(analysis_client)

        analysis_client.post(f"/api/v1/analysis/{session_id}")

        resp = analysis_client.get(f"/api/v1/analysis/{session_id}")
        assert resp.status_code == 200
        assert resp.json()["session_id"] == session_id

    def test_get_nonexistent_analysis(self, analysis_client):
        resp = analysis_client.get("/api/v1/analysis/session_fake")
        assert resp.status_code == 404
