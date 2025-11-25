import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchStatus } from './api';
import type { Paper, StatusSnapshot } from './types';
import { useEventStream } from './hooks/useEventStream';
import { PaperListView } from './views/PaperList';
import { PaperDetailView } from './views/PaperDetail';
import { TheoryModeView } from './views/TheoryMode';
import { DashboardView } from './views/Dashboard';

const VIEWS = [
  { id: 'list', label: 'Paper List' },
  { id: 'detail', label: 'Paper Detail' },
  { id: 'theory', label: 'Theory Mode' },
  { id: 'dashboard', label: 'Dashboard' },
] as const;

export default function App() {
  const [view, setView] = useState<(typeof VIEWS)[number]['id']>('list');
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [status, setStatus] = useState<StatusSnapshot | null>(null);
  const [events, setEvents] = useState<any[]>([]);

  const refreshStatus = useCallback(async () => {
    try {
      const snapshot = await fetchStatus();
      setStatus(snapshot);
    } catch (error) {
      console.error('Status fetch failed', error);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
    const timer = window.setInterval(refreshStatus, 30_000);
    return () => clearInterval(timer);
  }, [refreshStatus]);

  const onEvent = useCallback(
    (message: MessageEvent) => {
      const parsed = JSON.parse(message.data);
      console.info('[ws] event', parsed);
      setEvents((prev) => [parsed, ...prev].slice(0, 25));
      if (parsed.type === 'task_updated') {
        refreshStatus();
      }
    },
    [refreshStatus],
  );

  useEventStream(onEvent);

  const llmAvailable = status?.llm_available ?? false;

  const renderView = useMemo(() => {
    switch (view) {
      case 'list':
        return (
          <PaperListView
            onSelect={(paper) => {
              setSelectedPaper(paper);
              setView('detail');
            }}
            onRefreshDetail={refreshStatus}
          />
        );
      case 'detail':
        return <PaperDetailView paper={selectedPaper} onUpdate={setSelectedPaper} />;
      case 'theory':
        return <TheoryModeView llmAvailable={llmAvailable} />;
      case 'dashboard':
        return <DashboardView />;
      default:
        return null;
    }
  }, [view, selectedPaper, llmAvailable, refreshStatus]);

  return (
    <main>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>PaperTrail</h1>
          <p style={{ color: llmAvailable ? '#22c55e' : '#f87171' }}>
            LLM {llmAvailable ? 'available' : 'unavailable'} · Embeddings via {status?.embedding_provider || 'initializing'}
          </p>
        </div>
        <nav className="navbar">
          {VIEWS.map((item) => (
            <button key={item.id} onClick={() => setView(item.id)} className={view === item.id ? 'active' : ''}>
              {item.label}
            </button>
          ))}
        </nav>
      </header>
      {renderView}
      <section className="card">
        <h3>Event Feed</h3>
        <ul>
          {events.map((event) => (
            <li key={event.id}>
              [{new Date(event.created_at).toLocaleTimeString()}] {event.type} – {JSON.stringify(event.payload)}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
