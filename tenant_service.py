# tenant_service.py
"""Tenant provisioning logic, kept separate from the admin routes so a
future self-serve signup flow can call the same functions instead of
duplicating them.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import hash_password
from models import Tenant, Ticket, TicketStatus


def provision_tenant(db: Session, name: str, login_email: str, password: str) -> Tenant:
    tenant = Tenant(name=name, login_email=login_email, hashed_password=hash_password(password), config={})
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def reset_tenant_credentials(db: Session, tenant: Tenant, login_email: str | None, password: str | None) -> Tenant:
    if login_email:
        tenant.login_email = login_email
    if password:
        tenant.hashed_password = hash_password(password)
    db.commit()
    db.refresh(tenant)
    return tenant


def tenant_summary(db: Session, tenant: Tenant) -> dict:
    ticket_count = db.query(Ticket).filter(Ticket.tenant_id == tenant.id).count()
    pending_count = db.query(Ticket).filter(
        Ticket.tenant_id == tenant.id, Ticket.status == TicketStatus.PENDING_REVIEW
    ).count()
    input_tokens, output_tokens = db.query(
        func.coalesce(func.sum(Ticket.input_tokens), 0),
        func.coalesce(func.sum(Ticket.output_tokens), 0),
    ).filter(Ticket.tenant_id == tenant.id).first()

    return {
        "id": tenant.id,
        "name": tenant.name,
        "login_email": tenant.login_email,
        "ticket_count": ticket_count,
        "pending_count": pending_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
