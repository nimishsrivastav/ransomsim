"""
Integration tests for /api/v1/negotiations endpoints
"""
import pytest
from tests.fixtures.sample_data import SAMPLE_SCENARIO_REQUEST


def _create_scenario(client):
    """Helper to create a scenario and return its ID"""
    resp = client.post("/api/v1/scenarios/generate", json=SAMPLE_SCENARIO_REQUEST)
    return resp.json()["id"]


def _start_negotiation(client, scenario_id):
    """Helper to start a negotiation and return session_id + client_token"""
    resp = client.post(
        "/api/v1/negotiations/start",
        json={"scenario_id": scenario_id, "persona_type": "professional"},
    )
    data = resp.json()
    return data["session_id"], data.get("client_token")


class TestStartNegotiation:
    """Test POST /api/v1/negotiations/start"""

    def test_start_negotiation_success(self, client):
        scenario_id = _create_scenario(client)
        resp = client.post(
            "/api/v1/negotiations/start",
            json={"scenario_id": scenario_id, "persona_type": "professional"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "session_id" in data
        assert "initial_message" in data
        assert "client_token" in data
        assert data["initial_message"]["sender"] == "ai"

    def test_start_negotiation_missing_fields(self, client):
        resp = client.post("/api/v1/negotiations/start", json={})
        assert resp.status_code == 422

    def test_start_negotiation_invalid_persona(self, client):
        scenario_id = _create_scenario(client)
        resp = client.post(
            "/api/v1/negotiations/start",
            json={"scenario_id": scenario_id, "persona_type": "hacker_lord"},
        )
        assert resp.status_code == 422


class TestSendMessage:
    """Test POST /api/v1/negotiations/{session_id}/message"""

    def test_send_message_success(self, client):
        scenario_id = _create_scenario(client)
        session_id, token = _start_negotiation(client, scenario_id)

        resp = client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": "Can you prove you have our data?"},
            headers={"X-Client-Token": token} if token else {},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "ai_response" in data
        assert data["ai_response"]["sender"] == "ai"
        assert "pressure_level" in data

    def test_send_message_nonexistent_session(self, client):
        resp = client.post(
            "/api/v1/negotiations/session_fake/message",
            json={"content": "Hello"},
        )
        assert resp.status_code in (404, 500)

    def test_send_empty_message_rejected(self, client):
        scenario_id = _create_scenario(client)
        session_id, token = _start_negotiation(client, scenario_id)

        resp = client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": ""},
            headers={"X-Client-Token": token} if token else {},
        )
        assert resp.status_code == 422

    def test_send_oversized_message_rejected(self, client):
        scenario_id = _create_scenario(client)
        session_id, token = _start_negotiation(client, scenario_id)

        resp = client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": "A" * 5001},
            headers={"X-Client-Token": token} if token else {},
        )
        assert resp.status_code == 422


class TestSessionOwnership:
    """Test X-Client-Token validation"""

    def test_wrong_token_rejected(self, client):
        scenario_id = _create_scenario(client)
        session_id, _ = _start_negotiation(client, scenario_id)

        resp = client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": "Hello"},
            headers={"X-Client-Token": "wrong_token_123"},
        )
        assert resp.status_code == 403


class TestConversationHistory:
    """Test GET /api/v1/negotiations/{session_id}/history"""

    def test_get_history(self, client):
        scenario_id = _create_scenario(client)
        session_id, token = _start_negotiation(client, scenario_id)

        client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": "We want proof."},
            headers={"X-Client-Token": token} if token else {},
        )

        resp = client.get(f"/api/v1/negotiations/{session_id}/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert data["total_messages"] >= 2

    def test_get_history_nonexistent_session(self, client):
        resp = client.get("/api/v1/negotiations/session_fake/history")
        assert resp.status_code == 404


class TestCompleteNegotiation:
    """Test POST /api/v1/negotiations/{session_id}/complete"""

    def test_complete_session(self, client):
        scenario_id = _create_scenario(client)
        session_id, _ = _start_negotiation(client, scenario_id)

        resp = client.post(f"/api/v1/negotiations/{session_id}/complete")
        assert resp.status_code == 200
        assert resp.json()["session_id"] == session_id

    def test_complete_nonexistent_session(self, client):
        resp = client.post("/api/v1/negotiations/session_fake/complete")
        assert resp.status_code == 404

    def test_message_after_completion_rejected(self, client):
        scenario_id = _create_scenario(client)
        session_id, token = _start_negotiation(client, scenario_id)

        client.post(f"/api/v1/negotiations/{session_id}/complete")

        resp = client.post(
            f"/api/v1/negotiations/{session_id}/message",
            json={"content": "Hello"},
            headers={"X-Client-Token": token} if token else {},
        )
        assert resp.status_code == 400
