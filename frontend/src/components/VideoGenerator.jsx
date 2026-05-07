import { useState, useEffect, useRef } from 'react';
import useProjectStore from '../store/projectStore';

export default function VideoGenerator() {
  const { currentProject, generateVideo, loading, setStep } = useProjectStore();
  const segments = currentProject?.segments || [];
  const [activeIdx, setActiveIdx] = useState(0);
  const [modelChoice, setModelChoice] = useState('hunyuan');
  const [countdown, setCountdown] = useState(null);
  const timerRef = useRef(null);

  const activeSeg = segments[activeIdx];
  const hasVideo = activeSeg?.assets?.some(a => a.asset_type === 'video' && a.selected);
  const allVideosDone = segments.every(s => s.assets?.some(a => a.asset_type === 'video' && a.selected));
  const isLoading = loading[`video_${activeSeg?.seg_index}`];

  // 30-second auto-timeout
  const startCountdown = () => {
    setCountdown(30);
    timerRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          // Auto-select random model
          const auto = Math.random() > 0.5 ? 'hunyuan' : 'svd';
          handleGenerate(auto);
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };

  useEffect(() => {
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  const handleGenerate = (model) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setCountdown(null);
    if (activeSeg) generateVideo(activeSeg.seg_index, model || modelChoice);
  };

  // Countdown ring SVG
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeOffset = countdown !== null ? circumference * (1 - countdown / 30) : circumference;

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 800 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
          <span style={{ color: 'var(--accent-cyan)', marginRight: 10 }}>03</span>
          Video Generation
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Choose a cloud video model for each segment. Auto-selects after 30 seconds.
        </p>
      </div>

      {/* Segment Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {segments.map((s, i) => {
          const done = s.assets?.some(a => a.asset_type === 'video' && a.selected);
          return (
            <button key={s.id} onClick={() => { setActiveIdx(i); if (timerRef.current) { clearInterval(timerRef.current); setCountdown(null); } }}
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
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Generating video via cloud API...</p>
              <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>This may take 1-3 minutes depending on the model</p>
            </div>
          ) : (
            <>
              {/* Model Selection */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
                {[
                  { id: 'hunyuan', name: 'HunyuanVideo', desc: 'Top-tier motion consistency, smooth transitions', badge: 'badge-purple' },
                  { id: 'svd', name: 'Stable Video Diffusion', desc: 'Cinematic camera pans, artistic style', badge: 'badge-cyan' },
                ].map(m => (
                  <div key={m.id}
                    className={`selection-card ${modelChoice === m.id ? 'selected' : ''}`}
                    onClick={() => setModelChoice(m.id)}
                    style={{ padding: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontWeight: 700, fontSize: 15 }}>{m.name}</span>
                      <span className={`badge ${m.badge}`}>HF API</span>
                    </div>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>{m.desc}</p>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <button className="btn-primary" onClick={() => handleGenerate()} style={{ flex: 1, padding: 16 }}>
                  🎥 Generate Video
                </button>
                {countdown === null && (
                  <button className="btn-secondary" onClick={startCountdown} style={{ padding: 16 }}>
                    ⏱ Start 30s Timer
                  </button>
                )}
                {countdown !== null && (
                  <div style={{ position: 'relative', width: 64, height: 64, flexShrink: 0 }}>
                    <svg width="64" height="64" className="countdown-ring">
                      <circle cx="32" cy="32" r={radius} fill="none" stroke="var(--border-subtle)" strokeWidth="3" />
                      <circle cx="32" cy="32" r={radius} fill="none" stroke="var(--accent-cyan)" strokeWidth="3"
                        strokeDasharray={circumference} strokeDashoffset={strokeOffset} strokeLinecap="round" />
                    </svg>
                    <span style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 16, color: 'var(--accent-cyan)' }}>
                      {countdown}
                    </span>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {activeSeg && hasVideo && (
        <div className="glass-card" style={{ padding: 24, textAlign: 'center' }}>
          <span className="badge badge-green" style={{ marginBottom: 12, display: 'inline-flex' }}>✓ Video Generated</span>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            Video for segment {activeIdx + 1} is ready.
          </p>
        </div>
      )}

      {allVideosDone && (
        <button className="btn-primary" onClick={() => setStep(4)} style={{ width: '100%', padding: 16, marginTop: 20 }}>
          🔊 Continue to Audio & Render →
        </button>
      )}
    </div>
  );
}
