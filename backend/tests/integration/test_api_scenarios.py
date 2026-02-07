"""
Integration tests for /api/v1/scenarios endpoints
"""
import pytest
from tests.fixtures.sample_data import SAMPLE_SCENARIO_REQUEST


class TestGenerateScenario:
    """Test POST /api/v1/scenarios/generate"""

    def test_generate_scenario_success(self, client):
        response = client.post(
            "/api/v1/scenarios/generate",
            json=SAMPLE_SCENARIO_REQUEST,
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("scenario_")
        assert data["ransom_amount"] > 0
        assert data["organization"]["industry"] == "Healthcare"

    def test_generate_scenario_missing_fields(self, client):
        response = client.post("/api/v1/scenarios/generate", json={})
        assert response.status_code == 422

    def test_generate_scenario_invalid_persona(self, client):
        bad_request = {
            "organization": {
                "size": "medium",
                "industry": "Healthcare",
                "data_sensitivity": "high",
            },
            "persona_type": "invalid_type",
        }
        response = client.post("/api/v1/scenarios/generate", json=bad_request)
        assert response.status_code == 422

    def test_generate_scenario_invalid_difficulty(self, client):
        bad_request = {
            "organization": {
                "size": "medium",
                "industry": "Healthcare",
                "data_sensitivity": "high",
            },
            "persona_type": "professional",
            "difficulty": 15,  # Out of range
        }
        response = client.post("/api/v1/scenarios/generate", json=bad_request)
        assert response.status_code == 422


class TestGetScenario:
    """Test GET /api/v1/scenarios/{scenario_id}"""

    def test_get_scenario_after_creation(self, client):
        create_resp = client.post(
            "/api/v1/scenarios/generate",
            json=SAMPLE_SCENARIO_REQUEST,
        )
        scenario_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/v1/scenarios/{scenario_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == scenario_id

    def test_get_nonexistent_scenario(self, client):
        response = client.get("/api/v1/scenarios/scenario_doesnotexist")
        assert response.status_code == 404
