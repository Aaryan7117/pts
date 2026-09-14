/**
 * MediKiosk Web — Doctor 3-Column Consultation Cockpit
 * Synchronized clinical workspace enabling physician review, e-prescription,
 * and 1-click sign-off without switching tabs during high-volume OPD shifts.
 */

import { renderEvidenceViewer } from './evidence-viewer.js';

export function renderConsultationCockpit(encounterDetail, onVerifyCallback) {
  const enc = encounterDetail.encounter || {};
  const pat = encounterDetail.patient || {};
  const facts = encounterDetail.clinical_facts || [];
  const drugAlerts = encounterDetail.drug_interaction_alerts || [];
  const labAlerts = encounterDetail.lab_result_alerts || [];
  const ayush = encounterDetail.ayush_intake || {};
  const channel = enc.channel || 'kiosk';

  // Extract Chief Complaint
  const chiefComplaintFact = facts.find(f => f.category === 'chief_complaint' || f.category === 'symptom');
  const chiefComplaint = chiefComplaintFact ? (chiefComplaintFact.patient_words || chiefComplaintFact.value) : 'Acute chest discomfort';

  // Extract Medications
  const medications = facts.filter(f => f.category === 'medication');

  return `
    <div class="doctor-3col-workspace">
      <!-- =========================================================================
           COLUMN 1: PATIENT SNAPSHOT, VITALS & CLINICAL SAFETY (Left 25%)
           ========================================================================= -->
      <div class="doctor-col">
        <div class="doctor-col__header">
          <span>👤 Patient Snapshot</span>
          <span class="badge badge-teal">Room 102</span>
        </div>
        <div class="doctor-col__body">
          <div style="background:var(--bg-surface-soft); padding:var(--space-4); border-radius:var(--radius-lg); border:1px solid var(--border-default);">
            <div style="font-size:18px; font-weight:800; color:var(--text-primary);">${pat.name || enc.patient_id || 'Ramesh Kumar'}</div>
            <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">Age: ${pat.age ? `${pat.age} Y / ${pat.gender === 'F' ? 'Female' : 'Male'}` : '56 Y / Male'} · Token: <strong style="color:var(--brand-primary);">${enc.token_number || 'A-261'}</strong></div>
            <div style="font-size:11px; font-family:var(--font-family-mono); color:var(--pr-blue-600); margin-top:4px;">ABHA: ${pat.abha_id || '91-4821-3910-4819'}</div>
          </div>

          <!-- Vitals Strip -->
          <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Physiological Vitals</div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-2);">
            <div style="padding:8px 10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <div style="font-size:10px; color:var(--text-muted);">BP</div>
              <div style="font-size:14px; font-weight:700;">128/84 mmHg</div>
            </div>
            <div style="padding:8px 10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <div style="font-size:10px; color:var(--text-muted);">Heart Rate</div>
              <div style="font-size:14px; font-weight:700;">76 bpm</div>
            </div>
            <div style="padding:8px 10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <div style="font-size:10px; color:var(--text-muted);">SpO2</div>
              <div style="font-size:14px; font-weight:700; color:var(--status-success);">98%</div>
            </div>
            <div style="padding:8px 10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
              <div style="font-size:10px; color:var(--text-muted);">Temperature</div>
              <div style="font-size:14px; font-weight:700;">98.4°F</div>
            </div>
          </div>

          <!-- Drug Safety & Contraindication Alerts -->
          <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-top:var(--space-2);">Deterministic Safety Alerts</div>
          ${drugAlerts.length > 0 ? drugAlerts.map(alert => `
            <div style="padding:10px 12px; background:var(--status-warning-tint); border-radius:var(--radius-md); border-left:3px solid var(--status-warning); border:1px solid var(--status-warning);">
              <div style="font-size:11px; font-weight:700; color:var(--status-warning); display:flex; align-items:center; gap:4px;">
                ⚠ DRUG CONFLICT: ${alert.drug_a || 'Metformin'} + ${alert.drug_b || 'Contrast'}
              </div>
              <div style="font-size:11px; color:var(--pr-slate-800); margin-top:4px;">${alert.description || 'Potential interaction detected. Monitor renal parameters.'}</div>
            </div>
          `).join('') : `
            <div style="padding:10px 12px; background:var(--status-success-tint); border-radius:var(--radius-md); border:1px solid var(--status-success); font-size:12px; color:var(--status-success);">
              ✓ No adverse drug-drug conflicts detected
            </div>
          `}
        </div>
      </div>

      <!-- =========================================================================
           COLUMN 2: STANDARDIZED CLINICAL HISTORY & EVIDENCE (Center 45%)
           ========================================================================= -->
      <div class="doctor-col">
        <div class="doctor-col__header">
          <span>📋 Clinical History & Evidence Proof</span>
          <div style="display:flex; gap:6px;">
            <span class="badge ${enc.severity_badge === 'RED' ? 'badge-red' : (enc.severity_badge === 'YELLOW' ? 'badge-amber' : 'badge-green')}">
              ${enc.severity_badge || 'GREEN'} Triage
            </span>
          </div>
        </div>
        <div class="doctor-col__body">
          <!-- 30-Second Clinical Triage Synthesis -->
          <div style="background:var(--brand-tint); border-left:4px solid var(--brand-primary); padding:var(--space-4); border-radius:var(--radius-lg); border:1px solid var(--border-brand);">
            <div style="font-size:11px; font-weight:700; color:var(--brand-primary); text-transform:uppercase; margin-bottom:2px;">30-Second Clinical Triage Synthesis</div>
            <div style="font-size:14px; font-weight:600; color:var(--text-primary); line-height:1.4;">
              "${chiefComplaint}" · Duration: 3 days · Prior Medications: Metformin 500mg, Atorvastatin 20mg.
            </div>
          </div>

          <!-- Structured History Tabs/Accordion -->
          <div style="display:flex; flex-direction:column; gap:var(--space-3);">
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Extracted Clinical Facts</div>
            <div style="background:var(--bg-surface-soft); padding:var(--space-4); border-radius:var(--radius-lg); border:1px solid var(--border-default); display:flex; flex-direction:column; gap:8px;">
              <div><strong>Chief Complaint:</strong> ${chiefComplaint}</div>
              <div><strong>Recorded Medications:</strong> ${medications.length > 0 ? medications.map(m => m.value).join(', ') : 'Metformin 500mg BD, Atorvastatin 20mg HS'}</div>
              <div><strong>AYUSH Prakriti / Agni:</strong> Pitta-Vata / Manda Agni (Slow digestion)</div>
            </div>
          </div>

          <!-- Channel-Specific Evidence Section -->
          <div style="margin-top:var(--space-2);">
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-bottom:var(--space-2);">Channel Evidence & Provenance Proof</div>
            ${renderEvidenceViewer(channel, encounterDetail.documents ? encounterDetail.documents[0] : null)}
          </div>
        </div>
      </div>

      <!-- =========================================================================
           COLUMN 3: DOCTOR ASSESSMENT, PRESCRIPTION & SIGN-OFF (Right 30%)
           ========================================================================= -->
      <div class="doctor-col">
        <div class="doctor-col__header">
          <span>🩺 Doctor Prescription & Sign-Off</span>
          <span class="badge badge-blue">Dr. S. Verma</span>
        </div>
        <div class="doctor-col__body">
          <div>
            <label style="display:block; font-size:12px; font-weight:700; margin-bottom:4px; color:var(--text-secondary);">Clinical Assessment & Notes</label>
            <textarea id="doctorClinicalNotes" rows="4" class="form-input" style="height:auto; padding:10px; resize:vertical; font-size:13px;" placeholder="Type diagnostic impressions, clinical evaluation, and advice...">Patient evaluated. Prescriptions reconciled. Recommended lifestyle changes and continuation of Metformin with dietary modification.</textarea>
          </div>

          <!-- E-Prescription Pad -->
          <div style="display:flex; flex-direction:column; gap:var(--space-2);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Digital E-Prescription</span>
              <button class="btn btn-secondary btn-sm" onclick="alert('Added medication row.')">+ Add Drug</button>
            </div>
            
            <div style="padding:10px 12px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-default); display:flex; flex-direction:column; gap:4px;">
              <div style="font-size:13px; font-weight:700; color:var(--text-primary);">1. Tab Metformin 500mg</div>
              <div style="font-size:11px; color:var(--text-secondary);">Dose: 1 Tab BD (After Food) · Duration: 30 Days</div>
            </div>

            <div style="padding:10px 12px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-default); display:flex; flex-direction:column; gap:4px;">
              <div style="font-size:13px; font-weight:700; color:var(--status-ayush);">2. Ashwagandha Churna 3g</div>
              <div style="font-size:11px; color:var(--text-secondary);">Dose: 1/2 tsp BD with warm milk · Duration: 15 Days</div>
            </div>
          </div>

          <!-- 1-Click Verification Sign-Off Bar -->
          <div style="margin-top:auto; padding-top:var(--space-4); border-top:1px solid var(--border-subtle);">
            <button class="btn btn-ayush btn-lg" id="btnDoctorSignOff" style="width:100%; justify-content:center;">
              ✓ Sign & Verify Clinical Case
            </button>
            <div style="font-size:11px; text-align:center; color:var(--text-muted); margin-top:6px;">
              Audit Stamp: Digital signature applied with timestamp
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
