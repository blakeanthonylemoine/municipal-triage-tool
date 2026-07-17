# tests/test_admin_api.py
from fastapi.testclient import TestClient

from auth import create_access_token, hash_password, verify_password
from config import settings
from database import SessionLocal
from main import app
from models import Tenant

client = TestClient(app)


def _admin_headers():
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


def test_admin_login_fails_when_not_configured(monkeypatch):
    # settings is a singleton loaded once at import time, so patch its
    # attributes directly rather than the environment (which it no
    # longer re-reads per-request).
    monkeypatch.setattr(settings, "admin_email", None)
    monkeypatch.setattr(settings, "admin_password_hash", None)

    response = client.post("/api/admin/login", json={"email": "admin@example.com", "password": "whatever"})

    assert response.status_code == 500


def test_admin_login_rejects_wrong_password(monkeypatch):
    monkeypatch.setattr(settings, "admin_email", "admin@example.com")
    monkeypatch.setattr(settings, "admin_password_hash", hash_password("correct-password"))

    response = client.post("/api/admin/login", json={"email": "admin@example.com", "password": "wrong-password"})

    assert response.status_code == 401


def test_admin_login_succeeds_with_correct_credentials(monkeypatch):
    monkeypatch.setattr(settings, "admin_email", "admin@example.com")
    monkeypatch.setattr(settings, "admin_password_hash", hash_password("correct-password"))

    response = client.post("/api/admin/login", json={"email": "admin@example.com", "password": "correct-password"})

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_admin_routes_reject_missing_credentials():
    response = client.get("/api/admin/tenants")

    assert response.status_code in (401, 403)


def test_admin_routes_reject_non_admin_token():
    tenant_token = create_access_token({"sub": "1", "role": "tenant"})

    response = client.get("/api/admin/tenants", headers={"Authorization": f"Bearer {tenant_token}"})

    assert response.status_code == 403


def test_create_list_and_reset_tenant_credentials():
    db = SessionLocal()
    tenant_id = None
    try:
        create_response = client.post(
            "/api/admin/tenants",
            json={
                "name": "Admin API Test Municipality",
                "login_email": "admin-api-test@example.com",
                "password": "initial-pass",
            },
            headers=_admin_headers(),
        )
        assert create_response.status_code == 200
        created = create_response.json()
        assert created["name"] == "Admin API Test Municipality"
        assert created["login_email"] == "admin-api-test@example.com"
        assert "hashed_password" not in created
        tenant_id = created["id"]

        # Duplicate login_email should be rejected
        dup_response = client.post(
            "/api/admin/tenants",
            json={"name": "Duplicate", "login_email": "admin-api-test@example.com", "password": "whatever"},
            headers=_admin_headers(),
        )
        assert dup_response.status_code == 400

        # Shows up in the tenant list with stats
        list_response = client.get("/api/admin/tenants", headers=_admin_headers())
        assert list_response.status_code == 200
        listed = next(t for t in list_response.json() if t["id"] == tenant_id)
        assert listed["ticket_count"] == 0
        assert listed["pending_count"] == 0
        assert "hashed_password" not in listed

        # Reset credentials
        reset_response = client.patch(
            f"/api/admin/tenants/{tenant_id}/credentials",
            json={"login_email": "reset@example.com", "password": "new-password"},
            headers=_admin_headers(),
        )
        assert reset_response.status_code == 200
        assert reset_response.json()["login_email"] == "reset@example.com"

        # The new password actually verifies against the stored hash
        db.expire_all()
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        assert verify_password("new-password", tenant.hashed_password)
    finally:
        if tenant_id is not None:
            db.query(Tenant).filter(Tenant.id == tenant_id).delete()
            db.commit()
        db.close()


def test_reset_credentials_for_missing_tenant_returns_404():
    response = client.patch(
        "/api/admin/tenants/999999/credentials",
        json={"password": "whatever"},
        headers=_admin_headers(),
    )

    assert response.status_code == 404
