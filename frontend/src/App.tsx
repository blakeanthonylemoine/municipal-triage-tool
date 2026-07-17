import TicketQueue from './components/TicketQueue';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <h1 className="text-xl font-bold text-slate-900">Municipal Triage Tool</h1>
      </header>
      <TicketQueue />
    </div>
  );
}