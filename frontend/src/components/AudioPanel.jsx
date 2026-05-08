import { useState, useEffect } from 'react';
import useProjectStore from '../store/projectStore';

export default function AudioPanel() {
  const { currentProject, generateAudio, renderFinal, loading, error, fetchVoices, voices } = useProjectStore();
  const [voiceName, setVoiceName] = useState('female_warm');
  const [musicPrompt, setMusicPrompt] = useState('cinematic ambient atmospheric background music, emotional, soft');
  const [audioResult, setAudioResult] = useState(null);
  const [renderResult, setRenderResult] = useState(null);
  const [renderError, setRenderError] = useState(null);
  const [audioGenerated, setAudioGenerated] = useState(currentProject?.status === 'audio_ready' || currentProject?.status === 'complete');

  useEffect(() => { fetchVoices(); }, []);

  const handleGenerateAudio = async () => {
    const result = await generateAudio(voiceName, musicPrompt);
    if (result) {
      setAudioResult(result);
      setAudioGenerated(true);
    }
  };

  const handleRender = async () => {
    setRenderError(null);
    setRenderResult(null);
    try {
      const result = await renderFinal();
      if (result && result.success !== false) {
        setRenderResult(result);
      }
    } catch (e) {
      setRenderError(e.message || 'Render failed');
    }
  };

  const handleDownload = () => {
    if (!renderResult?.url) return;
    const a = document.createElement('a');
    a.href = renderResult.url;
    a.download = `autocinema_final_${currentProject?.id || 'video'}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const isAudioLoading = loading.audio;
  const isRendering = loading.render;
  const isComplete = renderResult?.success || currentProject?.status === 'complete';

  const voiceoverUrl = audioResult?.voiceover?.url || '';
  const musicUrl = audioResult?.music?.url || '';

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 720 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
          <span style={{ color: 'var(--accent-green)', marginRight: 10 }}>04</span>
          Audio & Final Render
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Generate cloud voiceover and background music, then render the final video.
        </p>
      </div>

      {/* Voice Selection */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>
          🎙️ Voice Selection
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 10 }}>
          {(voices.length > 0 ? voices : [
            { id: 'female_warm', name: 'Female Warm' },
            { id: 'female_professional', name: 'Female Professional' },
            { id: 'male_deep', name: 'Male Deep' },
            { id: 'male_news', name: 'Male News' },
            { id: 'female_friendly', name: 'Female Friendly' },
            { id: 'male_casual', name: 'Male Casual' },
          ]).map(v => (
            <button key={v.id} onClick={() => setVoiceName(v.id)}
              style={{
                padding: '12px 16px', borderRadius: 10, fontSize: 13, fontWeight: 600,
                border: voiceName === v.id ? '2px solid var(--accent-green)' : '1px solid var(--border-subtle)',
                background: voiceName === v.id ? 'rgba(34,197,94,0.1)' : 'var(--bg-card)',
                color: voiceName === v.id ? '#4ade80' : 'var(--text-secondary)',
                cursor: 'pointer', transition: 'all 0.2s', textAlign: 'left',
              }}>
              {v.name}
            </button>
          ))}
        </div>
        <p style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)' }}>
          Powered by Microsoft Edge Neural TTS — 100% free, cloud-based
        </p>
      </div>

      {/* Music Prompt */}
      <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>
          🎵 Background Music
        </h3>
        <textarea className="input-field" rows={3} value={musicPrompt} onChange={e => setMusicPrompt(e.target.value)}
          placeholder="Describe the mood of the background music..." />
        <p style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
          Powered by Pollinations.ai ElevenMusic — instrumental AI music
        </p>
      </div>

      {/* Generate Audio */}
      {!audioGenerated && (
        <button className="btn-primary" onClick={handleGenerateAudio} disabled={isAudioLoading}
          style={{ width: '100%', padding: 16, marginBottom: 16 }}>
          {isAudioLoading ? (
            <>
              <span className="animate-spin" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
              Generating voiceover & music...
            </>
          ) : '🔊 Generate Audio (Voice + Music)'}
        </button>
      )}

      {/* Audio Preview & Render */}
      {audioGenerated && (
        <>
          {/* Voiceover Preview */}
          <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <span style={{ fontSize: 20 }}>🎙️</span>
              <div>
                <p style={{ fontWeight: 600, fontSize: 14 }}>Voiceover</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{audioResult?.voiceover?.voice || 'Edge Neural TTS'}</p>
              </div>
              <span className="badge badge-green" style={{ marginLeft: 'auto' }}>✓ Ready</span>
            </div>
            {voiceoverUrl && (
              <audio controls style={{ width: '100%', borderRadius: 8, height: 40 }} src={voiceoverUrl} />
            )}
          </div>

          {/* Music Preview */}
          <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <span style={{ fontSize: 20 }}>🎵</span>
              <div>
                <p style={{ fontWeight: 600, fontSize: 14 }}>Background Music</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{audioResult?.music?.source || 'MusicGen'}</p>
              </div>
              <span className={`badge ${audioResult?.music?.success ? 'badge-green' : 'badge-yellow'}`} style={{ marginLeft: 'auto' }}>
                {audioResult?.music?.success ? '✓ Ready' : 'Skipped'}
              </span>
            </div>
            {audioResult?.music?.success && musicUrl ? (
              <audio controls style={{ width: '100%', borderRadius: 8, height: 40 }} src={musicUrl} />
            ) : (
              <p style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                {audioResult?.music?.error
                  ? `Music generation was skipped (${audioResult.music.error}). Voiceover will still work.`
                  : 'Music will be generated when you click Generate Audio.'}
              </p>
            )}
          </div>

          {/* Render / Download */}
          {isComplete ? (
            <div className="glass-card" style={{ padding: 32, textAlign: 'center', marginBottom: 16 }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                background: 'rgba(34,197,94,0.15)', display: 'flex',
                alignItems: 'center', justifyContent: 'center', fontSize: 28,
                margin: '0 auto 16px',
              }}>✅</div>
              <p style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>Render Complete!</p>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 16 }}>
                Your video is ready to download.
              </p>
              <button
                className="btn-primary"
                onClick={handleDownload}
                style={{ padding: '14px 32px', fontSize: 16 }}
              >
                ⬇️ Download Final Video (.mp4)
              </button>
            </div>
          ) : (
            <button className="btn-primary animate-pulse-glow" onClick={handleRender} disabled={isRendering}
              style={{ width: '100%', padding: 18, fontSize: 16 }}>
              {isRendering ? (
                <>
                  <span className="animate-spin" style={{ display: 'inline-block', width: 20, height: 20, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
                  Rendering Final Video...
                </>
              ) : '🚀 Render Final 1920×1080 MP4'}
            </button>
          )}

          {isRendering && (
            <div style={{ marginTop: 16 }}>
              <div className="progress-bar">
                <div className="progress-bar-fill" style={{ width: '60%' }} />
              </div>
              <p style={{ textAlign: 'center', marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
                FFmpeg is stitching clips, mixing audio, and burning subtitles...
              </p>
            </div>
          )}
        </>
      )}

      {/* Error display */}
      {(error || renderError) && (
        <div style={{ marginTop: 16, padding: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-sm)', color: '#fca5a5', fontSize: 14 }}>
          ⚠️ Render failed: {renderError || error}
        </div>
      )}
    </div>
  );
}
