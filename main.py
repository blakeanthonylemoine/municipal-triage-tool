# main.py
from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Tenant, Ticket, TicketStatus

# This is the line that was missing. It initializes the FastAPI application.
app = FastAPI(title="Municipal Triage Tool API")

@app.post("/api/v1/intake/{tenant_id}")
async def receive_inbound_request(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    # 1. Verify the tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 2. Extract the raw JSON payload from the incoming webhook
    try:
        raw_payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # 3. Create the pending ticket (The ML pipeline will process this later)
    new_ticket = Ticket(
        tenant_id=tenant.id,
        raw_payload=raw_payload,
        status=TicketStatus.PENDING_REVIEW
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return {"status": "success", "ticket_id": new_ticket.id, "message": "Request ingested."}
