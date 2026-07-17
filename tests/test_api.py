# tests/test_api.py
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Tenant

# Create a test client that wraps your FastAPI application
client = TestClient(app)

def test_receive_inbound_request_not_found():
    # Simulate a SendGrid webhook hitting a Tenant ID (9999) that does not exist
    payload = {"subject": "Pothole", "body": "There is a massive pothole on Main St."}
    
    response = client.post("/api/v1/intake/9999", json=payload)
    
    # Assert that the API responds exactly how we expect
    assert response.status_code == 404
    assert response.json()["detail"] == "Tenant not found"

def test_receive_inbound_request_success():
    # 1. Setup: Create a temporary tenant to receive the webhook
    db = SessionLocal()
    temp_tenant = Tenant(name="API Test Municipality", config={})
    db.add(temp_tenant)
    db.commit()
    db.refresh(temp_tenant)
    
    # 2. Execute: Hit the webhook endpoint
    payload = {"subject": "Water leak", "body": "Pipe burst on Elm St."}
    response = client.post(f"/api/v1/intake/{temp_tenant.id}", json=payload)
    
    # 3. Assert: Verify the API response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "ticket_id" in data
    
    # 4. Teardown
    db.delete(temp_tenant) # Cascades should ideally handle the ticket, but manual cleanup keeps it safe
    db.commit()
    db.close()