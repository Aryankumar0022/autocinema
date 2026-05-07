import { useState } from 'react';
import './index.css';
import Dashboard from './components/Dashboard';
import Workspace from './components/Workspace';

export default function App() {
  const [activeProjectId, setActiveProjectId] = useState(null);

  return (
    <div style={{ minHeight: '100vh' }}>
      {/* Ambient Background Glow */}
      <div style={{
        position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0,
        background: 'radial-gradient(ellipse 80% 60% at 50% -20%, rgba(168,85,247,0.08) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 100%, rgba(6,182,212,0.05) 0%, transparent 50%)',
      }} />

      <div style={{ position: 'relative', zIndex: 1 }}>
        {activeProjectId ? (
          <Workspace
            projectId={activeProjectId}
            onBack={() => setActiveProjectId(null)}
          />
        ) : (
          <Dashboard onOpenProject={(id) => setActiveProjectId(id)} />
        )}
      </div>
    </div>
  );
}
