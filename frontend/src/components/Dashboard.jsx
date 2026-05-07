import { useState, useEffect } from 'react';
import useProjectStore from '../store/projectStore';

const ICONS = {
  plus: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
  ),
  film: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="2" y="2" width="20" height="20" rx="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/><line x1="17" y1="17" x2="22" y2="17"/></svg>
  ),
  trash: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
  ),
  arrow: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
  ),
};

const STATUS_BADGES = {
  draft: { cls: 'badge-amber', label: 'Draft' },
  analyzed: { cls: 'badge-cyan', label: 'Analyzed' },
  audio_ready: { cls: 'badge-purple', label: 'Audio Ready' },
  rendering: { cls: 'badge-pink', label: 'Rendering' },
  complete: { cls: 'badge-green', label: 'Complete' },
};

export default function Dashboard({ onOpenProject }) {
  const { projects, fetchProjects, createProject, deleteProject } = useProjectStore();
  const [showNew, setShowNew] = useState(false);
  const [name, setName] = useState('');
  const [script, setScript] = useState('');

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    const p = await createProject(name.trim(), script.trim());
    if (p) {
      setName('');
      setScript('');
      setShowNew(false);
      onOpenProject(p.id);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '48px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 48 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 8 }}>
            <span className="gradient-text">AutoCinema</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>Cloud-powered vertical video production</p>
        </div>
        <button className="btn-primary" onClick={() => setShowNew(true)}>
          {ICONS.plus} New Project
        </button>
      </div>

      {/* New Project Modal */}
      {showNew && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }} onClick={() => setShowNew(false)}>
          <div className="glass-card animate-fade-in-up" style={{ padding: 32, width: '100%', maxWidth: 560 }} onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 24 }}>Create New Project</h2>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>Project Name</label>
              <input className="input-field" placeholder="My Epic Reel" value={name} onChange={e => setName(e.target.value)} autoFocus />
            </div>
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>Script / Narration Text</label>
              <textarea className="input-field" rows={6} placeholder="Paste your narration script here... (you can also add it later)" value={script} onChange={e => setScript(e.target.value)} />
            </div>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button className="btn-ghost" onClick={() => setShowNew(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleCreate} disabled={!name.trim()}>Create Project {ICONS.arrow}</button>
            </div>
          </div>
        </div>
      )}

      {/* Project List */}
      {projects.length === 0 ? (
        <div className="glass-card" style={{ padding: 64, textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.3 }}>🎬</div>
          <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, color: 'var(--text-secondary)' }}>No projects yet</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Create your first vertical video project to get started.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 16 }}>
          {projects.map((p, i) => {
            const badge = STATUS_BADGES[p.status] || STATUS_BADGES.draft;
            return (
              <div key={p.id} className="glass-card animate-fade-in-up" style={{ padding: 24, cursor: 'pointer', animationDelay: `${i * 50}ms`, display: 'flex', alignItems: 'center', gap: 20 }} onClick={() => onOpenProject(p.id)}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: 'var(--gradient-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: 'var(--accent-purple)' }}>
                  {ICONS.film}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>{p.name}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                    Created {new Date(p.created_at).toLocaleDateString()} · ID: {p.id}
                  </p>
                </div>
                <span className={`badge ${badge.cls}`}>{badge.label}</span>
                <button className="btn-ghost" style={{ padding: 8, color: 'var(--text-muted)' }} onClick={e => { e.stopPropagation(); deleteProject(p.id); }}>
                  {ICONS.trash}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
