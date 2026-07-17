# routers/admin.py
"""Admin-only routes: login, tenant listing/creation, credential resets.

All routes here (other than login) require an admin JWT via require_admin.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import create_access_token, require_admin, verify_password
from config import settings
from database import get_db
from models import Tenant
from schemas import AdminLoginRequest, TenantCreateRequest, TenantCredentialResetRequest, TenantOut, TokenResponse
from tenant_service import provision_tenant, reset_tenant_credentials, tenant_summary

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenResponse)
def admin_login(credentials: AdminLoginRequest):
    if not settings.admin_email or not settings.admin_password_hash:
        raise HTTPException(status_code=500, detail="Admin credentials are not configured")

    if credentials.email != settings.admin_email or not verify_password(
        credentials.password, settings.admin_password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": "admin", "role": "admin"})
    return TokenResponse(access_token=token)


@router.get("/tenants", response_model=list[TenantOut])
def list_tenants_for_admin(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    tenants = db.query(Tenant).order_by(Tenant.id).all()
    return [tenant_summary(db, tenant) for tenant in tenants]


@router.post("/tenants", response_model=TenantOut)
def create_tenant_for_admin(
    payload: TenantCreateRequest, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)
):
    existing = db.query(Tenant).filter(Tenant.login_email == payload.login_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A tenant with this login email already exists")

    tenant = provision_tenant(db, name=payload.name, login_email=payload.login_email, password=payload.password)
    return tenant_summary(db, tenant)


@router.patch("/tenants/{tenant_id}/credentials", response_model=TenantOut)
def reset_tenant_credentials_route(
    tenant_id: int,
    payload: TenantCredentialResetRequest,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant = reset_tenant_credentials(db, tenant, payload.login_email, payload.password)
    return tenant_summary(db, tenant)
