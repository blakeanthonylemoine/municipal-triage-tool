// Shared types mirroring the backend's schemas.py response models.
// Keeping these in one place instead of redefining slightly different
// local interfaces per component (or using `any`) so the shape can't
// drift out of sync as fields get added.

export type TicketStatus = 'PENDING_REVIEW' | 'APPROVED' | 'ESCALATED' | 'REJECTED';

export interface Ticket {
  id: number;
  tenant_id: number;
  status: TicketStatus;
  raw_payload: { body?: string };
  created_at: string | null;
  sender_email: string | null;
  ai_category_id: number | null;
  ai_urgency: number | null;
  ai_extracted_location: string | null;
  ai_extracted_email: string | null;
  ai_extracted_phone: string | null;
  ai_drafted_response: string | null;
  flagged_for_safety: boolean;
  approved_at: string | null;
  citizen_notified_at: string | null;
  input_tokens: number;
  output_tokens: number;
}

export interface Category {
  id: number;
  tenant_id: number;
  name: string;
  description: string | null;
  is_emergency_flag: boolean;
}

export interface TenantSummary {
  id: number;
  name: string;
  login_email: string | null;
  ticket_count: number;
  pending_count: number;
  input_tokens: number;
  output_tokens: number;
}
