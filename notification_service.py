# notification_service.py
"""Sends the clerk-approved drafted response to the citizen via Resend.

Best-effort: a failed or skipped send never blocks approval. The ticket's
status change is the source of truth; whether the citizen was actually
notified is recorded separately (Ticket.citizen_notified_at) so the UI
can show clerks the real outcome instead of assuming success.
"""
import resend

from config import settings
from models import Tenant, Ticket


def notify_citizen(tenant: Tenant, ticket: Ticket) -> bool:
    """Returns True only if the email was actually sent."""
    recipient = ticket.sender_email or ticket.ai_extracted_email
    if not recipient or not settings.resend_api_key or not ticket.ai_drafted_response:
        return False

    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send({
            "from": f"{tenant.name} via CivicTriage <{settings.notification_from_email}>",
            "to": recipient,
            "subject": "Update on your report",
            "text": ticket.ai_drafted_response,
        })
        return True
    except Exception as exc:
        print(f"Failed to send citizen notification for ticket {ticket.id}: {exc}")
        return False
