# File: models.py
import enum
from datetime import datetime
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
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)

    # AI Deductions (Nullable initially until the AI pipeline runs)
    ai_category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    ai_urgency = Column(Integer, nullable=True)  # Scale of 1 to 5
    ai_extracted_location = Column(String(500), nullable=True)
    ai_drafted_response = Column(Text, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="tickets")
    category = relationship("Category", back_populates="tickets")
    audit_logs = relationship("AuditLog", back_populates="ticket", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)  # e.g., "AI_PROCESSED", "HUMAN_APPROVED"
    actor = Column(String(100), default="System", nullable=False)  # "System" or User ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="audit_logs")