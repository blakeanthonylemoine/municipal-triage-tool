# tests/test_api.py
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from ai_pipeline import TriageResult
from database import SessionLocal
from main import app
from models import Category, Tenant, Ticket

# Create a test client that wraps your FastAPI application
client = TestClient(app)


def test_receive_webhook_tenant_not_found():
    payload = {"subject": "Pothole", "body": "There is a massive pothole on Main St."}

    response = client.post("/webhook/9999", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Tenant not found"


def test_receive_webhook_creates_ticket_using_tenants_real_categories(mocker):
    # 1. Setup: a tenant with its own categories, distinct ids from any other test's data
    db = SessionLocal()
    tenant = Tenant(name="Webhook API Test Municipality", config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    category = Category(tenant_id=tenant.id, name="Water Leaks")
    db.add(category)
    db.commit()
    db.refresh(category)

    try:
        # 2. Mock the Gemini call so this test doesn't hit the real API
        mock_response = MagicMock()
        mock_response.parsed = TriageResult(
            category_id=category.id,
            urgency_score=4,
            extracted_location="Elm St",
            extracted_email=None,
            extracted_phone=None,
            drafted_response="We're on it.",
        )
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mock_client = mocker.patch("ai_pipeline.client.models.generate_content", return_value=mock_response)

        # 3. Execute: hit the webhook endpoint
        payload = {"subject": "Water leak", "body": "Pipe burst on Elm St."}
        response = client.post(f"/webhook/{tenant.id}", json=payload)

        # 4. Assert: the ticket was created with the AI's result
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "ticket_id" in data

        ticket = db.query(Ticket).filter(Ticket.id == data["ticket_id"]).first()
        assert ticket.ai_category_id == category.id
        assert ticket.ai_urgency == 4

        # 5. Assert: the prompt sent to Gemini used this tenant's REAL category
        # (id and name), not the old hardcoded "1: Roads, 2: Utilities, ..." string.
        prompt_sent = mock_client.call_args.kwargs["contents"]
        assert f"{category.id}: Water Leaks" in prompt_sent
    finally:
        db.query(Ticket).filter(Ticket.tenant_id == tenant.id).delete()
        db.query(Category).filter(Category.tenant_id == tenant.id).delete()
        db.delete(tenant)
        db.commit()
        db.close()


def test_receive_webhook_captures_real_sender_email_from_payload(mocker):
    db = SessionLocal()
    tenant = Tenant(name="Sender Email Test Municipality", config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    try:
        mock_response = MagicMock()
        mock_response.parsed = TriageResult(
            category_id=None,
            urgency_score=2,
            extracted_location=None,
            extracted_email=None,
            extracted_phone=None,
            drafted_response="Thanks for reaching out.",
        )
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mocker.patch("ai_pipeline.client.models.generate_content", return_value=mock_response)

        payload = {"from": "real.citizen@example.com", "body": "There's trash piling up on 3rd St."}
        response = client.post(f"/webhook/{tenant.id}", json=payload)

        assert response.status_code == 200
        ticket = db.query(Ticket).filter(Ticket.id == response.json()["ticket_id"]).first()
        # The real envelope sender takes precedence, independent of anything the AI extracted from the body.
        assert ticket.sender_email == "real.citizen@example.com"
    finally:
        db.query(Ticket).filter(Ticket.tenant_id == tenant.id).delete()
        db.query(Category).filter(Category.tenant_id == tenant.id).delete()
        db.delete(tenant)
        db.commit()
        db.close()
