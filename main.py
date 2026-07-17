# main.py
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ai_pipeline import evaluate_ticket
from database import get_db
from models import Category, Tenant, Ticket, TicketStatus


class TicketApprovalUpdate(BaseModel):
    ai_category_id: int | None = None
    ai_urgency: int | None = None
    ai_extracted_location: str | None = None
    ai_extracted_email: str | None = None
    ai_extracted_phone: str | None = None
    ai_drafted_response: str | None = None

# This is the line that was missing. It initializes the FastAPI application.
app = FastAPI(title="Municipal Triage Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow the Vite dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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

@app.get("/api/tenants/{tenant_id}/tickets/pending")
def get_pending_tickets(tenant_id: int, db: Session = Depends(get_db)):
    # Fetch only tickets for this specific municipality
    tickets = db.query(Ticket).filter(
        Ticket.tenant_id == tenant_id,
        Ticket.status == TicketStatus.PENDING_REVIEW
    ).order_by(Ticket.created_at.desc()).all()
    
    return tickets

@app.get("/api/tenants/{tenant_id}/categories")
def get_categories(tenant_id: int, db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.tenant_id == tenant_id).order_by(Category.id).all()

@app.patch("/api/tickets/{ticket_id}/approve")
def approve_ticket(ticket_id: int, update: TicketApprovalUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Persist whatever fields the clerk edited, then approve.
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    ticket.status = TicketStatus.APPROVED

    db.commit()
    db.refresh(ticket)
    return ticket

@app.post("/webhook/{tenant_id}")
async def receive_webhook(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    # 1. Capture the incoming data
    payload = await request.json()
    complaint_text = payload.get("body", "")
    
    # 2. Hardcode categories just to prove the pipeline works (we will make this dynamic later)
    categories_str = "1: Roads, 2: Utilities, 3: Parks, 4: Code Violations"
    
    # 3. Run it through the Gemini pipeline you built
    ai_result, usage = evaluate_ticket(complaint_text, categories_str)
    
    # 4. Save everything to the database
    new_ticket = Ticket(
        tenant_id=tenant_id,
        raw_payload=payload,
        status=TicketStatus.PENDING_REVIEW,
        ai_category_id=ai_result.category_id,
        ai_urgency=ai_result.urgency_score,
        ai_extracted_location=ai_result.extracted_location,
        ai_extracted_email=ai_result.extracted_email,
        ai_extracted_phone=ai_result.extracted_phone,
        ai_drafted_response=ai_result.drafted_response,
        input_tokens=usage["input"],
        output_tokens=usage["output"]
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    return {"status": "success", "ticket_id": new_ticket.id}