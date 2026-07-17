import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Download, LogOut, Wrench } from 'lucide-react';
import TicketDetail from './TicketDetail';
import ApprovedTicketDetail from './ApprovedTicketDetail';
import Header from './Header';
import tenantApi from '../tenantApi';
import { clearTenantToken } from '../tenantAuth';
import type { Category, Ticket } from '../types';

const PRIORITY_COLORS: Record<number, string> = {
  5: 'oklch(0.55 0.2 25)',
  4: 'oklch(0.65 0.18 45)',
  3: 'oklch(0.75 0.15 85)',
  2: 'oklch(0.6 0.13 125)',
  1: 'oklch(0.55 0.12 145)',
};

function relativeTime(dateStr: string | null): string {
  if (!dateStr) return '';
  const minutes = Math.round((Date.now() - new Date(dateStr).getTime()) / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? '' : 's'} ago`;
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? '' : 's'} ago`;
}

type QueueView = 'pending' | 'approved';

export default function TicketQueue() {
  const [view, setView] = useState<QueueView>('pending');
  const [pendingTickets, setPendingTickets] = useState<Ticket[]>([]);
  const [approvedTickets, setApprovedTickets] = useState<Ticket[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [toolsOpen, setToolsOpen] = useState(false);
  const navigate = useNavigate();

  const fetchPending = () => {
    tenantApi.get('/api/tickets/pending')
      .then(response => setPendingTickets(response.data))
      .catch(error => console.error("Error fetching pending tickets:", error));
  };

  const fetchApproved = () => {
    tenantApi.get('/api/tickets/approved')
      .then(response => setApprovedTickets(response.data))
      .catch(error => console.error("Error fetching approved tickets:", error));
  };

  useEffect(() => {
    fetchPending();
    fetchApproved();
    tenantApi.get('/api/categories')
      .then(response => setCategories(response.data))
      .catch(error => console.error("Error fetching categories:", error));
  }, []);

  const handleApproved = () => {
    setSelectedId(null);
    fetchPending();
    fetchApproved();
  };

  const handleSelectView = (nextView: QueueView) => {
    setView(nextView);
    setSelectedId(null);
  };

  const handleLogout = () => {
    clearTenantToken();
    navigate('/login');
  };

  const handleExportCsv = () => {
    setToolsOpen(false);
    tenantApi.get('/api/tickets/export', { responseType: 'blob' })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'tickets_export.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => console.error('Error exporting tickets:', error));
  };

  const tickets = view === 'pending' ? pendingTickets : approvedTickets;
  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId) ?? null;
  const categoryName = (id: number | null) => categories.find((c) => c.id === id)?.name;

  return (
    <div className="h-screen flex flex-col">
      <Header>
        <div className="relative">
          <button
            onClick={() => setToolsOpen((open) => !open)}
            className="flex items-center gap-2 text-sm text-white/80 hover:text-white"
          >
            <Wrench size={16} /> Tools
          </button>
          {toolsOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-lg shadow-lg z-10 text-slate-700">
              <button
                onClick={handleExportCsv}
                className="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 flex items-center gap-2"
              >
                <Download size={14} /> Export All Tickets (CSV)
              </button>
            </div>
          )}
        </div>
        <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-white/80 hover:text-white ml-4">
          <LogOut size={16} /> Log Out
        </button>
      </Header>

      <div className="flex-1 flex flex-col lg:flex-row min-h-0">
        <div className="lg:w-[360px] lg:flex-none border-b lg:border-b-0 lg:border-r border-black/[0.06] bg-white flex flex-col min-h-0">
          <div className="flex border-b border-black/[0.06] flex-none">
            <button
              onClick={() => handleSelectView('pending')}
              className="flex-1 px-[18px] py-[14px] font-bold text-[15px] text-left"
              style={
                view === 'pending'
                  ? { color: 'oklch(0.27 0.06 250)', borderBottom: '2px solid oklch(0.27 0.06 250)', marginBottom: '-1px' }
                  : { color: 'oklch(0.5 0.01 90)' }
              }
            >
              Inbox <span className="font-medium">({pendingTickets.length})</span>
            </button>
            <button
              onClick={() => handleSelectView('approved')}
              className="flex-1 px-[18px] py-[14px] font-bold text-[15px] text-left"
              style={
                view === 'approved'
                  ? { color: 'oklch(0.27 0.06 250)', borderBottom: '2px solid oklch(0.27 0.06 250)', marginBottom: '-1px' }
                  : { color: 'oklch(0.5 0.01 90)' }
              }
            >
              Approved <span className="font-medium">({approvedTickets.length})</span>
            </button>
          </div>
          <div className="overflow-y-auto flex-1">
            {tickets.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500">
                {view === 'pending'
                  ? "No tickets pending review. You're all caught up!"
                  : 'No tickets have been approved yet.'}
              </div>
            ) : (
              tickets.map((ticket) => (
                <button
                  key={ticket.id}
                  onClick={() => setSelectedId(ticket.id)}
                  className="w-full text-left px-[18px] py-3 border-b border-black/[0.04] block"
                  style={
                    ticket.id === selectedId
                      ? { background: 'oklch(0.94 0.01 250 / 0.5)', borderLeft: '3px solid oklch(0.27 0.06 250)' }
                      : undefined
                  }
                >
                  <div className="flex gap-2 items-center mb-[3px]">
                    <span
                      className="w-5 h-5 rounded-[5px] text-white text-[11px] font-bold flex items-center justify-center flex-none"
                      style={{ background: PRIORITY_COLORS[ticket.ai_urgency ?? 1] ?? '#94a3b8' }}
                    >
                      {ticket.ai_urgency ?? '?'}
                    </span>
                    <span className="font-semibold text-[13px] flex-1 truncate">
                      {ticket.raw_payload?.body?.slice(0, 60) || 'Waiting for AI extraction...'}
                    </span>
                    {ticket.flagged_for_safety && (
                      <AlertTriangle size={13} className="text-red-600 flex-none" aria-label="Emergency flag" />
                    )}
                  </div>
                  <div className="text-xs text-slate-500 pl-7">
                    {categoryName(ticket.ai_category_id) ?? 'Uncategorized'} ·{' '}
                    {view === 'pending'
                      ? relativeTime(ticket.created_at)
                      : `approved ${relativeTime(ticket.approved_at)}`}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {selectedTicket ? (
            view === 'pending' ? (
              <TicketDetail ticket={selectedTicket} categories={categories} onApproved={handleApproved} />
            ) : (
              <ApprovedTicketDetail ticket={selectedTicket} categories={categories} />
            )
          ) : (
            <div className="h-full flex items-center justify-center text-sm text-slate-500">
              Select a ticket to review the original text and AI analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
