/**
 * MediKiosk Web — Screen 19: OPD Queue Ticket & Screen 24: Privacy Auto-Reset
 * Prints the OPD queue ticket and strictly resets patient data after 10 seconds for HIPAA/DPDP privacy.
 */

import { store } from '../../store.js';
import { queueApi } from '../../api/queue.api.js';

let countdownInterval = null;

export function renderKioskQueueToken() {
  const kioskState = store.getState().kiosk;
  const token = kioskState.tokenNumber || 'A-261';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator" style="background:var(--status-success-tint); color:var(--status-success);">
              ✓ Intake Completed
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Your Case is Ready</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              Your clinical intake has been transmitted directly to Dr. S. Verma's workstation desk.
            </p>
          </div>

          <!-- Automated Privacy Reset Box -->
          <div style="background:var(--status-danger-tint); border:1.5px solid var(--status-danger); border-radius:var(--radius-xl); padding:var(--space-4); text-align:center;">
            <div style="font-size:11px; font-weight:700; color:var(--status-danger); text-transform:uppercase;">
              🔒 Patient Privacy Protection
            </div>
            <div style="font-size:24px; font-weight:800; color:var(--status-danger); margin:6px 0;" id="kioskResetTimer">
              10s
            </div>
            <div style="font-size:12px; color:var(--pr-slate-800);">
              Screen will automatically wipe all records for the next patient.
            </div>
          </div>
        </div>

        <!-- Right Pane: Digital Queue Ticket -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="align-items:center; justify-content:center;">
            <div class="queue-ticket">
              <div class="queue-ticket__header">All India Institute of Ayurveda · OPD Ticket</div>
              <div style="font-size:14px; color:var(--text-muted);">Department: General Medicine (Kayachikitsa)</div>
              
              <div class="queue-ticket__token" id="ticketTokenDisplay">${token}</div>
              
              <div class="queue-ticket__meta-grid">
                <div>
                  <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase; display:block;">Consulting Doctor</span>
                  <strong style="font-size:15px; color:var(--text-primary);">Dr. S. Verma</strong>
                </div>
                <div>
                  <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase; display:block;">Chamber Room</span>
                  <strong style="font-size:15px; color:var(--brand-primary);">Cabin 102 (1st Floor)</strong>
                </div>
                <div style="margin-top:8px;">
                  <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase; display:block;">Estimated Wait</span>
                  <strong style="font-size:15px; color:var(--status-success);">~12 Minutes</strong>
                </div>
                <div style="margin-top:8px;">
                  <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase; display:block;">Patients Ahead</span>
                  <strong style="font-size:15px; color:var(--status-warning);">2 Patients</strong>
                </div>
              </div>

              <div style="display:flex; flex-direction:column; gap:var(--space-3);">
                <button class="btn btn-secondary btn-lg" onclick="window.print()">
                  🖨 Print Paper Token Slip
                </button>
                <button id="btnResetKioskNow" class="btn btn-danger btn-lg">
                  Wipe & Exit Now / स्क्रीन रीसेट करें
                </button>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <span style="font-size:13px; color:var(--text-muted);">
              Please proceed to Waiting Area A outside Cabin 102.
            </span>
            <a href="#/doctor/queue" class="btn btn-ghost btn-sm" style="color:var(--brand-primary); font-weight:700;">
              Open Dr. Verma's Desk (Window 2) →
            </a>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskQueueToken() {
  const token = store.getState().kiosk.tokenNumber || 'A-261';

  // Fetch live queue status if server is active
  queueApi.getStatus(token)
    .then(status => {
      console.log('Live Queue Status from server:', status);
    })
    .catch(err => {
      console.warn('Queue status API fallback:', err);
    });

  // Automated 10-Second Privacy Countdown
  let secondsRemaining = 10;
  const timerElem = document.getElementById('kioskResetTimer');

  countdownInterval = setInterval(() => {
    secondsRemaining -= 1;
    if (timerElem) {
      timerElem.textContent = `${secondsRemaining}s`;
    }

    if (secondsRemaining <= 0) {
      clearInterval(countdownInterval);
      store.resetKioskSession();
      window.location.hash = '#/kiosk/welcome';
    }
  }, 1000);

  // Manual reset button
  const resetBtn = document.getElementById('btnResetKioskNow');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      clearInterval(countdownInterval);
      store.resetKioskSession();
      window.location.hash = '#/kiosk/welcome';
    });
  }
}

export function destroyKioskQueueToken() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
}
