import { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Clock } from 'lucide-react';
import TicketDetail from './TicketDetail';

export default function TicketQueue() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Hardcoded for the MVP pilot phase (e.g., Tenant 1 is the current dev/test tenant)
  const CURRENT_TENANT_ID = 1;

  const fetchTickets = () => {
    axios.get(`http://localhost:8000/api/tenants/${CURRENT_TENANT_ID}/tickets/pending`)
      .then(response => setTickets(response.data))
      .catch(error => console.error("Error fetching tickets:", error));
  };

  useEffect(() => {
    fetchTickets();
    axios.get(`http://localhost:8000/api/tenants/${CURRENT_TENANT_ID}/categories`)
      .then(response => setCategories(response.data))
      .catch(error => console.error("Error fetching categories:", error));
  }, []);

  const handleApproved = () => {
    setSelectedId(null);
    fetchTickets();
  };

  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId) ?? null;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Pending Review Queue</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="flex flex-col gap-4">
          {tickets.length === 0 ? (
            <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
              No tickets pending review. You're all caught up!
            </div>
          ) : (
            tickets.map((ticket: any) => (
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
                    {new Date(ticket.created_at).toLocaleDateString()}
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
