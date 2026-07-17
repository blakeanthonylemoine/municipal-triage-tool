# routers/webhook.py
"""Ingestion endpoint hit by the tenant's automated email-forwarding
setup, not a logged-in clerk -- deliberately outside the JWT login
system (see TASKS.md).

This used to be two separate routes: /api/v1/intake/{tenant_id} (saved
the raw payload only, predating the AI pipeline) and /webhook/{tenant_id}
(ran the AI pipeline but never checked the tenant existed). Consolidated
into one route that does both: validates the tenant, then runs the
pipeline.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Tenant
from ticket_service import create_ticket_from_webhook

router = APIRouter(tags=["webhook"])


@router.post("/webhook/{tenant_id}")
async def receive_webhook(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    payload = await request.json()
    ticket = create_ticket_from_webhook(db, tenant_id, payload)
    return {"status": "success", "ticket_id": ticket.id}
