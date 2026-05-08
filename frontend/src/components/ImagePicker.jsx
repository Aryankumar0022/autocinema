import { useState } from 'react';
import useProjectStore from '../store/projectStore';

export default function ImagePicker() {
  const { currentProject, generateImages, generateAllImages, selectImage, loading, setStep } = useProjectStore();
  const segments = currentProject?.segments || [];
  const [activeSegIdx, setActiveSegIdx] = useState(0);

  const activeSeg = segments[activeSegIdx];
  const imageAssets = activeSeg?.assets?.filter(a => a.asset_type === 'image') || [];
  const hasSelected = imageAssets.some(a => a.selected);
  const allSegsDone = segments.every(s => {
    const imgs = s.assets?.filter(a => a.asset_type === 'image') || [];
    return imgs.some(a => a.selected);
  });

  const anyPending = segments.some(s => (s.assets?.filter(a => a.asset_type === 'image') || []).length === 0);

  const handleGenerate = () => {
    if (activeSeg) generateImages(activeSeg.seg_index);
  };

  const handleSelect = (assetId) => {
    if (activeSeg) selectImage(activeSeg.seg_index, assetId);
  };

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: 900 }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
            <span style={{ color: 'var(--accent-pink)', marginRight: 10 }}>02</span>
            Image Generation
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            For each segment, 2 random cloud models generate 1 image each. Pick your favorite.
          </p>
        </div>
        {anyPending && (
          <button 
            className="btn-primary" 
            onClick={generateAllImages}
            style={{ padding: '10px 20px', fontSize: 13, background: 'var(--gradient-purple)' }}
          >
            ✨ Generate All Images
          </button>
        )}
      </div>

      {/* Segment Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {segments.map((s, i) => {
          const imgs = s.assets?.filter(a => a.asset_type === 'image') || [];
          const done = imgs.some(a => a.selected);
          return (
            <button key={s.id} onClick={() => setActiveSegIdx(i)}
              style={{
                padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 600,
                border: i === activeSegIdx ? '2px solid var(--accent-purple)' : '1px solid var(--border-subtle)',
                background: done ? 'rgba(34,197,94,0.1)' : i === activeSegIdx ? 'var(--bg-card-hover)' : 'var(--bg-card)',
                color: done ? '#4ade80' : i === activeSegIdx ? 'var(--text-primary)' : 'var(--text-muted)',
                cursor: 'pointer', transition: 'all 0.2s',
                display: 'flex', alignItems: 'center', gap: 6
              }}>
              Seg {i + 1} 
              {loading[`images_${s.seg_index}`] ? (
                <span className="animate-spin" style={{ width: 12, height: 12, border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%' }} />
              ) : done ? '✓' : ''}
            </button>
          );
        })}
      </div>

      {/* Active Segment */}
      {activeSeg && (
        <div className="glass-card" style={{ padding: 24 }}>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>
            "{activeSeg.narration_text}"
          </p>

          {imageAssets.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <button className="btn-primary" onClick={handleGenerate}
                disabled={loading[`images_${activeSeg.seg_index}`]}
                style={{ padding: '14px 36px' }}>
                {loading[`images_${activeSeg.seg_index}`] ? (
                  <>
                    <span className="animate-spin" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%' }} />
                    Generating images...
                  </>
                ) : '🎨 Generate 2 Image Options'}
              </button>
              <p style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)' }}>
                Two random models will be selected from FLUX / FLUX Realism / Turbo
              </p>
            </div>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                {imageAssets.map((asset) => (
                  <div key={asset.id}
                    className={`selection-card ${asset.selected ? 'selected' : ''}`}
                    onClick={() => handleSelect(asset.id)}>
                    <div style={{ aspectRatio: '1/1', background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                      {asset.url ? (
                        <img src={asset.url} alt={asset.model_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      ) : (
                        <div className="shimmer-loading" style={{ width: '100%', height: '100%' }} />
                      )}
                    </div>
                    <div style={{ padding: 12 }}>
                      <p style={{ fontSize: 12, fontWeight: 600, color: asset.selected ? 'var(--accent-purple)' : 'var(--text-secondary)' }}>
                        {asset.model_name || 'Cloud Model'}
                      </p>
                      {Boolean(asset.selected) && <span className="badge badge-purple" style={{ marginTop: 6 }}>✓ Selected</span>}
                    </div>
                  </div>
                ))}
              </div>
              {!hasSelected && (
                <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>Click an image to select it</p>
              )}
            </>
          )}
        </div>
      )}

      {/* Next Step */}
      {allSegsDone && (
        <button className="btn-primary" onClick={() => setStep(2)} style={{ width: '100%', padding: 16, marginTop: 20 }}>
          🎥 Continue to Video Generation →
        </button>
      )}
    </div>
  );
}
