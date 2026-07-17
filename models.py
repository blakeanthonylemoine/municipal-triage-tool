# File: models.py
import enum
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base

class TicketStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    config = Column(JSONB, nullable=False, default={})  # Holds target legacy emails/endpoints
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    retention_days = Column(Integer, default=1095)

    # One shared login per tenant, provisioned/reset manually by the admin.
    login_email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)

    # Relationships
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="tenant", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)  # Strictly used to context-prompt the LLM
    is_emergency_flag = Column(Boolean, default=False, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="categories")
    tickets = relationship("Ticket", back_populates="category")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING_REVIEW, nullable=False)
    
    # Ingestion Core
    raw_payload = Column(JSONB, nullable=False)  # The exact, untouched incoming payload
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # The citizen's real sender address, from the forwarded email's actual
    # envelope/header metadata (payload["from"]) -- authoritative when present.
    # Distinct from ai_extracted_email, which is only a best-guess pulled from
    # free text and is the sole option for the secondary web-form channel.
    sender_email = Column(String(255), nullable=True)

    # AI Deductions (Nullable initially until the AI pipeline runs)
    ai_category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    ai_urgency = Column(Integer, nullable=True)  # Scale of 1 to 5
    ai_extracted_location = Column(String(500), nullable=True)
    ai_extracted_email = Column(String(255), nullable=True)
    ai_extracted_phone = Column(String(50), nullable=True)
    ai_drafted_response = Column(Text, nullable=True)

    # Internal UI Flag for the "Requires Immediate Human Review" feature
    flagged_for_safety = Column(Boolean, default=False)

    # Set when a clerk approves the ticket; drives the "recently approved" ordering.
    approved_at = Column(DateTime, nullable=True)
    # Set only if the citizen-notification email actually sent successfully.
    # A missing value on an approved ticket means no email was on file, or the send failed.
    citizen_notified_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="tickets")
    category = relationship("Category", back_populates="tickets")
    audit_logs = relationship("AuditLog", back_populates="ticket", cascade="all, delete-orphan")

    # Tokens Used
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)  # e.g., "AI_PROCESSED", "HUMAN_APPROVED"
    actor = Column(String(100), default="System", nullable=False)  # "System" or User ID
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    notes = Column(Text, nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="audit_logs")