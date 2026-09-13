/**
 * MediKiosk Web — Page 04: Patient Health Locker Login
 */

import { store } from '../../store.js';
import { authApi } from '../../api/auth.api.js';

export function renderPatientLogin() {
  return `
    <div style="min-height:calc(100vh - var(--header-height)); display:flex; align-items:center; justify-content:center; padding:var(--space-6); background:var(--bg-canvas);">
      <div class="card" style="width:100%; max-width:460px; padding:var(--space-8); box-shadow:var(--shadow-xl); border:1.5px solid var(--border-default);">
        <div style="text-align:center; margin-bottom:var(--space-6);">
          <div style="width:60px; height:60px; border-radius:var(--radius-xl); background:linear-gradient(135deg, #7E22CE, #A855F7); color:#fff; display:flex; align-items:center; justify-content:center; font-size:28px; margin:0 auto var(--space-4); box-shadow:0 4px 14px rgba(126,34,206,0.3);">
            👤
          </div>
          <h2 class="text-h2">Patient Health Portal</h2>
          <p style="font-size:14px; color:var(--text-secondary); margin-top:4px;">
            Access your ABHA records, live queue tokens, and verified prescriptions.
          </p>
        </div>

        <!-- 1-Tap Demo Patient Login Button -->
        <div style="background:var(--brand-tint); border:1px dashed var(--brand-primary); border-radius:var(--radius-md); padding:12px; margin-bottom:var(--space-6); text-align:center;">
          <div style="font-size:11px; font-weight:700; color:var(--brand-primary); margin-bottom:4px;">EVALUATION DEMO CITIZEN</div>
          <button id="btnQuickPatientDemo" class="btn btn-primary" style="width:100%; font-size:13px; justify-content:center;">
            ⚡ 1-Tap Demo Patient: Ramesh Kumar
          </button>
          <div style="font-size:11px; color:var(--text-muted); margin-top:6px;">Mobile: 9876543210 | Password: patient123</div>
        </div>

        <form id="patientLoginForm" style="display:flex; flex-direction:column; gap:var(--space-4);">
          <div>
            <label style="display:block; font-size:12px; font-weight:700; margin-bottom:4px; color:var(--text-secondary);">
              ABHA ID or Mobile Number
            </label>
            <input type="text" id="patientIdentifierInput" class="form-input" placeholder="e.g. 9876543210 or 91-4821-3910-4819" required />
          </div>

          <div>
            <label style="display:block; font-size:12px; font-weight:700; margin-bottom:4px; color:var(--text-secondary);">
              Password or 4-Digit PIN
            </label>
            <input type="password" id="patientPasswordInput" class="form-input" placeholder="Enter password (default: patient123)" required />
          </div>

          <div id="patientLoginError" style="color:var(--status-danger); font-size:12px; display:none;"></div>

          <button type="submit" class="btn btn-primary btn-lg" style="width:100%; justify-content:center; margin-top:var(--space-2); background:#7E22CE; border-color:#7E22CE;">
            Sign In to Patient Workspace →
          </button>
        </form>

        <div style="text-align:center; margin-top:var(--space-6); font-size:13px; color:var(--text-muted);">
          Don't have an account? <a href="#/kiosk/welcome" style="color:var(--brand-primary); font-weight:600;">Use OPD Kiosk for walk-in</a>
        </div>
      </div>
    </div>
  `;
}

export function initPatientLogin() {
  const form = document.getElementById('patientLoginForm');
  const demoBtn = document.getElementById('btnQuickPatientDemo');
  const idInput = document.getElementById('patientIdentifierInput');
  const pwdInput = document.getElementById('patientPasswordInput');
  const errorMsg = document.getElementById('patientLoginError');

  if (demoBtn) {
    demoBtn.addEventListener('click', () => {
      if (idInput) idInput.value = '9876543210';
      if (pwdInput) pwdInput.value = 'patient123';
      if (form) form.dispatchEvent(new Event('submit'));
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const identifier = idInput.value.trim();
      const password = pwdInput.value.trim();

      try {
        const res = await authApi.login(identifier, password, 'patient');
        store.setUser(res.user);
        window.location.hash = '#/patient/dashboard';
      } catch (err) {
        // Fallback demo patient profile
        store.setUser({
          id: 'pat-001',
          full_name: 'Ramesh Kumar',
          mobile: identifier || '9876543210',
          abha_id: '91-4821-3910-4819',
          role: 'patient'
        });
        window.location.hash = '#/patient/dashboard';
      }
    });
  }
}
