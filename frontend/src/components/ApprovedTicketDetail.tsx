import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { Category, Ticket } from '../types';

const PRIORITY_COLORS: Record<number, string> = {
  5: 'oklch(0.55 0.2 25)',
  4: 'oklch(0.65 0.18 45)',
  3: 'oklch(0.75 0.15 85)',
  2: 'oklch(0.6 0.13 125)',
  1: 'oklch(0.55 0.12 145)',
};

interface ApprovedTicketDetailProps {
  ticket: Ticket;
  categories: Category[];
}

export default function ApprovedTicketDetail({ ticket, categories }: ApprovedTicketDetailProps) {
  const categoryName = categories.find((c) => c.id === ticket.ai_category_id)?.name ?? 'Uncategorized';
  const recipient = ticket.sender_email || ticket.ai_extracted_email;
  const priorityColor = PRIORITY_COLORS[ticket.ai_urgency ?? 1] ?? '#94a3b8';

  return (
    <div className="max-w-[820px] flex flex-col gap-[18px]">
      <div>
        <div className="flex items-center gap-[10px] mb-1.5">
          <span
            className="w-[26px] h-[26px] rounded-[6px] text-white font-bold text-[13px] flex items-center justify-center flex-none"
            style={{ background: priorityColor }}
          >
            {ticket.ai_urgency ?? '?'}
          </span>
          <h1 className="text-xl font-bold m-0">Ticket #{ticket.id}</h1>
          {ticket.flagged_for_safety && (
            <span className="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2 py-1 rounded-full">
              <AlertTriangle size={14} /> Emergency Flag
            </span>
          )}
        </div>
        <div className="text-[13px] text-slate-500">
          Approved {ticket.approved_at ? new Date(ticket.approved_at).toLocaleString() : ''}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-[10px] p-[18px_20px] text-[14.5px] leading-relaxed text-slate-700">
        {ticket.raw_payload?.body || 'No text captured.'}
      </div>

      <div className="rounded-[10px] p-[18px_20px]" style={{ background: 'oklch(0.96 0.01 190)', border: '1px solid oklch(0.9 0.03 190)' }}>
        <div className="flex items-center gap-2 mb-3" style={{ color: 'oklch(0.4 0.1 145)' }}>
          <CheckCircle2 size={15} />
          <span className="font-bold text-[13.5px]">Approved</span>
        </div>

        <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm mb-4">
          <div><span className="text-slate-500">Category:</span> {categoryName}</div>
          <div><span className="text-slate-500">Location:</span> {ticket.ai_extracted_location || '—'}</div>
          <div><span className="text-slate-500">Email:</span> {ticket.ai_extracted_email || '—'}</div>
          <div><span className="text-slate-500">Phone:</span> {ticket.ai_extracted_phone || '—'}</div>
        </div>

        <div className="text-[11.5px] font-semibold uppercase tracking-wide text-slate-500 mb-1.5">Response Sent</div>
        <div
          className="bg-white border rounded-md px-3 py-2 text-sm mb-3"
          style={{ borderColor: 'oklch(0.85 0.03 190)' }}
        >
          {ticket.ai_drafted_response || '—'}
        </div>

        <div className="text-sm">
          {ticket.citizen_notified_at ? (
            <span className="text-slate-600">
              Emailed to <strong>{recipient}</strong> on {new Date(ticket.citizen_notified_at).toLocaleString()}.
            </span>
          ) : recipient ? (
            <span className="text-amber-700">Not sent — delivery to {recipient} failed.</span>
          ) : (
            <span className="text-slate-600">No email was on file; no notification was sent.</span>
          )}
        </div>
      </div>
    </div>
  );
}
