/**
 * MediKiosk Web — Page 32: Doctor Live OPD Waiting Queue & Clinical Triaging Table
 * Single Pane of Glass: All 3 channels (Kiosk, BYOD, IVR) converge here.
 */

import { store } from '../../store.js';
import { doctorApi } from '../../api/doctor.api.js';

let pollTimer = null;

export function renderDoctorQueue() {
  const queue = store.getState().doctor.queue || [];
  const total = queue.length;
  const redCount = queue.filter(q => q.severity_badge === 'RED').length;

  return `
    <div style="max-width:1400px; margin:0 auto; padding:var(--space-8) var(--space-6);">
      <!-- Top Metrics Strip -->
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-6);">
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <h1 class="text-h2">Clinical Command Center</h1>
            <span class="badge badge-teal">Room 102 · General Medicine</span>
          </div>
          <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
            Single Pane of Glass where In-Clinic Kiosk, Mobile BYOD, and 2G IVR encounters converge.
          </p>
        </div>

        <div style="display:flex; gap:var(--space-3);">
          <button id="btnRefreshDoctorQueue" class="btn btn-secondary btn-md">
            🔄 Refresh Queue
          </button>
          <a href="#/kiosk/welcome" target="_blank" class="btn btn-primary btn-md" style="text-decoration:none;">
            + Open Kiosk Window 1 ↗
          </a>
        </div>
      </div>

      <!-- Stat Cards Strip -->
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:var(--space-4); margin-bottom:var(--space-6);">
        <div class="card card-sm">
          <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Waiting Patients</div>
          <div style="font-size:32px; font-weight:800; color:var(--brand-primary); margin-top:4px;" id="doctorQueueCount">${total}</div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Active in OPD Queue</div>
        </div>

        <div class="card card-sm" style="border-left:4px solid var(--status-danger);">
          <div style="font-size:11px; font-weight:700; color:var(--status-danger); text-transform:uppercase;">Critical / Red Flag</div>
          <div style="font-size:32px; font-weight:800; color:var(--status-danger); margin-top:4px;" id="doctorCriticalCount">${redCount}</div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Immediate attention required</div>
        </div>

        <div class="card card-sm">
          <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Average Consult Time</div>
          <div style="font-size:32px; font-weight:800; color:var(--status-success); margin-top:4px;">5.2 m</div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Target: 2-5 mins OPD</div>
        </div>

        <div class="card card-sm">
          <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Active Physician</div>
          <div style="font-size:20px; font-weight:800; color:var(--text-primary); margin-top:8px;">Dr. S. Verma</div>
          <div style="font-size:12px; color:var(--status-ayush); margin-top:2px;">MD (Internal Medicine)</div>
        </div>
      </div>

      <!-- Live Waiting Queue Table -->
      <div class="card" style="padding:0; overflow:hidden;">
        <div style="padding:var(--space-4) var(--space-6); background:var(--bg-surface-soft); border-bottom:1px solid var(--border-default); display:flex; justify-content:space-between; align-items:center;">
          <h3 class="text-h3" style="font-size:16px;">Active Patient Queue & Triage Synthesis</h3>
          <span style="font-size:12px; color:var(--text-muted);">Real-time SQLite WAL Sync</span>
        </div>

        <div class="clinical-table-container" style="border:none; box-shadow:none;">
          <table class="clinical-table">
            <thead>
              <tr>
                <th style="width:90px;">Token</th>
                <th style="width:140px;">Channel</th>
                <th style="width:110px;">Priority</th>
                <th>30-Second Clinical Triage Synthesis</th>
                <th style="width:90px;">Documents</th>
                <th style="width:140px; text-align:right;">Action</th>
              </tr>
            </thead>
            <tbody id="doctorQueueTableBody">
              ${_renderRows(queue)}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function _renderRows(queue) {
  if (!queue || queue.length === 0) {
    return `
      <tr>
        <td colspan="6" style="text-align:center; padding:var(--space-8); color:var(--text-muted);">
          No patients currently waiting in queue. Use Window 1 to intake a patient.
        </td>
      </tr>
    `;
  }

  const langLabels = {
    'hi': 'हिन्दी',
    'en': 'English',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'mr': 'मराठी'
  };

  return queue.map(entry => {
    const channelBadge = entry.channel === 'ivr_phone'
      ? '<span class="badge badge-amber">📞 Citizen IVR</span>'
      : entry.channel === 'android_byod'
      ? '<span class="badge badge-purple">📱 BYOD</span>'
      : '<span class="badge badge-teal">🏥 Kiosk</span>';

    const langName = langLabels[entry.language] || entry.language || 'हिन्दी';
    const langBadge = `<span class="badge badge-purple" style="font-size:11px;" title="Patient Language: ${langName}">🗣 ${langName}</span>`;

    const severityBadge = entry.severity_badge === 'RED'
      ? '<span class="badge badge-red">🔴 CRITICAL</span>'
      : entry.severity_badge === 'YELLOW'
      ? '<span class="badge badge-amber">🟡 MODERATE</span>'
      : '<span class="badge badge-green">🟢 ROUTINE</span>';

    return `
      <tr style="${entry.severity_badge === 'RED' ? 'background:var(--status-danger-tint);' : ''}">
        <td><strong class="text-mono" style="font-size:17px; color:var(--brand-primary);">${entry.token_number}</strong></td>
        <td>
          <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
            ${channelBadge}
            ${langBadge}
          </div>
        </td>
        <td>${severityBadge}</td>
        <td>
          <div style="font-weight:600; color:var(--text-primary); font-size:14px;">${entry.summary_30_words || 'Patient intake recorded'}</div>
          ${entry.has_medication_conflict ? '<span style="color:var(--status-warning); font-size:11px; font-weight:700;">⚠ Drug Interaction Alert</span>' : ''}
        </td>
        <td><span class="badge badge-blue">${entry.fact_count || 3} facts</span></td>
        <td style="text-align:right;">
          <a href="#/doctor/patient/${entry.encounter_id}" class="btn btn-primary btn-sm">
            Review Case →
          </a>
        </td>
      </tr>
    `;
  }).join('');
}

export async function initDoctorQueue() {
  async function fetchQueue() {
    try {
      const res = await doctorApi.getQueue();
      const q = res.queue || [];
      store.setDoctorQueue(q, res.total_waiting);
      _updateDom(q);
    } catch (e) {
      console.warn('Doctor queue API fetch fallback (using local sample):', e);
      const fallbackQueue = [
        {
          encounter_id: 'enc-demo-lakshmi-001',
          token_number: 'A-101',
          channel: 'kiosk',
          severity_badge: 'RED',
          summary_30_words: 'எனக்கு மூன்று நாட்களாக மார்பு வலி உள்ளது (Chest discomfort for 3 days)',
          fact_count: 5,
          has_medication_conflict: true,
          has_red_flags: true,
          language: 'ta'
        },
        {
          encounter_id: 'enc-demo-ananya-003',
          token_number: 'A-103',
          channel: 'android_byod',
          severity_badge: 'RED',
          summary_30_words: 'Cannot catch breath, chest tightness since last night',
          fact_count: 4,
          has_medication_conflict: false,
          has_red_flags: true,
          language: 'en'
        },
        {
          encounter_id: 'enc-demo-sunita-004',
          token_number: 'IVR-402',
          channel: 'ivr_phone',
          severity_badge: 'RED',
          summary_30_words: 'Acute weakness, dizziness, extreme thirst reported via telephony',
          fact_count: 3,
          has_medication_conflict: false,
          has_red_flags: true,
          language: 'hi'
        }
      ];
      const kioskState = store.getState().kiosk || {};
      const currentPatientQueueItem = (kioskState.encounterId || kioskState.patientWords) ? [{
        encounter_id: kioskState.encounterId || 'enc-kiosk-live',
        token_number: kioskState.tokenNumber || 'A-261',
        channel: kioskState.channel || 'kiosk',
        severity_badge: kioskState.severityBadge || 'GREEN',
        summary_30_words: kioskState.patientWords || 'Clinical intake completed at OPD Kiosk',
        fact_count: (kioskState.extractedFacts && kioskState.extractedFacts.length) || 3,
        has_medication_conflict: false,
        has_red_flags: kioskState.severityBadge === 'RED',
        language: kioskState.language || 'hi'
      }] : [];
      const combinedQueue = [...currentPatientQueueItem, ...fallbackQueue];
      store.setDoctorQueue(combinedQueue, combinedQueue.length);
      _updateDom(combinedQueue);
    }
  }

  function _updateDom(q) {
    const totalEl = document.getElementById('doctorQueueCount');
    if (totalEl) totalEl.textContent = q.length;

    const critEl = document.getElementById('doctorCriticalCount');
    if (critEl) critEl.textContent = q.filter(x => x.severity_badge === 'RED').length;

    const tbody = document.getElementById('doctorQueueTableBody');
    if (tbody) tbody.innerHTML = _renderRows(q);
  }

  await fetchQueue();

  const refreshBtn = document.getElementById('btnRefreshDoctorQueue');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', fetchQueue);
  }

  // Auto-poll every 5 seconds for live multi-window synchronization
  pollTimer = setInterval(fetchQueue, 5000);
}

export function destroyDoctorQueue() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}
