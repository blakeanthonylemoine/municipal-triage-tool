# tests/test_tenant_auth.py
from fastapi.testclient import TestClient

from auth import create_access_token
from database import SessionLocal
from main import app
from models import Tenant
from tenant_service import provision_tenant

client = TestClient(app)


def test_tenant_login_rejects_unknown_email():
    response = client.post("/api/tenant/login", json={"email": "no-such-tenant@example.com", "password": "whatever"})

    assert response.status_code == 401


def test_tenant_login_rejects_wrong_password():
    db = SessionLocal()
    tenant = provision_tenant(
        db, name="Tenant Login Test Municipality", login_email="tenant-login-test@example.com", password="correct-password"
    )
    try:
        response = client.post(
            "/api/tenant/login", json={"email": "tenant-login-test@example.com", "password": "wrong-password"}
        )
        assert response.status_code == 401
    finally:
        db.delete(tenant)
        db.commit()
        db.close()


def test_tenant_login_succeeds_with_correct_credentials():
    db = SessionLocal()
    tenant = provision_tenant(
        db, name="Tenant Login Test Municipality", login_email="tenant-login-test-2@example.com", password="correct-password"
    )
    try:
        response = client.post(
            "/api/tenant/login", json={"email": "tenant-login-test-2@example.com", "password": "correct-password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["access_token"]
    finally:
        db.delete(tenant)
        db.commit()
        db.close()


def test_tenant_login_rejects_tenant_with_no_credentials_configured():
    db = SessionLocal()
    tenant = Tenant(name="No Credentials Municipality", config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    try:
        response = client.post("/api/tenant/login", json={"email": "irrelevant@example.com", "password": "whatever"})
        assert response.status_code == 401
    finally:
        db.delete(tenant)
        db.commit()
        db.close()


def test_tenant_scoped_routes_reject_missing_credentials():
    response = client.get("/api/tickets/pending")

    assert response.status_code in (401, 403)


def test_tenant_scoped_routes_reject_admin_token():
    admin_token = create_access_token({"sub": "admin", "role": "admin"})

    response = client.get("/api/tickets/pending", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 403
