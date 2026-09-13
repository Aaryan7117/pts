import { api } from './client.js';

export const authApi = {
  // Check system health
  getHealth: () => api.get('/api/health'),

  // Unified login for Patients & Doctors
  login: (identifier, password, role = 'auto') => 
    api.post('/api/auth/login', { identifier, password, role }),

  // Register new patient profile
  registerPatient: (patientData) => 
    api.post('/api/auth/patient/register', patientData),

  // Hospital directory (OPD doctors & room numbers)
  getDirectory: () => 
    api.get('/api/auth/directory'),
};
