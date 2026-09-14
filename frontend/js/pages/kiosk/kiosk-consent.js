/**
 * MediKiosk Web — Screen 03: Plain-Language Informed Consent
 * Compliant with DPDP Act & ABDM: 3 transparent points explaining data purpose and retention.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';
import { i18n } from '../../i18n.js';

export function renderKioskConsent() {
  const lang = store.getState().kiosk.language || 'hi';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 03 · Step 2 of 6
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">${i18n.t('consent_title', lang)}</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              ${i18n.t('consent_sub', lang)}
            </p>
          </div>

          <button id="btnReadConsent" class="btn btn-secondary btn-md" style="width:100%; justify-content:center;">
            ${i18n.t('hear_explanation', lang)}
          </button>
        </div>

        <!-- Right Pane: 3 Safety Cards & Agreement -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">${i18n.t('consent_title', lang)}</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">${i18n.t('consent_sub', lang)}</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-4);">
              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">🎯</div>
                <div>
                  <h3 class="text-h4">${i18n.t('consent_point1_title', lang)}</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    ${i18n.t('consent_point1_desc', lang)}
                  </p>
                </div>
              </div>

              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">🔒</div>
                <div>
                  <h3 class="text-h4">${i18n.t('consent_point2_title', lang)}</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    ${i18n.t('consent_point2_desc', lang)}
                  </p>
                </div>
              </div>

              <div class="card card-sm" style="display:flex; gap:var(--space-4); align-items:flex-start;">
                <div style="font-size:24px;">👨‍⚕️</div>
                <div>
                  <h3 class="text-h4">${i18n.t('consent_point3_title', lang)}</h3>
                  <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
                    ${i18n.t('consent_point3_desc', lang)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/language" class="btn btn-secondary btn-lg">${i18n.t('back', lang)}</a>
            <div style="display:flex; gap:var(--space-3);">
              <a href="#/kiosk/welcome" class="btn btn-ghost btn-lg">${i18n.t('decline', lang)}</a>
              <button id="btnAgreeConsent" class="btn btn-ayush btn-touch" style="min-width:280px; justify-content:center;">
                ${i18n.t('agree_continue', lang)}
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
      const text = `${i18n.t('consent_point1_desc', lang)} ${i18n.t('consent_point2_desc', lang)}`;
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
