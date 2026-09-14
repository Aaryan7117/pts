import { api } from './client.js';

export const documentsApi = {
  // Upload document for OCR & medical fact extraction
  upload: (encounterId, file, docType = 'prescription', docDate = null, patientId = null) => {
    const formData = new FormData();
    formData.append('encounter_id', encounterId);
    formData.append('document', file);
    formData.append('document_type', docType);
    if (docDate) formData.append('document_date', docDate);
    if (patientId) formData.append('patient_id', patientId);
    return api.upload('/api/documents/upload', formData);
  },

  // Get document timeline with line bounding boxes
  getEncounterTimeline: (encounterId) => 
    api.get(`/api/documents/encounter/${encounterId}/timeline`),
};
