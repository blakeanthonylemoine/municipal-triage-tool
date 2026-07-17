# tests/test_notifications.py
from config import settings
from database import SessionLocal
from models import Tenant, Ticket, TicketStatus
from notification_service import notify_citizen


def _make_tenant_and_ticket(db, **ticket_kwargs):
    tenant = Tenant(name="Notification Test Municipality", config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    ticket = Ticket(
        tenant_id=tenant.id,
        raw_payload={"body": "Test complaint"},
        status=TicketStatus.PENDING_REVIEW,
        ai_drafted_response="Thanks, we're on it.",
        **ticket_kwargs,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return tenant, ticket


def _cleanup(db, tenant):
    db.query(Ticket).filter(Ticket.tenant_id == tenant.id).delete()
    db.delete(tenant)
    db.commit()
    db.close()


def test_notify_citizen_skips_without_any_email(monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(db)
    try:
        assert notify_citizen(tenant, ticket) is False
    finally:
        _cleanup(db, tenant)


def test_notify_citizen_skips_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", None)
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(db, sender_email="citizen@example.com")
    try:
        assert notify_citizen(tenant, ticket) is False
    finally:
        _cleanup(db, tenant)


def test_notify_citizen_skips_without_drafted_response(monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(db, sender_email="citizen@example.com")
    ticket.ai_drafted_response = None
    db.commit()
    try:
        assert notify_citizen(tenant, ticket) is False
    finally:
        _cleanup(db, tenant)


def test_notify_citizen_prefers_sender_email_over_ai_extracted(monkeypatch, mocker):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    mock_send = mocker.patch("notification_service.resend.Emails.send")
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(
        db, sender_email="real-sender@example.com", ai_extracted_email="guessed@example.com"
    )
    try:
        result = notify_citizen(tenant, ticket)

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[0][0]
        assert call_kwargs["to"] == "real-sender@example.com"
        assert tenant.name in call_kwargs["from"]
        assert call_kwargs["text"] == "Thanks, we're on it."
    finally:
        _cleanup(db, tenant)


def test_notify_citizen_falls_back_to_ai_extracted_email(monkeypatch, mocker):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    mock_send = mocker.patch("notification_service.resend.Emails.send")
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(db, ai_extracted_email="guessed@example.com")
    try:
        result = notify_citizen(tenant, ticket)

        assert result is True
        assert mock_send.call_args[0][0]["to"] == "guessed@example.com"
    finally:
        _cleanup(db, tenant)


def test_notify_citizen_returns_false_when_send_raises(monkeypatch, mocker):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    mocker.patch("notification_service.resend.Emails.send", side_effect=Exception("boom"))
    db = SessionLocal()
    tenant, ticket = _make_tenant_and_ticket(db, sender_email="citizen@example.com")
    try:
        assert notify_citizen(tenant, ticket) is False
    finally:
        _cleanup(db, tenant)
