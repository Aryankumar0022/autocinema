/**
 * AutoCinema Project Store (Zustand)
 * Lightweight state management for the entire video production workflow.
 */

import { create } from 'zustand';

const API = '';

const useProjectStore = create((set, get) => ({
  // ── State ─────────────────────────────────────────
  projects: [],
  currentProject: null,
  currentStep: 0,  // 0=script, 1=images, 2=videos, 3=audio, 4=render
  loading: {},      // { analyzeScript: true, generateImages_0: true, ... }
  error: null,
  voices: [],

  // ── Helpers ───────────────────────────────────────
  setLoading: (key, val) => set(s => ({ loading: { ...s.loading, [key]: val } })),
  setError: (err) => set({ error: err }),
  clearError: () => set({ error: null }),
  setStep: (step) => set({ currentStep: step }),

  // ── Fetch Voices ──────────────────────────────────
  fetchVoices: async () => {
    try {
      const res = await fetch(`${API}/api/voices`);
      const data = await res.json();
      set({ voices: data });
    } catch (e) {
      console.error('Failed to fetch voices:', e);
    }
  },

  // ── Projects ──────────────────────────────────────
  fetchProjects: async () => {
    try {
      const res = await fetch(`${API}/api/projects`);
      const data = await res.json();
      set({ projects: data });
    } catch (e) {
      set({ error: 'Failed to fetch projects' });
    }
  },

  loadProject: async (id) => {
    try {
      const res = await fetch(`${API}/api/projects/${id}`);
      const data = await res.json();
      set({ currentProject: data, error: null });
      // Auto-detect step
      const segs = data.segments || [];
      if (data.status === 'complete') set({ currentStep: 5 });
      else if (data.status === 'audio_ready') set({ currentStep: 4 });
      else if (segs.some(s => s.status === 'video_ready')) set({ currentStep: 3 });
      else if (segs.some(s => s.status === 'images_ready' || s.status === 'image_selected')) set({ currentStep: 2 });
      else if (segs.length > 0) set({ currentStep: 1 });
      else set({ currentStep: 0 });
    } catch (e) {
      set({ error: 'Failed to load project' });
    }
  },

  createProject: async (name, script) => {
    try {
      const res = await fetch(`${API}/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, script }),
      });
      const data = await res.json();
      set(s => ({ projects: [data, ...s.projects], currentProject: data, currentStep: 0 }));
      return data;
    } catch (e) {
      set({ error: 'Failed to create project' });
      return null;
    }
  },

  updateProject: async (updates) => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      const data = await res.json();
      set({ currentProject: data });
    } catch (e) {
      set({ error: 'Failed to update project' });
    }
  },

  deleteProject: async (id) => {
    try {
      await fetch(`${API}/api/projects/${id}`, { method: 'DELETE' });
      set(s => ({
        projects: s.projects.filter(p => p.id !== id),
        currentProject: s.currentProject?.id === id ? null : s.currentProject,
      }));
    } catch (e) {
      set({ error: 'Failed to delete project' });
    }
  },

  // ── Script Analysis ───────────────────────────────
  analyzeScript: async () => {
    const { currentProject, setLoading } = get();
    if (!currentProject) return;
    setLoading('analyze', true);
    set({ error: null });
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}/analyze`, { method: 'POST' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed');
      }
      await get().loadProject(currentProject.id);
      set({ currentStep: 1 });
    } catch (e) {
      set({ error: e.message });
    } finally {
      setLoading('analyze', false);
    }
  },

  // ── Image Generation ──────────────────────────────
  generateImages: async (segIndex) => {
    const { currentProject, setLoading } = get();
    if (!currentProject) return;
    const key = `images_${segIndex}`;
    setLoading(key, true);
    set({ error: null });
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}/segments/${segIndex}/images`, { method: 'POST' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Image generation failed');
      }
      const data = await res.json();
      await get().loadProject(currentProject.id);
      return data;
    } catch (e) {
      set({ error: e.message });
    } finally {
      setLoading(key, false);
    }
  },

  selectImage: async (segIndex, assetId) => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      await fetch(`${API}/api/projects/${currentProject.id}/segments/${segIndex}/select-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_id: assetId }),
      });
      await get().loadProject(currentProject.id);
    } catch (e) {
      set({ error: 'Failed to select image' });
    }
  },

  // ── Video Generation ──────────────────────────────
  generateVideo: async (segIndex, modelChoice = 'hunyuan') => {
    const { currentProject, setLoading } = get();
    if (!currentProject) return;
    const key = `video_${segIndex}`;
    setLoading(key, true);
    set({ error: null });
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}/segments/${segIndex}/video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_choice: modelChoice }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Video generation failed');
      }
      await get().loadProject(currentProject.id);
    } catch (e) {
      set({ error: e.message });
    } finally {
      setLoading(key, false);
    }
  },

  // ── Audio Generation ──────────────────────────────
  generateAudio: async (voiceName = 'female_warm', musicPrompt = '') => {
    const { currentProject, setLoading } = get();
    if (!currentProject) return;
    setLoading('audio', true);
    set({ error: null });
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}/audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voice_name: voiceName,
          music_prompt: musicPrompt || 'cinematic ambient atmospheric background music, emotional, soft',
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Audio generation failed');
      }
      const data = await res.json();
      await get().loadProject(currentProject.id);
      set({ currentStep: 4 });
      return data;
    } catch (e) {
      set({ error: e.message });
    } finally {
      setLoading('audio', false);
    }
  },

  // ── Final Render ──────────────────────────────────
  renderFinal: async () => {
    const { currentProject, setLoading } = get();
    if (!currentProject) return;
    setLoading('render', true);
    set({ error: null });
    try {
      const res = await fetch(`${API}/api/projects/${currentProject.id}/render`, { method: 'POST' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Render failed');
      }
      const data = await res.json();
      await get().loadProject(currentProject.id);
      set({ currentStep: 5 });
      return data;
    } catch (e) {
      set({ error: e.message });
    } finally {
      setLoading('render', false);
    }
  },
}));

export default useProjectStore;
