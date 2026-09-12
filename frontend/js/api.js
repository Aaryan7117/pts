/**
 * MediKiosk — API Client
 * Fetch wrapper for all backend endpoints.
 */

const API_BASE = '';  // Vite proxies /api to FastAPI

async function request(url, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  } catch (err) {
    if (err.message === 'Failed to fetch') {
      throw new Error('Cannot reach server. Is the backend running?');
    }
    throw err;
  }
}

export const api = {
  // ── Health ──
  health: () => request('/api/health'),

  // ── Encounters ──
  bootstrap: (language = 'hi', channel = 'kiosk') =>
    request('/api/encounters/bootstrap', {
      method: 'POST',
      body: JSON.stringify({ language, device_channel: channel }),
    }),

  getEncounter: (encounterId) =>
    request(`/api/encounters/${encounterId}`),

  // ── Call Sessions (Voice & Text Intake) ──
  startCall: (encounterId, language = 'hi') =>
    request('/api/call/session/start', {
      method: 'POST',
      body: JSON.stringify({ encounter_id: encounterId, language }),
    }),

  audioTurn: async (sessionId, audioBlob) => {
    const form = new FormData();
    form.append('session_id', sessionId);
    form.append('audio_file', audioBlob, 'recording.webm');
    const res = await fetch('/api/call/audio-turn', { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  textTurn: async (sessionId, text) => {
    const form = new FormData();
    form.append('session_id', sessionId);
    form.append('text', text);
    const res = await fetch('/api/call/text-turn', { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  endCall: (sessionId) =>
    request('/api/call/session/end', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    }),

  // ── Documents (Prescription Scan) ──
  uploadDocument: async (encounterId, imageBlob) => {
    const form = new FormData();
    form.append('encounter_id', encounterId);
    form.append('document', imageBlob, 'prescription.jpg');
    const res = await fetch('/api/documents/upload', { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  // ── Queue ──
  queueStatus: (token) => request(`/api/queue/status/${token}`),

  // ── Doctor Dashboard ──
  doctorAuth: (pin) =>
    request('/api/doctor/auth', {
      method: 'POST',
      body: JSON.stringify({ pin }),
    }),

  doctorQueue: () => request('/api/doctor/queue'),

  patientDetail: (encounterId) =>
    request(`/api/doctor/patient/${encounterId}`),

  callNext: (encounterId) =>
    request(`/api/doctor/patient/${encounterId}/call-next`, { method: 'POST' }),
};
