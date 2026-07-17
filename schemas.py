# schemas.py
"""Pydantic request/response models, shared across routers.

Response models exist specifically so sensitive columns (e.g.
Tenant.hashed_password) can never leak by omission -- FastAPI filters
to exactly what's declared here, not whatever the ORM object happens
to have.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models import TicketStatus


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class TenantLoginRequest(BaseModel):
    email: str
    password: str


class TenantCreateRequest(BaseModel):
    name: str
    login_email: str
    password: str


class TenantCredentialResetRequest(BaseModel):
    login_email: str | None = None
    password: str | None = None


class TicketApprovalUpdate(BaseModel):
    ai_category_id: int | None = None
    ai_urgency: int | None = None
    ai_extracted_location: str | None = None
    ai_extracted_email: str | None = None
    ai_extracted_phone: str | None = None
    ai_drafted_response: str | None = None


class TenantOut(BaseModel):
    id: int
    name: str
    login_email: str | None
    ticket_count: int
    pending_count: int
    input_tokens: int
    output_tokens: int


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    name: str
    description: str | None
    is_emergency_flag: bool


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    status: TicketStatus
    raw_payload: dict
    created_at: datetime | None
    ai_category_id: int | None
    ai_urgency: int | None
    ai_extracted_location: str | None
    ai_extracted_email: str | None
    ai_extracted_phone: str | None
    ai_drafted_response: str | None
    flagged_for_safety: bool
    input_tokens: int
    output_tokens: int
