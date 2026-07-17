# ticket_service.py
"""Ticket domain logic, kept out of the routers -- mirrors the
tenant_service.py pattern already used for tenant provisioning.
"""
import csv
import io

from sqlalchemy.orm import Session

from ai_pipeline import evaluate_ticket
from models import Category, Ticket, TicketStatus


def _categories_prompt_string(db: Session, tenant_id: int) -> str:
    categories = db.query(Category).filter(Category.tenant_id == tenant_id).order_by(Category.id).all()
    return ", ".join(f"{c.id}: {c.name}" for c in categories)


def create_ticket_from_webhook(db: Session, tenant_id: int, payload: dict) -> Ticket:
    complaint_text = payload.get("body", "")
    categories_str = _categories_prompt_string(db, tenant_id)

    ai_result, usage = evaluate_ticket(complaint_text, categories_str)

    ticket = Ticket(
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
        output_tokens=usage["output"],
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def approve_ticket(db: Session, ticket: Ticket, updates: dict) -> Ticket:
    for field, value in updates.items():
        setattr(ticket, field, value)
    ticket.status = TicketStatus.APPROVED
    db.commit()
    db.refresh(ticket)
    return ticket


def export_tickets_csv(db: Session, tenant_id: int) -> str:
    tickets = db.query(Ticket).filter(Ticket.tenant_id == tenant_id).order_by(Ticket.created_at.desc()).all()
    category_names = {c.id: c.name for c in db.query(Category).filter(Category.tenant_id == tenant_id).all()}

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "Ticket ID", "Status", "Created At", "Category", "Urgency",
        "Location", "Email", "Phone", "Original Complaint", "Drafted Response", "Flagged For Safety",
    ])
    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.status.value,
            ticket.created_at.isoformat() if ticket.created_at else "",
            category_names.get(ticket.ai_category_id, ""),
            ticket.ai_urgency or "",
            ticket.ai_extracted_location or "",
            ticket.ai_extracted_email or "",
            ticket.ai_extracted_phone or "",
            (ticket.raw_payload or {}).get("body", ""),
            ticket.ai_drafted_response or "",
            "Yes" if ticket.flagged_for_safety else "No",
        ])
    return buffer.getvalue()
