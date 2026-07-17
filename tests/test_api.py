# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

# Create a test client that wraps your FastAPI application
client = TestClient(app)

def test_receive_inbound_request_not_found():
    # Simulate a SendGrid webhook hitting a Tenant ID (9999) that does not exist
    payload = {"subject": "Pothole", "body": "There is a massive pothole on Main St."}
    
    response = client.post("/api/v1/intake/9999", json=payload)
    
    # Assert that the API responds exactly how we expect
    assert response.status_code == 404
    assert response.json()["detail"] == "Tenant not found"