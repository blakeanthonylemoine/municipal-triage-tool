# tests/test_ticket_review.py
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from auth import create_access_token
from config import settings
from database import SessionLocal
from main import app
from models import Category, Tenant, Ticket, TicketStatus

client = TestClient(app)


def _tenant_headers(tenant_id: int):
    token = create_access_token({"sub": str(tenant_id), "role": "tenant"})
    return {"Authorization": f"Bearer {token}"}


def _make_tenant_with_category(db, name="Ticket Review Test Municipality"):
    tenant = Tenant(name=name, config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    category = Category(tenant_id=tenant.id, name="Roads")
    db.add(category)
    db.commit()
    db.refresh(category)

    return tenant, category


def _cleanup(db, *tenants):
    for tenant in tenants:
        db.query(Ticket).filter(Ticket.tenant_id == tenant.id).delete()
        db.query(Category).filter(Category.tenant_id == tenant.id).delete()
        db.delete(tenant)
    db.commit()
    db.close()


def test_get_categories_scoped_to_authenticated_tenant():
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        response = client.get("/api/categories", headers=_tenant_headers(tenant.id))

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == category.id
        assert data[0]["name"] == "Roads"
    finally:
        _cleanup(db, tenant)


def test_categories_do_not_leak_across_tenants():
    db = SessionLocal()
    tenant_a, _ = _make_tenant_with_category(db, name="Tenant A")
    tenant_b, _ = _make_tenant_with_category(db, name="Tenant B")
    try:
        response = client.get("/api/categories", headers=_tenant_headers(tenant_a.id))

        assert response.status_code == 200
        returned_tenant_ids = {row["tenant_id"] for row in response.json()}
        assert returned_tenant_ids == {tenant_a.id}
    finally:
        _cleanup(db, tenant_a, tenant_b)


def test_approve_ticket_persists_edits_and_sets_status():
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        ticket = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "There is a pothole on Main St."},
            status=TicketStatus.PENDING_REVIEW,
            ai_urgency=2,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        response = client.patch(
            f"/api/tickets/{ticket.id}/approve",
            json={
                "ai_category_id": category.id,
                "ai_urgency": 4,
                "ai_extracted_location": "Main St",
                "ai_drafted_response": "Thanks, we're on it.",
            },
            headers=_tenant_headers(tenant.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["ai_category_id"] == category.id
        assert data["ai_urgency"] == 4
        assert data["ai_extracted_location"] == "Main St"
        assert data["ai_drafted_response"] == "Thanks, we're on it."
        assert data["approved_at"] is not None
        assert data["citizen_notified_at"] is None  # no email on file, nothing to send

        # Approved tickets should no longer show up in the pending queue
        pending_response = client.get("/api/tickets/pending", headers=_tenant_headers(tenant.id))
        assert pending_response.status_code == 200
        assert all(t["id"] != ticket.id for t in pending_response.json())
    finally:
        _cleanup(db, tenant)


def test_approve_ticket_partial_update_leaves_other_fields_unchanged():
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        ticket = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Broken swing at the park."},
            status=TicketStatus.PENDING_REVIEW,
            ai_category_id=category.id,
            ai_urgency=3,
            ai_extracted_location="Founders Park",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        response = client.patch(
            f"/api/tickets/{ticket.id}/approve", json={"ai_urgency": 5}, headers=_tenant_headers(tenant.id)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ai_urgency"] == 5
        assert data["ai_extracted_location"] == "Founders Park"
        assert data["ai_category_id"] == category.id
    finally:
        _cleanup(db, tenant)


def test_approve_nonexistent_ticket_returns_404():
    db = SessionLocal()
    tenant, _ = _make_tenant_with_category(db)
    try:
        response = client.patch(
            "/api/tickets/999999/approve", json={"ai_urgency": 3}, headers=_tenant_headers(tenant.id)
        )
        assert response.status_code == 404
    finally:
        _cleanup(db, tenant)


def test_export_tickets_returns_csv_scoped_to_tenant():
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    other_tenant, _ = _make_tenant_with_category(db, name="Other Export Municipality")
    try:
        ticket = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "There is a pothole on Main St."},
            status=TicketStatus.PENDING_REVIEW,
            ai_category_id=category.id,
            ai_urgency=3,
            ai_extracted_location="Main St",
        )
        other_ticket = Ticket(
            tenant_id=other_tenant.id,
            raw_payload={"body": "This complaint belongs to someone else entirely."},
            status=TicketStatus.PENDING_REVIEW,
        )
        db.add_all([ticket, other_ticket])
        db.commit()
        db.refresh(ticket)

        response = client.get("/api/tickets/export", headers=_tenant_headers(tenant.id))

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert "attachment" in response.headers["content-disposition"]
        assert "Main St" in response.text
        assert category.name in response.text
        assert "someone else entirely" not in response.text
    finally:
        _cleanup(db, tenant, other_tenant)


def test_approve_ticket_sends_notification_and_records_it(mocker, monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "fake-key-for-test")
    mocker.patch("notification_service.resend.Emails.send")

    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        ticket = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Water leak at 5th and Oak."},
            status=TicketStatus.PENDING_REVIEW,
            sender_email="citizen@example.com",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        response = client.patch(
            f"/api/tickets/{ticket.id}/approve",
            json={"ai_drafted_response": "We're dispatching a crew."},
            headers=_tenant_headers(tenant.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved_at"] is not None
        assert data["citizen_notified_at"] is not None
    finally:
        _cleanup(db, tenant)


def test_get_approved_tickets_ordered_by_recency():
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        older = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Older approved ticket"},
            status=TicketStatus.APPROVED,
            approved_at=datetime(2020, 1, 1, tzinfo=UTC),
        )
        newer = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Newer approved ticket"},
            status=TicketStatus.APPROVED,
            approved_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        pending = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Still pending"},
            status=TicketStatus.PENDING_REVIEW,
        )
        db.add_all([older, newer, pending])
        db.commit()
        db.refresh(older)
        db.refresh(newer)
        db.refresh(pending)

        response = client.get("/api/tickets/approved", headers=_tenant_headers(tenant.id))

        assert response.status_code == 200
        ids = [t["id"] for t in response.json()]
        assert ids == [newer.id, older.id]
        assert pending.id not in ids
    finally:
        _cleanup(db, tenant)


def test_approved_tickets_with_null_approved_at_sort_last():
    # Regression: Postgres defaults DESC to NULLS FIRST, which would otherwise
    # rank tickets approved before the approved_at column existed above a
    # genuinely just-approved ticket.
    db = SessionLocal()
    tenant, category = _make_tenant_with_category(db)
    try:
        legacy_null = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Approved before approved_at existed"},
            status=TicketStatus.APPROVED,
            approved_at=None,
        )
        recent = Ticket(
            tenant_id=tenant.id,
            raw_payload={"body": "Genuinely just approved"},
            status=TicketStatus.APPROVED,
            approved_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        db.add_all([legacy_null, recent])
        db.commit()
        db.refresh(legacy_null)
        db.refresh(recent)

        response = client.get("/api/tickets/approved", headers=_tenant_headers(tenant.id))

        assert response.status_code == 200
        ids = [t["id"] for t in response.json()]
        assert ids == [recent.id, legacy_null.id]
    finally:
        _cleanup(db, tenant)


def test_approved_tickets_do_not_leak_across_tenants():
    db = SessionLocal()
    tenant_a, _ = _make_tenant_with_category(db, name="Approved Tenant A")
    tenant_b, _ = _make_tenant_with_category(db, name="Approved Tenant B")
    try:
        ticket_a = Ticket(
            tenant_id=tenant_a.id,
            raw_payload={"body": "A's ticket"},
            status=TicketStatus.APPROVED,
            approved_at=datetime.now(UTC),
        )
        ticket_b = Ticket(
            tenant_id=tenant_b.id,
            raw_payload={"body": "B's ticket"},
            status=TicketStatus.APPROVED,
            approved_at=datetime.now(UTC),
        )
        db.add_all([ticket_a, ticket_b])
        db.commit()
        db.refresh(ticket_a)
        db.refresh(ticket_b)

        response = client.get("/api/tickets/approved", headers=_tenant_headers(tenant_a.id))

        assert response.status_code == 200
        ids = [t["id"] for t in response.json()]
        assert ticket_a.id in ids
        assert ticket_b.id not in ids
    finally:
        _cleanup(db, tenant_a, tenant_b)


def test_cannot_approve_another_tenants_ticket():
    db = SessionLocal()
    owner_tenant, _ = _make_tenant_with_category(db, name="Owner Municipality")
    other_tenant, _ = _make_tenant_with_category(db, name="Other Municipality")
    try:
        ticket = Ticket(
            tenant_id=owner_tenant.id,
            raw_payload={"body": "Streetlight is out."},
            status=TicketStatus.PENDING_REVIEW,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # The other tenant's token should not be able to see or approve this ticket.
        response = client.patch(
            f"/api/tickets/{ticket.id}/approve",
            json={"ai_urgency": 5},
            headers=_tenant_headers(other_tenant.id),
        )
        assert response.status_code == 404

        db.refresh(ticket)
        assert ticket.status == TicketStatus.PENDING_REVIEW
    finally:
        _cleanup(db, owner_tenant, other_tenant)
