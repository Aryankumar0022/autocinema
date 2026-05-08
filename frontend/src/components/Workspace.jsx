import { useEffect } from 'react';
import useProjectStore from '../store/projectStore';
import ScriptEditor from './ScriptEditor';
import SegmentViewer from './SegmentViewer';
import ImagePicker from './ImagePicker';
import VideoGenerator from './VideoGenerator';
import AudioPanel from './AudioPanel';

const STEPS = [
  { num: '01', label: 'Script', icon: '📝' },
  { num: '02', label: 'Images', icon: '🎨' },
  { num: '03', label: 'Video', icon: '🎥' },
  { num: '04', label: 'Audio & Render', icon: '🔊' },
  { num: '05', label: 'Complete', icon: '✅' },
];

export default function Workspace({ projectId, onBack }) {
  const { currentProject, loadProject, currentStep, setStep } = useProjectStore();

  useEffect(() => {
    loadProject(projectId);
  }, [projectId]);

  if (!currentProject) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="animate-spin" style={{ width: 32, height: 32, border: '3px solid var(--border-subtle)', borderTopColor: 'var(--accent-purple)', borderRadius: '50%' }} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 24px' }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 32 }}>
        <button className="btn-ghost" onClick={onBack} style={{ padding: '8px 14px' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
          Back
        </button>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.02em' }}>{currentProject.name}</h1>
          <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Project {currentProject.id}</p>
        </div>
      </div>

      {/* Step Indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 40, padding: '0 8px' }}>
        {STEPS.map((step, i) => (
          <div key={i} style={{ display: 'contents' }}>
            <button
              onClick={() => { if (i <= currentStep) setStep(i); }}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '10px 18px', borderRadius: 10,
                background: i === currentStep ? 'var(--bg-card-hover)' : 'transparent',
                border: i === currentStep ? '1px solid var(--border-hover)' : '1px solid transparent',
                cursor: i <= currentStep ? 'pointer' : 'default',
                opacity: i > currentStep ? 0.35 : 1,
                transition: 'all 0.3s',
                color: 'var(--text-primary)',
              }}>
              <span style={{ fontSize: 16 }}>{i < currentStep ? '✅' : step.icon}</span>
              <span style={{ fontSize: 13, fontWeight: i === currentStep ? 700 : 500, display: 'none' }} className="step-label">{step.label}</span>
              <span style={{ fontSize: 13, fontWeight: i === currentStep ? 700 : 500 }}>{step.label}</span>
            </button>
            {i < STEPS.length - 1 && (
              <div style={{ flex: 1, height: 2, background: i < currentStep ? 'var(--accent-purple)' : 'var(--border-subtle)', borderRadius: 1, minWidth: 16, transition: 'background 0.5s' }} />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div style={{ minHeight: '50vh' }}>
        {currentStep === 0 && (
          <div>
            <ScriptEditor />
            {currentProject.segments?.length > 0 && (
              <div style={{ marginTop: 32 }}>
                <SegmentViewer />
              </div>
            )}
          </div>
        )}
        {currentStep === 1 && <ImagePicker />}
        {currentStep === 2 && <VideoGenerator />}
        {currentStep === 3 && <AudioPanel />}
        {currentStep === 4 && (
          <div className="glass-card animate-fade-in-up" style={{ padding: 48, textAlign: 'center' }}>
            <div style={{ fontSize: 64, marginBottom: 20 }}>🎬</div>
            <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 12 }}>
              <span className="gradient-text">Video Complete!</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 15, marginBottom: 32, maxWidth: 480, margin: '0 auto 32px' }}>
              Your 1080×1920 vertical video is ready for Instagram Reels and TikTok.
            </p>
            {/* Video Preview */}
            <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'center' }}>
              <video
                controls
                style={{ maxWidth: 300, borderRadius: 12, border: '1px solid var(--border-subtle)' }}
                src={`/static/outputs/proj_${currentProject.id}_final.mp4`}
              />
            </div>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button
                className="btn-primary"
                onClick={async () => {
                  try {
                    const res = await fetch(`/static/outputs/proj_${currentProject.id}_final.mp4`);
                    if (!res.ok) throw new Error('File not found');
                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `proj_${currentProject.id}_final.mp4`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                  } catch (e) {
                    alert('Download failed: ' + e.message);
                  }
                }}
              >
                ⬇️ Download MP4
              </button>
              <button className="btn-secondary" onClick={onBack}>
                ← Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
