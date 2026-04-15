import { useCallback, useEffect, useState } from 'react';
import { Route, Routes, useNavigate } from 'react-router-dom';

import { api } from './api/client';
import { SettingsModal } from './components/SettingsModal';
import { Sidebar } from './components/Sidebar';
import { HomePage } from './pages/HomePage';
import { SessionPage } from './pages/SessionPage';
import { useSessionStore } from './state/sessionStore';

export default function App() {
  const [modalOpen, setModalOpen] = useState(false);
  const setSessions = useSessionStore((s) => s.setSessions);
  const upsertSession = useSessionStore((s) => s.upsertSession);
  const navigate = useNavigate();

  const refreshList = useCallback(async () => {
    try {
      const list = await api.listSessions(100, 0);
      setSessions(list.sessions);
    } catch (err) {
      console.error('failed to load sessions', err);
    }
  }, [setSessions]);

  useEffect(() => {
    refreshList();
    const t = setInterval(refreshList, 8000);
    return () => clearInterval(t);
  }, [refreshList]);

  const handleCreate = async (input: {
    query: string;
    maxIterations: number;
    maxConcurrent: number;
  }) => {
    const { session } = await api.createSession({
      query: input.query,
      max_iterations: input.maxIterations,
      max_concurrent_researchers: input.maxConcurrent,
    });
    upsertSession(session);
    await api.startResearch(session.id);
    navigate(`/session/${session.id}`);
    refreshList();
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar onNewResearch={() => setModalOpen(true)} />
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<HomePage onNewResearch={() => setModalOpen(true)} />} />
          <Route path="/session/:id" element={<SessionPage />} />
        </Routes>
      </main>
      <SettingsModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
