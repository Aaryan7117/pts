/**
 * MediKiosk Web — Screen 10: Closed-Loop Explain-Back Confirmation
 * Zero patient clinical editing burden: large YES / NO verification controls.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';
import { i18n } from '../../i18n.js';

export function renderKioskExplainBack() {
  const kioskState = store.getState().kiosk;
  const lang = kioskState.language || 'hi';

  const headingText = i18n.t('explain_back_heading', lang);
  const subText = i18n.t('explain_back_sub', lang);

  // Check if patient provided custom words or use localized defaults
  const facts = kioskState.extractedFacts || [];
  const problemFact = facts.find(f => f.category === 'chief_complaint' && f.field === 'problem');
  const durationFact = facts.find(f => f.category === 'symptom' && f.field === 'duration');
  const painFact = facts.find(f => f.category === 'symptom' && f.field === 'severity');

  const problemDisplay = problemFact ? problemFact.value : i18n.t('sample_fact_problem', lang);
  const durationDisplay = durationFact ? durationFact.value : i18n.t('sample_fact_duration', lang);
  const painDisplay = painFact ? painFact.value : i18n.t('sample_fact_pain', lang);

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 10 · Step 5 of 6 (Verification)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">${i18n.t('explain_back_step_title', lang)}</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              ${i18n.t('explain_back_step_desc', lang)}
            </p>
          </div>

          <button id="btnReadSummaryAloud" class="btn btn-secondary btn-md" style="justify-content:center;">
            ${i18n.t('hear_summary', lang)}
          </button>
        </div>

        <!-- Right Pane: Closed-Loop Summary Card -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="justify-content:center;">
            <div class="explain-back-card">
              <div class="explain-back-card__header">
                <div>
                  <h2 class="text-h2">${headingText}</h2>
                  <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
                    ${subText}
                  </div>
                </div>
                <span class="badge badge-teal">AI Synthesized</span>
              </div>

              <div class="explain-back-card__fact-list">
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">${i18n.t('main_problem', lang)}</span>
                  <span class="explain-back-card__fact-value">${problemDisplay}</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">${i18n.t('duration', lang)}</span>
                  <span class="explain-back-card__fact-value">${durationDisplay}</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">${i18n.t('pain_level', lang)}</span>
                  <span class="explain-back-card__fact-value">${painDisplay}</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">${i18n.t('breathing_diff', lang)}</span>
                  <span class="explain-back-card__fact-value" style="color:var(--status-success);">${i18n.t('none_reported', lang)}</span>
                </div>
              </div>

              <!-- Two Massive Verification Actions -->
              <div class="explain-back-card__actions">
                <button id="btnExplainBackNo" class="btn btn-outline-danger btn-touch" style="justify-content:center;">
                  ${i18n.t('btn_no_repeat', lang)}
                </button>
                <button id="btnExplainBackYes" class="btn btn-ayush btn-touch" style="justify-content:center;">
                  ${i18n.t('btn_yes_correct', lang)}
                </button>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/intake" class="btn btn-secondary btn-lg">${i18n.t('rerecord', lang)}</a>
            <span style="font-size:13px; color:var(--text-muted);">
              One-tap confirmation · No medical editing required
            </span>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskExplainBack() {
  const lang = store.getState().kiosk.language || 'hi';
  const summaryVoice = i18n.t('summary_voice_text', lang);

  // Read summary aloud button
  const readBtn = document.getElementById('btnReadSummaryAloud');
  if (readBtn) {
    readBtn.addEventListener('click', () => {
      tts.speak(summaryVoice, lang);
    });
  }

  // Automatic voice playback on entry
  setTimeout(() => {
    tts.speak(summaryVoice, lang);
  }, 400);

  // YES action: Continue to documents
  const yesBtn = document.getElementById('btnExplainBackYes');
  if (yesBtn) {
    yesBtn.addEventListener('click', () => {
      window.location.hash = '#/kiosk/documents';
    });
  }

  // NO action: Return to voice intake
  const noBtn = document.getElementById('btnExplainBackNo');
  if (noBtn) {
    noBtn.addEventListener('click', () => {
      window.location.hash = '#/kiosk/intake';
    });
  }
}
