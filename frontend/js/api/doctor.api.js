import { api } from './client.js';

export const doctorApi = {
  // PIN authentication (PIN: 1234)
  auth: (pin) => 
    api.post('/api/doctor/auth', { pin }),

  // Get active OPD doctor triage queue
  getQueue: () => 
    api.get('/api/doctor/queue'),

  // Get full clinical patient details
  getPatientDetail: (encounterId) => 
    api.get(`/api/doctor/patient/${encounterId}`),

  // Longitudinal patient timeline by ABHA
  getPatientByAbha: (abhaId) => 
    api.get(`/api/doctor/patient/by-abha/${encodeURIComponent(abhaId)}`),

  // Call next patient into doctor chamber
  callNextPatient: (encounterId) => 
    api.post(`/api/doctor/patient/${encounterId}/call-next`, {}),

  // Sign off & verify clinical encounter
  verifyEncounter: (encounterId, doctorId = 'doc-verma', notes = 'Clinical history verified.') => 
    api.post(`/api/doctor/encounter/${encounterId}/verify?doctor_id=${encodeURIComponent(doctorId)}&notes=${encodeURIComponent(notes)}`, {})
};
