/**
 * MediKiosk Web — Page 08: Patient Health Workspace & ABHA Locker
 */

import { store } from '../../store.js';
import { patientApi } from '../../api/patient.api.js';

export function renderPatientDashboard() {
  const user = store.getState().auth.user || {
    full_name: 'Ramesh Kumar',
    mobile: '9876543210',
    abha_id: '91-4821-3910-4819'
  };

  const patientState = store.getState().patient;
  const activeToken = patientState.activeToken || { token: 'A-261', patients_ahead: 2, estimated_wait_minutes: 12, doctor_room: 'Cabin 102 (Dr. S. Verma)' };

  return `
    <div class="workspace-shell">
      <!-- Left Sidebar Navigation -->
      <aside class="workspace-sidebar">
        <div>
          <div style="padding:var(--space-3) var(--space-4); margin-bottom:var(--space-4); display:flex; align-items:center; gap:10px;">
            <div style="width:36px; height:36px; border-radius:50%; background:#7E22CE; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700;">
              ${user.full_name ? user.full_name[0] : 'P'}
            </div>
            <div>
              <div style="font-size:14px; font-weight:700; color:var(--text-primary);">${user.full_name || 'Ramesh Kumar'}</div>
              <div style="font-size:11px; color:var(--text-muted); font-family:var(--font-family-mono);">${user.mobile || '9876543210'}</div>
            </div>
          </div>

          <ul class="workspace-nav-list">
            <li><a href="#/patient/dashboard" class="workspace-nav-link active">❖ <span>Dashboard</span></a></li>
            <li><a href="#/kiosk/welcome" class="workspace-nav-link">📋 <span>Start New Intake</span></a></li>
            <li><a href="#/patient/queue" class="workspace-nav-link">🎫 <span>Live Queue Token</span></a></li>
            <li><a href="#/doctor/queue" class="workspace-nav-link">🩺 <span>Doctor Workstation</span></a></li>
          </ul>
        </div>

        <div>
          <button class="btn btn-ghost btn-sm" style="width:100%; justify-content:flex-start;" onclick="window.patientLogout()">
            🚪 Sign Out
          </button>
        </div>
      </aside>

      <!-- Main Workspace Canvas -->
      <main class="workspace-main-content">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-6);">
          <div>
            <h1 class="text-h2">Citizen Health Workspace</h1>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
              Ayushman Bharat Digital Mission (ABDM) Personal Health Locker
            </p>
          </div>
          <button class="btn btn-primary btn-md" onclick="alert('Document upload dialog opened.')">
            + Upload Prescription / Report
          </button>
        </div>

        <!-- ABHA Health Card & Live Token Grid -->
        <div style="display:grid; grid-template-columns:1.2fr 1fr; gap:var(--space-6); margin-bottom:var(--space-6);">
          <!-- Card 1: Official ABHA Digital Health Card -->
          <div class="card" style="background:linear-gradient(135deg, #0F172A, #1E3A8A); color:#fff; border:none; padding:var(--space-6); position:relative; overflow:hidden;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-6);">
              <div>
                <div style="font-size:11px; text-transform:uppercase; color:#94a3b8; letter-spacing:0.06em;">Government of India · ABDM</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin-top:2px;">ABHA DIGITAL HEALTH CARD</div>
              </div>
              <span class="badge badge-teal" style="font-size:10px;">AIIA Verified</span>
            </div>

            <div style="font-size:24px; font-weight:800; letter-spacing:3px; font-family:var(--font-family-mono); color:#38BDF8; margin-bottom:var(--space-6);">
              ${user.abha_id || '91-4821-3910-4819'}
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-4);">
              <div>
                <span style="font-size:10px; text-transform:uppercase; color:#94a3b8;">Patient Name</span>
                <div style="font-size:15px; font-weight:700;">${user.full_name || 'Ramesh Kumar'}</div>
              </div>
              <div>
                <span style="font-size:10px; text-transform:uppercase; color:#94a3b8;">Linked Mobile</span>
                <div style="font-size:15px; font-weight:700; font-family:var(--font-family-mono);">${user.mobile || '9876543210'}</div>
              </div>
            </div>
          </div>

          <!-- Card 2: Live OPD Queue Ticket -->
          <div class="card" style="border-left:4px solid var(--brand-primary); display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-3);">
                <span style="font-size:12px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Live OPD Queue Token</span>
                <span class="badge badge-blue">In Queue</span>
              </div>
              <div style="font-size:38px; font-weight:800; color:var(--brand-primary); font-family:var(--font-family-mono);">
                ${activeToken.token || 'A-261'}
              </div>
              <div style="font-size:14px; font-weight:600; color:var(--text-primary); margin-top:4px;">
                ${activeToken.doctor_room || 'Cabin 102 (Dr. S. Verma)'}
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-subtle); padding-top:var(--space-3); margin-top:var(--space-4);">
              <span style="font-size:13px; color:var(--text-muted);">Patients Ahead: <strong>${activeToken.patients_ahead || 2}</strong></span>
              <span style="font-size:13px; color:var(--status-success); font-weight:700;">Wait: ~${activeToken.estimated_wait_minutes || 12} mins</span>
            </div>
          </div>
        </div>

        <!-- Doctor-Verified Records Section -->
        <div class="card" style="padding:0; overflow:hidden;">
          <div style="padding:var(--space-4) var(--space-6); background:var(--bg-surface-soft); border-bottom:1px solid var(--border-default); display:flex; justify-content:space-between; align-items:center;">
            <h3 class="text-h3" style="font-size:16px;">Doctor-Verified Medical Records & Consultations</h3>
            <span class="badge badge-green">1 Verified</span>
          </div>

          <div style="padding:var(--space-6);">
            <div style="border:1px solid var(--border-default); border-radius:var(--radius-lg); padding:var(--space-4); margin-bottom:var(--space-3); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="badge badge-teal">General Medicine OPD</span>
                  <span style="font-size:12px; color:var(--text-muted);">12-Sep-2026</span>
                </div>
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-top:4px;">
                  Clinical History Review & E-Prescription Reconciled
                </div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">
                  Consulting Physician: Dr. S. Verma (Cabin 102) · Notes: Metformin continued, low carb diet advised.
                </div>
              </div>

              <div style="text-align:right;">
                <button class="btn btn-secondary btn-sm" onclick="alert('Downloading signed prescription PDF...')">
                  📄 View PDF Slip
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  `;
}

export async function initPatientDashboard() {
  const user = store.getState().auth.user;
  const identifier = user ? (user.abha_id || user.mobile || user.id) : '9876543210';

  try {
    const data = await patientApi.getDashboard(identifier);
    store.setPatientDashboard(data);
  } catch (err) {
    console.warn('Patient dashboard API fetch fallback:', err);
  }
}
