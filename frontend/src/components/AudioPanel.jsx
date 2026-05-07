import { useState, useEffect } from 'react';
import useProjectStore from '../store/projectStore';

export default function AudioPanel() {
  const { currentProject, generateAudio, renderFinal, loading, error, fetchVoices, voices } = useProjectStore();
  const [voiceName, setVoiceName] = useState('female_warm');
  const [musicPrompt, setMusicPrompt] = useState('cinematic ambient atmospheric background music, emotional, soft');
  const [audioGenerated, setAudioGenerated] = useState(currentProject?.status === 'audio_ready' || currentProject?.status === 'complete');

  useEffect(() => { fetchVoices(); }, []);

  const handleGenerateAudio = async () => {
    const result = await generateAudio(voiceName, musicPrompt);
    if (result) setAudioGenerated(true);
  };

  const handleRender = async () => {
    await renderFinal();
  };

  const isAudioLoading = loading.audio;
  const isRendering = loading.render;

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
          Powered by Meta MusicGen via Hugging Face — 100% free
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

      {/* Audio Ready → Render */}
      {audioGenerated && (
        <>
          <div className="glass-card" style={{ padding: 20, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 24 }}>✅</span>
            <div>
              <p style={{ fontWeight: 600, fontSize: 14 }}>Audio Generated Successfully</p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Voiceover and background music are ready</p>
            </div>
          </div>

          <button className="btn-primary animate-pulse-glow" onClick={handleRender} disabled={isRendering}
            style={{ width: '100%', padding: 18, fontSize: 16 }}>
            {isRendering ? (
              <>
                <span className="animate-spin" style={{ display: 'inline-block', width: 20, height: 20, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
                Rendering Final Video...
              </>
            ) : '🚀 Render Final 1080×1920 MP4'}
          </button>
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

      {error && (
        <div style={{ marginTop: 16, padding: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-sm)', color: '#fca5a5', fontSize: 14 }}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
