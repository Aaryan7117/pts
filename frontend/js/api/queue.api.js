import { api } from './client.js';

export const queueApi = {
  // Get live queue status for a patient token
  getStatus: (token) => 
    api.get(`/api/queue/status/${encodeURIComponent(token)}`),

  // Get all queue tokens (for overview displays)
  getAll: () => 
    api.get('/api/queue/all'),
};
