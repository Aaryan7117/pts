/**
 * MediKiosk Web — Screen 05: Care Stream / OPD Specialty Selection
 */

import { store } from '../../store.js';
import { i18n } from '../../i18n.js';

export function renderKioskCareStream() {
  const lang = store.getState().kiosk.language || 'hi';
  const currentStream = store.getState().kiosk.careStream || 'General Medicine';

  const careStreams = [
    {
      id: 'General Medicine',
      icon: '🩺',
      title: i18n.t('dept_general', lang),
      desc: i18n.t('dept_general_desc', lang)
    },
    {
      id: 'Kayachikitsa (AYUSH)',
      icon: '🌿',
      title: i18n.t('dept_ayush', lang),
      desc: i18n.t('dept_ayush_desc', lang)
    },
    {
      id: 'Follow-up',
      icon: '📋',
      title: i18n.t('dept_followup', lang),
      desc: i18n.t('dept_followup_desc', lang)
    },
    {
      id: 'Emergency',
      icon: '🚨',
      title: i18n.t('dept_emergency', lang),
      desc: i18n.t('dept_emergency_desc', lang)
    }
  ];

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 05 · Step 3 of 6
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">${i18n.t('care_dept_heading', lang)}</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              ${i18n.t('care_dept_sub', lang)}
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
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">${i18n.t('care_stream_title', lang)}</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">${i18n.t('care_stream_sub', lang)}</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-4);">
              ${careStreams.map(stream => `
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
            <a href="#/kiosk/consent" class="btn btn-secondary btn-lg">${i18n.t('back', lang)}</a>
            <button id="btnCareStreamContinue" class="btn btn-primary btn-touch" style="min-width:260px; justify-content:center;">
              ${i18n.t('continue', lang)}
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
