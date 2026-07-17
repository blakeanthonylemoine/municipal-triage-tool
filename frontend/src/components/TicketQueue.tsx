import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Clock, Download, LogOut, Wrench } from 'lucide-react';
import TicketDetail from './TicketDetail';
import tenantApi from '../tenantApi';
import { clearTenantToken } from '../tenantAuth';
import type { Category, Ticket } from '../types';

export default function TicketQueue() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [toolsOpen, setToolsOpen] = useState(false);
  const navigate = useNavigate();

  const fetchTickets = () => {
    tenantApi.get('/api/tickets/pending')
      .then(response => setTickets(response.data))
      .catch(error => console.error("Error fetching tickets:", error));
  };

  useEffect(() => {
    fetchTickets();
    tenantApi.get('/api/categories')
      .then(response => setCategories(response.data))
      .catch(error => console.error("Error fetching categories:", error));
  }, []);

  const handleApproved = () => {
    setSelectedId(null);
    fetchTickets();
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

  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId) ?? null;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Pending Review Queue</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <button
              onClick={() => setToolsOpen((open) => !open)}
              className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
            >
              <Wrench size={16} /> Tools
            </button>
            {toolsOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-lg shadow-lg z-10">
                <button
                  onClick={handleExportCsv}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                >
                  <Download size={14} /> Export All Tickets (CSV)
                </button>
              </div>
            )}
          </div>
          <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
            <LogOut size={16} /> Log Out
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="flex flex-col gap-4">
          {tickets.length === 0 ? (
            <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
              No tickets pending review. You're all caught up!
            </div>
          ) : (
            tickets.map((ticket: Ticket) => (
              <button
                key={ticket.id}
                onClick={() => setSelectedId(ticket.id)}
                className={`text-left bg-white border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow flex justify-between items-start ${
                  ticket.id === selectedId ? 'border-blue-500 ring-1 ring-blue-500' : 'border-slate-200'
                }`}
              >
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold text-slate-900">Ticket #{ticket.id}</span>
                    {ticket.flagged_for_safety && (
                      <span className="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2 py-1 rounded-full">
                        <AlertTriangle size={14} /> Emergency Flag
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600 line-clamp-2 max-w-2xl">
                    {ticket.ai_drafted_response || "Waiting for AI extraction..."}
                  </p>
                </div>

                <div className="flex flex-col items-end gap-2 text-sm shrink-0 ml-4">
                  <span className="flex items-center gap-1 text-slate-500">
                    <Clock size={14} />
                    {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : '—'}
                  </span>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
                    Urgency: {ticket.ai_urgency || "?"}/5
                  </span>
                </div>
              </button>
            ))
          )}
        </div>

        <div className="lg:sticky lg:top-6">
          {selectedTicket ? (
            <TicketDetail ticket={selectedTicket} categories={categories} onApproved={handleApproved} />
          ) : (
            <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
              Select a ticket to review the original text and AI analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
