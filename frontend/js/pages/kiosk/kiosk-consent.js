/**
 * MediKiosk Web — Screen 03: Plain-Language Informed Consent
 * Compliant with DPDP Act & ABDM: 3 transparent points explaining data purpose and retention.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';

export function renderKioskConsent() {
  const lang = store.getState().kiosk.language || 'hi';

  const readAloudText = lang === 'hi'
    ? 'हम आपकी स्वास्थ्य समस्याओं को डॉक्टर के लिए संक्षेप में तैयार करने के लिए पूछते हैं। आपकी जानकारी सुरक्षित है।'
    : 'We collect your symptoms to prepare a case summary for your physician. Your data is confidential and secure.';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 03 · Step 2 of 6
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Informed Consent</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              Patient confidentiality is our clinical priority. Review our 3 safety commitments.
            </p>
          </div>

          <button id="btnReadConsent" class="btn btn-secondary btn-md" style="width:100%; justify-content:center;">
            🔊 Hear Explanation
          </button>
        </div>

        <!-- Right Pane: 3 Safety Cards & Agreement -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">Before We Begin / शुरू करने से पहले</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">Please review how your health information is protected:</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-4);">
              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">🎯</div>
                <div>
                  <h3 class="text-h4">1. Why We Ask Symptoms / हम लक्षण क्यों पूछते हैं</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    To prepare an organized clinical history before you enter the doctor's chamber, reducing your wait and consultation rush.
                  </p>
                </div>
              </div>

              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">🔒</div>
                <div>
                  <h3 class="text-h4">2. Prescription Document Security / दस्तावेज़ सुरक्षा</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    Uploaded prescriptions are processed on local hospital servers for medicine OCR and stored securely.
                  </p>
                </div>
              </div>

              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">👨‍⚕️</div>
                <div>
                  <h3 class="text-h4">3. Who Sees Your Records / कौन देख सकता है</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    Only authorized AIIA hospital doctors and medical attendants assigned to your consultation room can access this summary.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/language" class="btn btn-secondary btn-lg">← Back</a>
            <div style="display:flex; gap:var(--space-3);">
              <a href="#/kiosk/welcome" class="btn btn-ghost btn-lg">Decline</a>
              <button id="btnAgreeConsent" class="btn btn-ayush btn-touch" style="min-width:280px; justify-content:center;">
                ✓ I Agree / मुझे स्वीकार है →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskConsent() {
  const readBtn = document.getElementById('btnReadConsent');
  if (readBtn) {
    readBtn.addEventListener('click', () => {
      const lang = store.getState().kiosk.language || 'hi';
      const text = lang === 'hi'
        ? 'हम आपके लक्षण डॉक्टर के लिए संक्षेप में तैयार करने के लिए पूछते हैं। आपकी जानकारी सुरक्षित है।'
        : 'We collect your symptoms to prepare a case summary for your physician. Your data is confidential and secure.';
      tts.speak(text, lang);
    });
  }

  const agreeBtn = document.getElementById('btnAgreeConsent');
  if (agreeBtn) {
    agreeBtn.addEventListener('click', () => {
      window.location.hash = '#/kiosk/care-stream';
    });
  }
}
