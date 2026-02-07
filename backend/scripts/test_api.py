"""
scripts/test_api.py - Test API endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health/")
    print("Health Check:", response.json())


def test_generate_scenario():
    """Test scenario generation"""
    data = {
        "organization": {
            "size": "medium",
            "industry": "Healthcare",
            "data_sensitivity": "critical"
        },
        "persona_type": "professional",
        "difficulty": 7
    }
    
    response = requests.post(
        f"{BASE_URL}/scenarios/generate",
        json=data
    )
    
    scenario = response.json()
    print("Generated Scenario:", json.dumps(scenario, indent=2))
    return scenario["id"]


def test_start_negotiation(scenario_id):
    """Test starting negotiation"""
    data = {
        "scenario_id": scenario_id,
        "persona_type": "professional"
    }
    
    response = requests.post(
        f"{BASE_URL}/negotiations/start",
        json=data
    )
    
    result = response.json()
    print("Negotiation Started:", json.dumps(result, indent=2))
    return result["session_id"]


def test_send_message(session_id):
    """Test sending message"""
    data = {
        "content": "Can you provide proof that you have access to our systems?"
    }
    
    response = requests.post(
        f"{BASE_URL}/negotiations/{session_id}/message",
        json=data
    )
    
    result = response.json()
    print("AI Response:", result["ai_response"]["content"])
    return result


def test_get_history(session_id):
    """Test getting conversation history"""
    response = requests.get(
        f"{BASE_URL}/negotiations/{session_id}/history"
    )
    
    history = response.json()
    print(f"Total Messages: {history['total_messages']}")
    return history


def test_generate_analysis(session_id):
    """Test analysis generation"""
    response = requests.post(
        f"{BASE_URL}/analysis/{session_id}"
    )
    
    analysis = response.json()
    print("Performance Score:", analysis["performance_score"])
    print("Outcome:", analysis["outcome"])
    return analysis


if __name__ == "__main__":
    print("=== Testing Ransomware Negotiator API ===\n")
    
    # 1. Health check
    print("1. Health Check")
    test_health()
    print()
    
    # 2. Generate scenario
    print("2. Generate Scenario")
    scenario_id = test_generate_scenario()
    print()
    
    # 3. Start negotiation
    print("3. Start Negotiation")
    session_id = test_start_negotiation(scenario_id)
    print()
    
    # 4. Send messages
    print("4. Send Messages")
    for i in range(3):
        test_send_message(session_id)
        print()
    
    # 5. Get history
    print("5. Get Conversation History")
    test_get_history(session_id)
    print()
    
    # 6. Generate analysis
    print("6. Generate Analysis")
    test_generate_analysis(session_id)
    print()
    
    print("=== All Tests Complete ===")