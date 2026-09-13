/**
 * MediKiosk Web — Screen 05: Care Stream / OPD Specialty Selection
 */

import { store } from '../../store.js';

const CARE_STREAMS = [
  { id: 'General Medicine', icon: '🩺', title: 'General Medicine / सामान्य चिकित्सा', desc: 'Fever, cough, body pain, blood pressure, diabetes review' },
  { id: 'Kayachikitsa (AYUSH)', icon: '🌿', title: 'Ayurveda / कायचिकित्सा (AYUSH)', desc: 'Holistic Ayurvedic consultation, lifestyle, diet & chronic disorders' },
  { id: 'Follow-up', icon: '📋', title: 'Follow-up Visit / पुराना पर्चा', desc: 'Continuing existing prescription or post-investigation report review' },
  { id: 'Emergency', icon: '🚨', title: 'Emergency / तीव्र दर्द व कष्ट', desc: 'Severe chest pain, breathing difficulty, acute distress (Priority)' }
];

export function renderKioskCareStream() {
  const currentStream = store.getState().kiosk.careStream || 'General Medicine';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 05 · Step 3 of 6
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Care Department</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              Select your consultation specialty to route your case to the right physician cabin.
            </p>
          </div>

          <div class="kiosk-audio-help-box">
            <span style="font-size:24px;">🏛</span>
            <div style="font-size:13px;">
              <strong>All India Institute of Ayurveda:</strong> Integrated Allopathic & AYUSH clinical desks.
            </div>
          </div>
        </div>

        <!-- Right Pane: Care Stream Cards -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">Reason for Visit / आने का कारण</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">Choose which department you wish to consult today:</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-4);">
              ${CARE_STREAMS.map(stream => `
                <div class="choice-card ${currentStream === stream.id ? 'selected' : ''}" data-stream-id="${stream.id}">
                  <div class="choice-card__content">
                    <div class="choice-card__icon-wrap" style="font-size:24px;">
                      ${stream.icon}
                    </div>
                    <div>
                      <div class="choice-card__title">${stream.title}</div>
                      <div class="choice-card__subtitle">${stream.desc}</div>
                    </div>
                  </div>
                  <div class="choice-card__radio"></div>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/consent" class="btn btn-secondary btn-lg">← Back</a>
            <button id="btnCareStreamContinue" class="btn btn-primary btn-touch" style="min-width:260px; justify-content:center;">
              Continue / आगे बढ़ें →
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskCareStream() {
  const cards = document.querySelectorAll('.choice-card[data-stream-id]');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      const streamId = card.getAttribute('data-stream-id');
      store.updateKioskIntake({ careStream: streamId });
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      if (streamId === 'Emergency') {
        window.location.hash = '#/kiosk/triage';
      }
    });
  });

  const continueBtn = document.getElementById('btnCareStreamContinue');
  if (continueBtn) {
    continueBtn.addEventListener('click', () => {
      window.location.hash = '#/kiosk/intake';
    });
  }
}
