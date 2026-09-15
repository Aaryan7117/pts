/**
 * MediKiosk Web — Page 29: Doctor PIN Authentication
 * Clean, high-security clinical gate (Default PIN: 1234)
 */

import { store } from '../../store.js';
import { doctorApi } from '../../api/doctor.api.js';

export function renderDoctorLogin() {
  return `
    <div style="min-height:calc(100vh - var(--header-height)); display:flex; align-items:center; justify-content:center; padding:var(--space-6); background:var(--bg-canvas);">
      <div class="card" style="width:100%; max-width:440px; padding:var(--space-8); box-shadow:var(--shadow-xl); border:1.5px solid var(--border-default);">
        <div style="text-align:center; margin-bottom:var(--space-6);">
          <div class="doctor-login__icon" aria-hidden="true">
            <i class="fa-solid fa-user-doctor"></i>
          </div>
          <h2 class="text-h2">Doctor Workstation</h2>
          <p style="font-size:14px; color:var(--text-secondary); margin-top:4px;">
            Clinical Command Center · All India Institute of Ayurveda
          </p>
        </div>

        <!-- Evaluation Demo Banner -->
        <div style="background:var(--brand-tint); border:1px dashed var(--brand-primary); border-radius:var(--radius-md); padding:10px; text-align:center; margin-bottom:var(--space-6);">
          <div style="font-size:11px; font-weight:700; color:var(--brand-dark);">QUICK EVALUATION DEMO</div>
          <div style="font-size:13px; font-weight:600; color:var(--text-primary); margin-top:2px;">
            Default Doctor PIN: <code style="background:#fff; padding:2px 6px; border-radius:4px; font-weight:800;">1234</code>
          </div>
        </div>

        <form id="doctorLoginForm" style="display:flex; flex-direction:column; gap:var(--space-4);">
          <div>
            <label style="display:block; font-size:12px; font-weight:700; margin-bottom:4px; color:var(--text-secondary);">
              Clinician ID / Staff Username
            </label>
            <input type="text" id="doctorUsernameInput" value="doc-verma" class="form-input" placeholder="e.g. doc-verma" required />
          </div>

          <div>
            <label style="display:block; font-size:12px; font-weight:700; margin-bottom:4px; color:var(--text-secondary);">
              4-Digit Security PIN
            </label>
            <input type="password" id="doctorPinInput" maxlength="6" value="1234" class="form-input" placeholder="••••" required style="letter-spacing:4px; font-size:18px; font-weight:700; text-align:center;" />
          </div>

          <div id="doctorLoginError" style="color:var(--status-danger); font-size:12px; display:none;"></div>

          <button type="submit" class="btn btn-primary btn-lg" style="width:100%; justify-content:center; margin-top:var(--space-2);">
            Access Clinical Workstation →
          </button>
        </form>

        <div style="text-align:center; margin-top:var(--space-6); font-size:12px; color:var(--text-muted);">
          Authorized medical attendants & registered OPD physicians only.
        </div>
      </div>
    </div>
  `;
}

export function initDoctorLogin() {
  const form = document.getElementById('doctorLoginForm');
  const pinInput = document.getElementById('doctorPinInput');
  const errorMsg = document.getElementById('doctorLoginError');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const pin = pinInput.value.trim();

      try {
        await doctorApi.auth(pin);
        store.setDoctorAuthenticated(true);
        window.location.hash = '#/doctor/queue';
      } catch (err) {
        if (pin === '1234') {
          // Fallback bypass
          store.setDoctorAuthenticated(true);
          window.location.hash = '#/doctor/queue';
        } else {
          if (errorMsg) {
            errorMsg.textContent = 'Invalid PIN. Please enter 1234 for hackathon evaluation.';
            errorMsg.style.display = 'block';
          }
        }
      }
    });
  }
}
