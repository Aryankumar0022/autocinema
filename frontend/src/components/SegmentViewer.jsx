import useProjectStore from '../store/projectStore';

export default function SegmentViewer() {
  const { currentProject, setStep } = useProjectStore();
  const segments = currentProject?.segments || [];

  if (segments.length === 0) {
    return (
      <div className="glass-card animate-fade-in-up" style={{ padding: 48, textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>No segments yet. Analyze your script first.</p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 800 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
          <span style={{ color: 'var(--accent-cyan)', marginRight: 10 }}>📋</span>
          Script Segments
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Gemini split your script into {segments.length} segments. Review the prompts below.
        </p>
      </div>

      <div style={{ display: 'grid', gap: 16, marginBottom: 24 }}>
        {segments.map((seg, i) => (
          <div key={seg.id} className="glass-card" style={{ padding: 20, animationDelay: `${i * 60}ms` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <span style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--gradient-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 800 }}>{i + 1}</span>
              <span className="badge badge-cyan">{seg.duration}s</span>
              <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{seg.status}</span>
            </div>
            <p style={{ fontSize: 15, lineHeight: 1.7, marginBottom: 12, color: 'var(--text-primary)' }}>
              "{seg.narration_text}"
            </p>
            <details style={{ cursor: 'pointer' }}>
              <summary style={{ fontSize: 13, color: 'var(--accent-purple)', fontWeight: 600 }}>View Prompts</summary>
              <div style={{ marginTop: 12, paddingLeft: 12, borderLeft: '2px solid var(--border-subtle)' }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4 }}>VISUAL PROMPT</p>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 12 }}>{seg.visual_prompt}</p>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4 }}>MOTION PROMPT</p>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{seg.motion_prompt}</p>
              </div>
            </details>
          </div>
        ))}
      </div>

      <button className="btn-primary" onClick={() => setStep(2)} style={{ width: '100%', padding: 16 }}>
        🎨 Continue to Image Generation →
      </button>
    </div>
  );
}
