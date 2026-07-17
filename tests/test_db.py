# tests/test_db.py
from database import SessionLocal
from models import Tenant, Ticket, TicketStatus

def test_create_tenant_and_ticket():
    db = SessionLocal()
    
    # 1. Test Tenant Creation
    new_tenant = Tenant(name="Test Municipality", config={"inbound_email": "test@mock.gov"})
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    
    assert new_tenant.id is not None
    assert new_tenant.name == "Test Municipality"
    
    # 2. Test Ticket Relationship and Defaults
    new_ticket = Ticket(tenant_id=new_tenant.id, raw_payload={"body": "Pothole on 5th!"})
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    assert new_ticket.id is not None
    # Ensure our default enum status is correctly applied
    assert new_ticket.status == TicketStatus.PENDING_REVIEW
    
    # Cleanup for subsequent runs
    db.delete(new_ticket)
    db.delete(new_tenant)
    db.commit()
    db.close()