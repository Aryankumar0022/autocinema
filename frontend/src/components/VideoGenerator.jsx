import { useState, useEffect, useRef } from 'react';
import useProjectStore from '../store/projectStore';

export default function VideoGenerator() {
  const { currentProject, generateVideo, loading, setStep, error } = useProjectStore();
  const segments = currentProject?.segments || [];
  const [activeIdx, setActiveIdx] = useState(0);
  const [modelChoice, setModelChoice] = useState('zoom_in');

  const activeSeg = segments[activeIdx];
  const hasVideo = activeSeg?.assets?.some(a => a.asset_type === 'video' && a.selected);
  const allVideosDone = segments.every(s => s.assets?.some(a => a.asset_type === 'video' && a.selected));
  const isLoading = loading[`video_${activeSeg?.seg_index}`];

  const handleGenerate = (model) => {
    if (activeSeg) generateVideo(activeSeg.seg_index, model || modelChoice);
  };

  const KENBURNS_MODELS = [
    { id: 'zoom_in', name: 'Cinematic Zoom In', desc: 'Slow zoom into center — dramatic focus pull', icon: '🔍', badge: 'badge-purple' },
    { id: 'zoom_out', name: 'Epic Zoom Out', desc: 'Starts zoomed, slowly reveals the full frame', icon: '🌐', badge: 'badge-cyan' },
    { id: 'pan_left', name: 'Smooth Pan Left', desc: 'Gentle horizontal camera pan from right to left', icon: '👈', badge: 'badge-green' },
    { id: 'pan_up', name: 'Vertical Pan Up', desc: 'Slow upward camera tilt — revealing the scene', icon: '⬆️', badge: 'badge-purple' },
  ];

  const CLOUD_MODELS = [
    { id: 'seedance', name: 'Seedance', desc: 'AI-generated motion — requires Pollinations credits', icon: '🤖', badge: 'badge-cyan' },
    { id: 'wan-fast', name: 'Wan Fast', desc: 'Fast AI video — requires Pollinations credits', icon: '⚡', badge: 'badge-cyan' },
  ];

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 800 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
          <span style={{ color: 'var(--accent-cyan)', marginRight: 10 }}>03</span>
          Video Generation
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Choose a camera animation style for each segment. Ken Burns effects are instant & free via FFmpeg.
        </p>
      </div>

      {/* Segment Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {segments.map((s, i) => {
          const done = s.assets?.some(a => a.asset_type === 'video' && a.selected);
          return (
            <button key={s.id} onClick={() => setActiveIdx(i)}
              style={{
                padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 600,
                border: i === activeIdx ? '2px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                background: done ? 'rgba(34,197,94,0.1)' : 'var(--bg-card)',
                color: done ? '#4ade80' : 'var(--text-muted)',
                cursor: 'pointer', transition: 'all 0.2s',
              }}>
              Seg {i + 1} {done && '✓'}
            </button>
          );
        })}
      </div>

      {activeSeg && !hasVideo && (
        <div className="glass-card" style={{ padding: 32 }}>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 24 }}>
            "{activeSeg.narration_text}"
          </p>

          {isLoading ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div className="animate-spin" style={{ width: 40, height: 40, border: '3px solid var(--border-subtle)', borderTopColor: 'var(--accent-cyan)', borderRadius: '50%', margin: '0 auto 16px' }} />
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Generating video clip...</p>
              <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>Ken Burns effects take ~10 seconds via local FFmpeg</p>
            </div>
          ) : (
            <>
              {/* Ken Burns Presets */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>🎬 Camera Effects</span>
                  <span className="badge badge-green">Free & Instant</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  {KENBURNS_MODELS.map(m => (
                    <div key={m.id}
                      className={`selection-card ${modelChoice === m.id ? 'selected' : ''}`}
                      onClick={() => setModelChoice(m.id)}
                      style={{ padding: 16, cursor: 'pointer' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontWeight: 700, fontSize: 14 }}>{m.icon} {m.name}</span>
                      </div>
                      <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>{m.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Cloud Models (optional) */}
              <details style={{ marginBottom: 20 }}>
                <summary style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-muted)', cursor: 'pointer', marginBottom: 12 }}>
                  ☁️ Cloud AI Models (requires Pollinations credits)
                </summary>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
                  {CLOUD_MODELS.map(m => (
                    <div key={m.id}
                      className={`selection-card ${modelChoice === m.id ? 'selected' : ''}`}
                      onClick={() => setModelChoice(m.id)}
                      style={{ padding: 16, cursor: 'pointer', opacity: 0.7 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontWeight: 700, fontSize: 14 }}>{m.icon} {m.name}</span>
                        <span className="badge badge-cyan" style={{ fontSize: 10 }}>Paid</span>
                      </div>
                      <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.4 }}>{m.desc}</p>
                    </div>
                  ))}
                </div>
              </details>

              <button className="btn-primary" onClick={() => handleGenerate()} style={{ width: '100%', padding: 16 }}>
                🎥 Generate Video
              </button>
            </>
          )}

          {error && (
            <div style={{ marginTop: 16, padding: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-sm)', color: '#fca5a5', fontSize: 14 }}>
              ⚠️ {error}
            </div>
          )}
        </div>
      )}

      {activeSeg && hasVideo && (() => {
        const videoAsset = activeSeg.assets?.find(a => a.asset_type === 'video' && a.selected);
        const videoUrl = videoAsset?.url || '';
        return (
          <div className="glass-card" style={{ padding: 24, textAlign: 'center' }}>
            <span className="badge badge-green" style={{ marginBottom: 16, display: 'inline-flex' }}>✓ Video Generated</span>
            {videoUrl && (
              <div style={{ margin: '16px auto', maxWidth: 320, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
                <video
                  src={videoUrl}
                  controls
                  loop
                  muted
                  autoPlay
                  playsInline
                  style={{ width: '100%', display: 'block', aspectRatio: '16/9', objectFit: 'cover', background: '#000' }}
                />
              </div>
            )}
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>
              {videoAsset?.model_name || 'Video'} — Segment {activeIdx + 1}
            </p>
          </div>
        );
      })()}

      {allVideosDone && (
        <button className="btn-primary" onClick={() => setStep(3)} style={{ width: '100%', padding: 16, marginTop: 20 }}>
          🔊 Continue to Audio & Render →
        </button>
      )}
    </div>
  );
}
