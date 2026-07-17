import { useEffect, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import tenantApi from '../tenantApi';
import type { Category, Ticket } from '../types';

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

  // Reset the edit form whenever a different ticket is selected.
  useEffect(() => {
    setCategoryId(ticket.ai_category_id?.toString() ?? '');
    setUrgency(ticket.ai_urgency?.toString() ?? '');
    setLocation(ticket.ai_extracted_location ?? '');
    setEmail(ticket.ai_extracted_email ?? '');
    setPhone(ticket.ai_extracted_phone ?? '');
    setDraftedResponse(ticket.ai_drafted_response ?? '');
    setError(null);
  }, [ticket.id]);

  const handleApprove = () => {
    setIsSaving(true);
    setError(null);

    tenantApi.patch(`/api/tickets/${ticket.id}/approve`, {
      ai_category_id: categoryId ? Number(categoryId) : null,
      ai_urgency: urgency ? Number(urgency) : null,
      ai_extracted_location: location || null,
      ai_extracted_email: email || null,
      ai_extracted_phone: phone || null,
      ai_drafted_response: draftedResponse || null,
    })
      .then(() => onApproved(ticket.id))
      .catch(() => setError('Failed to approve this ticket. Please try again.'))
      .finally(() => setIsSaving(false));
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col h-full">
      <div className="p-5 border-b border-slate-200 flex items-center justify-between">
        <span className="font-semibold text-slate-900">Ticket #{ticket.id}</span>
        {ticket.flagged_for_safety && (
          <span className="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2 py-1 rounded-full">
            <AlertTriangle size={14} /> Emergency Flag
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 p-5 overflow-y-auto">
        <div>
          <h3 className="text-xs font-semibold uppercase text-slate-500 mb-2">Original Citizen Text</h3>
          <p className="text-sm text-slate-700 whitespace-pre-wrap bg-slate-50 border border-slate-200 rounded-lg p-4">
            {ticket.raw_payload?.body || 'No text captured.'}
          </p>
        </div>

        <div className="flex flex-col gap-4">
          <h3 className="text-xs font-semibold uppercase text-slate-500">AI Analysis (editable)</h3>

          <label className="text-sm text-slate-700">
            Category
            <select
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
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
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
              value={urgency}
              onChange={(e) => setUrgency(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Location
            <input
              type="text"
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Email
            <input
              type="email"
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Phone
            <input
              type="text"
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </label>

          <label className="text-sm text-slate-700">
            Drafted Response
            <textarea
              rows={4}
              className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
              value={draftedResponse}
              onChange={(e) => setDraftedResponse(e.target.value)}
            />
          </label>
        </div>
      </div>

      <div className="p-5 border-t border-slate-200 flex items-center justify-end gap-3">
        {error && <span className="text-sm text-red-600">{error}</span>}
        <button
          onClick={handleApprove}
          disabled={isSaving}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
        >
          {isSaving && <Loader2 size={16} className="animate-spin" />}
          Approve
        </button>
      </div>
    </div>
  );
}
