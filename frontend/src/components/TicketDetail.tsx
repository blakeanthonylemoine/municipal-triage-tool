import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import tenantApi from '../tenantApi';
import type { Category, Ticket } from '../types';

const PRIORITY_COLORS: Record<number, string> = {
  5: 'oklch(0.55 0.2 25)',
  4: 'oklch(0.65 0.18 45)',
  3: 'oklch(0.75 0.15 85)',
  2: 'oklch(0.6 0.13 125)',
  1: 'oklch(0.55 0.12 145)',
};

interface TicketDetailProps {
  ticket: Ticket;
  categories: Category[];
  onApproved: (ticketId: number) => void;
}

export default function TicketDetail({ ticket, categories, onApproved }: TicketDetailProps) {
  const [categoryId, setCategoryId] = useState<string>('');
  const [urgency, setUrgency] = useState<string>('');
  const [location, setLocation] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [draftedResponse, setDraftedResponse] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approvedResult, setApprovedResult] = useState<Ticket | null>(null);

  // Reset the edit form whenever a different ticket is selected.
  useEffect(() => {
    setCategoryId(ticket.ai_category_id?.toString() ?? '');
    setUrgency(ticket.ai_urgency?.toString() ?? '');
    setLocation(ticket.ai_extracted_location ?? '');
    setEmail(ticket.ai_extracted_email ?? '');
    setPhone(ticket.ai_extracted_phone ?? '');
    setDraftedResponse(ticket.ai_drafted_response ?? '');
    setError(null);
    setApprovedResult(null);
  }, [ticket.id]);

  const handleApprove = () => {
    setIsSaving(true);
    setError(null);

    tenantApi.patch<Ticket>(`/api/tickets/${ticket.id}/approve`, {
      ai_category_id: categoryId ? Number(categoryId) : null,
      ai_urgency: urgency ? Number(urgency) : null,
      ai_extracted_location: location || null,
      ai_extracted_email: email || null,
      ai_extracted_phone: phone || null,
      ai_drafted_response: draftedResponse || null,
    })
      .then((response) => setApprovedResult(response.data))
      .catch(() => setError('Failed to approve this ticket. Please try again.'))
      .finally(() => setIsSaving(false));
  };

  const priorityColor = PRIORITY_COLORS[Number(urgency)] ?? '#94a3b8';

  if (approvedResult) {
    const recipient = approvedResult.sender_email || approvedResult.ai_extracted_email;
    return (
      <div className="max-w-[820px] bg-white border border-slate-200 rounded-[10px] p-6 flex flex-col items-start gap-3">
        <div className="flex items-center gap-2" style={{ color: 'oklch(0.4 0.1 145)' }}>
          <CheckCircle2 size={20} />
          <span className="font-bold text-[15px]">Ticket #{approvedResult.id} approved</span>
        </div>
        {approvedResult.citizen_notified_at ? (
          <p className="text-sm text-slate-600">Reply sent to <strong>{recipient}</strong>.</p>
        ) : recipient ? (
          <p className="text-sm text-amber-700">Approved, but the reply to {recipient} could not be sent.</p>
        ) : (
          <p className="text-sm text-slate-600">No email was on file for this citizen, so no reply was sent.</p>
        )}
        <button
          onClick={() => onApproved(approvedResult.id)}
          className="text-white px-4 py-2 rounded-md text-sm font-medium mt-2"
          style={{ background: 'oklch(0.27 0.06 250)' }}
        >
          Back to Queue
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-[820px] flex flex-col gap-[18px]">
      <div>
        <div className="flex items-center gap-[10px] mb-1.5">
          <span
            className="w-[26px] h-[26px] rounded-[6px] text-white font-bold text-[13px] flex items-center justify-center flex-none"
            style={{ background: priorityColor }}
          >
            {urgency || '?'}
          </span>
          <h1 className="text-xl font-bold m-0">Ticket #{ticket.id}</h1>
          {ticket.flagged_for_safety && (
            <span className="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2 py-1 rounded-full">
              <AlertTriangle size={14} /> Emergency Flag
            </span>
          )}
        </div>
        <div className="text-[13px] text-slate-500">
          {ticket.created_at ? new Date(ticket.created_at).toLocaleString() : ''}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-[10px] p-[18px_20px] text-[14.5px] leading-relaxed text-slate-700">
        {ticket.raw_payload?.body || 'No text captured.'}
      </div>

      <div className="rounded-[10px] p-[18px_20px]" style={{ background: 'oklch(0.96 0.01 190)', border: '1px solid oklch(0.9 0.03 190)' }}>
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={15} style={{ color: 'oklch(0.4 0.09 190)' }} />
          <span className="font-bold text-[13.5px]" style={{ color: 'oklch(0.35 0.06 190)' }}>AI triage suggestion (editable)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <label className="text-sm text-slate-700">
            Category
            <select
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm bg-white"
              style={{ borderColor: 'oklch(0.85 0.03 190)' }}
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
            >
              <option value="">Unassigned</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
          </label>

          <label className="text-sm text-slate-700">
            Urgency (1-5)
            <input
              type="number"
              min={1}
              max={5}
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm bg-white"
              style={{ borderColor: 'oklch(0.85 0.03 190)' }}
              value={urgency}
              onChange={(e) => setUrgency(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Location
            <input
              type="text"
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm bg-white"
              style={{ borderColor: 'oklch(0.85 0.03 190)' }}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Email
            <input
              type="email"
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm bg-white"
              style={{ borderColor: 'oklch(0.85 0.03 190)' }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700 md:col-span-2">
            Phone
            <input
              type="text"
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm bg-white"
              style={{ borderColor: 'oklch(0.85 0.03 190)' }}
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </label>
        </div>

        <div className="text-[11.5px] font-semibold uppercase tracking-wide text-slate-500 mb-1.5">Drafted Response</div>
        <textarea
          rows={4}
          className="w-full border rounded-md px-3 py-2 text-sm bg-white mb-4"
          style={{ borderColor: 'oklch(0.85 0.03 190)' }}
          value={draftedResponse}
          onChange={(e) => setDraftedResponse(e.target.value)}
        />

        <div className="flex items-center gap-3">
          {error && <span className="text-sm text-red-600">{error}</span>}
          <button
            onClick={handleApprove}
            disabled={isSaving}
            className="flex items-center gap-2 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-60"
            style={{ background: 'oklch(0.27 0.06 250)' }}
          >
            {isSaving && <Loader2 size={16} className="animate-spin" />}
            Approve &amp; Send Reply
          </button>
        </div>
      </div>
    </div>
  );
}
