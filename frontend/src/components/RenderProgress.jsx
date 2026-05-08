/**
 * RenderProgress — Final render step with progress animation and download.
 */

import { useState } from 'react';
import useProjectStore from '../store/projectStore';

export default function RenderProgress() {
  const { currentProject, loading, error, renderFinal } = useProjectStore();
  const [renderResult, setRenderResult] = useState(null);

  const isRendering = loading.render;
  const isComplete = currentProject?.status === 'complete';

  const handleRender = async () => {
    const result = await renderFinal();
    if (result) setRenderResult(result);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
          🎬 Final Render
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Combine all segments, voiceover, music, and subtitles into the final video.
        </p>
      </div>

      {/* Status Card */}
      <div className="glass-card" style={{ padding: 32, textAlign: 'center' }}>
        {isRendering ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
            {/* Animated Ring */}
            <div style={{
              width: 80, height: 80, borderRadius: '50%',
              border: '3px solid var(--border-subtle)',
              borderTopColor: 'var(--accent-purple)',
              animation: 'spin 1s linear infinite',
            }} />
            <div>
              <p style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Rendering your video…</p>
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                FFmpeg is stitching clips, mixing audio, and burning subtitles
              </p>
            </div>
            {/* Shimmer bar */}
            <div style={{ width: '100%', maxWidth: 400 }}>
              <div className="progress-bar">
                <div className="progress-bar-fill shimmer-loading" style={{ width: '70%' }} />
              </div>
            </div>
          </div>
        ) : isComplete || renderResult?.success ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 64, height: 64, borderRadius: '50%',
              background: 'rgba(34,197,94,0.15)', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: 28,
            }}>✅</div>
            <p style={{ fontSize: 18, fontWeight: 700 }}>Render Complete!</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              Your video is ready to download.
            </p>
            {renderResult?.url && (
              <button
                className="btn-primary"
                onClick={() => {
                  const a = document.createElement('a');
                  a.href = renderResult.url;
                  a.download = 'autocinema_final.mp4';
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}
                style={{ marginTop: 8 }}
              >
                ⬇️ Download Video
              </button>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 64, height: 64, borderRadius: '50%',
              background: 'var(--gradient-card)', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: 28,
            }}>🎞️</div>
            <p style={{ fontSize: 16, fontWeight: 600 }}>Ready to render</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, maxWidth: 360 }}>
              This will combine all video segments with voiceover, background music,
              and word-level subtitles into a single video.
            </p>
            <button
              className="btn-primary"
              onClick={handleRender}
              disabled={isRendering}
              style={{ marginTop: 8 }}
            >
              🚀 Start Final Render
            </button>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '12px 16px', borderRadius: 'var(--radius-sm)',
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
          color: '#f87171', fontSize: 13,
        }}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
