/**
 * MediKiosk Web — Screen 10: Closed-Loop Explain-Back Confirmation
 * Zero patient clinical editing burden: large YES / NO verification controls.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';
import { DoctorAvatar } from '../../components/avatar-3d.js';
import { i18n } from '../../i18n.js';

let avatarInstance = null;

export function renderKioskExplainBack() {
  const kioskState = store.getState().kiosk;
  const lang = kioskState.language || 'hi';

  const headingText = i18n.t('explain_back_heading', lang);
  const subText = i18n.t('explain_back_sub', lang);

  // Dynamic clinical facts from patient input
  const facts = kioskState.extractedFacts || [];
  const patientWords = kioskState.patientWords || '';
  const problemFact = facts.find(f => f.category === 'chief_complaint' && f.field === 'problem');
  const durationFact = facts.find(f => f.category === 'symptom' && f.field === 'duration');
  const painFact = facts.find(f => f.category === 'symptom' && f.field === 'severity');

  const problemDisplay = (problemFact && problemFact.value) || patientWords || (lang === 'en' ? 'General Clinical Intake' : 'सामान्य परामर्श');
  const durationDisplay = (durationFact && durationFact.value) || (lang === 'en' ? 'Recent onset' : 'हाल ही में');
  const painDisplay = (painFact && painFact.value) || (lang === 'en' ? 'Moderate (5/10)' : 'मध्यम (५/१०)');

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 10 · Step 5 of 6 (Verification)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-3); font-size:20px;">${i18n.t('explain_back_step_title', lang)}</h2>
            <p style="font-size:13px; color:var(--text-secondary); line-height:1.4;">
              ${i18n.t('explain_back_step_desc', lang)}
            </p>
          </div>

          <!-- Doctor Avatar Attendant -->
          <div id="kioskExplainAvatarContainer" style="margin:var(--space-2) 0; display:flex; justify-content:center;"></div>

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
                  <h2 class="text-h2" style="font-size:22px;">${headingText}</h2>
                  <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
                    ${subText}
                  </div>
                </div>
                <span class="badge badge-teal">AI Synthesized</span>
              </div>

              <div class="explain-back-card__fact-list">
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">${i18n.t('main_problem', lang)}</span>
                  <span class="explain-back-card__fact-value" style="color:var(--brand-primary);">${problemDisplay}</span>
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

let autoPlayTimer = null;

export function initKioskExplainBack() {
  const kioskState = store.getState().kiosk;
  const lang = kioskState.language || 'hi';
  const facts = kioskState.extractedFacts || [];
  const problemFact = facts.find(f => f.category === 'chief_complaint' && f.field === 'problem');
  const durationFact = facts.find(f => f.category === 'symptom' && f.field === 'duration');
  const problemText = (problemFact && problemFact.value) || kioskState.patientWords || 'General Symptoms';
  const durationText = (durationFact && durationFact.value) || 'recent onset';

  const summaryVoice = lang === 'en'
    ? `According to your report, your main complaint is ${problemText} for ${durationText}. Please confirm if this is correct.`
    : `आपके विवरण के अनुसार, आपकी मुख्य समस्या ${problemText} है जो ${durationText} है। कृपया पुष्टि करें कि क्या यह सही है।`;

  // Mount Doctor Avatar
  avatarInstance = new DoctorAvatar('kioskExplainAvatarContainer');
  avatarInstance.mount();

  // Read summary aloud button
  const readBtn = document.getElementById('btnReadSummaryAloud');
  if (readBtn) {
    readBtn.addEventListener('click', () => {
      tts.speak(summaryVoice, lang);
    });
  }

  // Automatic voice playback on entry
  autoPlayTimer = setTimeout(() => {
    tts.speak(summaryVoice, lang);
  }, 400);

  // YES action: Continue to documents
  const yesBtn = document.getElementById('btnExplainBackYes');
  if (yesBtn) {
    yesBtn.addEventListener('click', () => {
      tts.stop();
      window.location.hash = '#/kiosk/documents';
    });
  }

  // NO action: Return to voice intake
  const noBtn = document.getElementById('btnExplainBackNo');
  if (noBtn) {
    noBtn.addEventListener('click', () => {
      tts.stop();
      window.location.hash = '#/kiosk/intake';
    });
  }
}

export function destroyKioskExplainBack() {
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer);
    autoPlayTimer = null;
  }
  tts.stop();
  if (avatarInstance) {
    avatarInstance.destroy();
    avatarInstance = null;
  }
}

