# routers/tickets.py
"""Tenant-facing routes: login, the review queue, categories, approve, export.

All routes here (other than login) require a tenant JWT and derive
tenant_id from the token via require_tenant -- never from the URL.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from auth import create_access_token, require_tenant, verify_password
from database import get_db
from models import Category, Tenant, Ticket, TicketStatus
from schemas import CategoryOut, TenantLoginRequest, TicketApprovalUpdate, TicketOut, TokenResponse
from ticket_service import approve_ticket, export_tickets_csv

router = APIRouter(tags=["tickets"])


@router.post("/api/tenant/login", response_model=TokenResponse)
def tenant_login(credentials: TenantLoginRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.login_email == credentials.email).first()
    if not tenant or not tenant.hashed_password or not verify_password(credentials.password, tenant.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(tenant.id), "role": "tenant"})
    return TokenResponse(access_token=token)


@router.get("/api/tickets/pending", response_model=list[TicketOut])
def get_pending_tickets(db: Session = Depends(get_db), tenant_id: int = Depends(require_tenant)):
    return db.query(Ticket).filter(
        Ticket.tenant_id == tenant_id,
        Ticket.status == TicketStatus.PENDING_REVIEW,
    ).order_by(Ticket.created_at.desc()).all()


@router.get("/api/tickets/approved", response_model=list[TicketOut])
def get_approved_tickets(db: Session = Depends(get_db), tenant_id: int = Depends(require_tenant)):
    # nullslast(): Postgres defaults DESC to NULLS FIRST, which would otherwise put
    # tickets approved before approved_at existed above genuinely recent approvals.
    return db.query(Ticket).filter(
        Ticket.tenant_id == tenant_id,
        Ticket.status == TicketStatus.APPROVED,
    ).order_by(Ticket.approved_at.desc().nullslast()).all()


@router.get("/api/categories", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db), tenant_id: int = Depends(require_tenant)):
    return db.query(Category).filter(Category.tenant_id == tenant_id).order_by(Category.id).all()


@router.get("/api/tickets/export")
def export_tickets(db: Session = Depends(get_db), tenant_id: int = Depends(require_tenant)):
    csv_content = export_tickets_csv(db, tenant_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tickets_export.csv"},
    )


@router.patch("/api/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve_ticket_route(
    ticket_id: int,
    update: TicketApprovalUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(require_tenant),
):
    # Scoped to the authenticated tenant so one municipality can't edit another's tickets by guessing an id.
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.tenant_id == tenant_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return approve_ticket(db, ticket, update.model_dump(exclude_unset=True))
