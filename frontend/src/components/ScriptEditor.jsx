import { useState } from 'react';
import useProjectStore from '../store/projectStore';

export default function ScriptEditor() {
  const { currentProject, updateProject, analyzeScript, loading, error } = useProjectStore();
  const [script, setScript] = useState(currentProject?.script || '');
  const isAnalyzing = loading.analyze;

  const handleAnalyze = async () => {
    if (!script.trim()) return;
    if (script !== currentProject?.script) {
      await updateProject({ script });
    }
    await analyzeScript();
  };

  const wordCount = script.trim().split(/\s+/).filter(Boolean).length;
  const estDuration = Math.ceil(wordCount / 2.5);

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 720 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
          <span style={{ color: 'var(--accent-purple)', marginRight: 10 }}>01</span>
          Script & Narration
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6 }}>
          Paste your narration text below. Gemini 1.5 Flash will analyze it, split it into vertical-friendly segments, 
          and generate cinematic image prompts for each segment.
        </p>
      </div>

      <textarea
        className="input-field"
        rows={10}
        placeholder="In a world where ancient forests hold secrets older than time itself, a lone explorer discovers a gateway to dimensions unknown. The trees whisper forgotten languages as golden light filters through the emerald canopy..."
        value={script}
        onChange={e => setScript(e.target.value)}
        style={{ marginBottom: 16, lineHeight: 1.8, fontSize: 15 }}
      />

      {/* Stats Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Words</span>
          <span className="badge badge-purple">{wordCount}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Est. Duration</span>
          <span className="badge badge-cyan">{estDuration}s</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Segments</span>
          <span className="badge badge-green">~{Math.max(1, Math.ceil(estDuration / 5))}</span>
        </div>
      </div>

      {error && (
        <div style={{ padding: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-sm)', marginBottom: 16, color: '#fca5a5', fontSize: 14 }}>
          ⚠️ {error}
        </div>
      )}

      <button className="btn-primary" onClick={handleAnalyze} disabled={!script.trim() || isAnalyzing} style={{ width: '100%', padding: 16 }}>
        {isAnalyzing ? (
          <>
            <span className="animate-spin" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
            Analyzing with Gemini 1.5 Flash...
          </>
        ) : (
          <>✨ Analyze Script & Generate Prompts</>
        )}
      </button>
    </div>
  );
}
