/**
 * MediKiosk Web — Screen 02: Kiosk Language Selection
 * Selects 1 of 5 supported Indian languages and sets system-wide locale & speech synthesizer.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';

const LANGUAGES = [
  { code: 'hi', native: 'हिन्दी', english: 'Hindi', preview: 'नमस्ते! आयुष ओपीडी में आपका स्वागत है।' },
  { code: 'en', native: 'English', english: 'English', preview: 'Hello! Welcome to MediKiosk OPD intake.' },
  { code: 'ta', native: 'தமிழ்', english: 'Tamil', preview: 'வணக்கம்! ஆயுஷ் மருத்துவமனைக்கு வரவேற்கிறோம்.' },
  { code: 'te', native: 'తెలుగు', english: 'Telugu', preview: 'నమస్కారం! ఆయుష్ ఓపీడీకి స్వాగతం.' },
  { code: 'mr', native: 'मराठी', english: 'Marathi', preview: 'नमस्कार! आयुष ओपीडी मध्ये आपले स्वागत आहे.' }
];

export function renderKioskLanguage() {
  const currentLang = store.getState().kiosk.language || 'hi';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 02 · Step 1 of 6
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Select Language</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              All questions, synthetic speech readouts, and explain-back summaries will use this language.
            </p>
          </div>

          <div class="kiosk-audio-help-box">
            <span style="font-size:24px;">🌐</span>
            <div style="font-size:13px;">
              <strong>5 Official Indian Languages:</strong> Fully supported for voice and touch.
            </div>
          </div>
        </div>

        <!-- Right Pane: Language Choice Cards -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">अपनी भाषा चुनें / Choose Language</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">Tap a card to hear an instant voice sample.</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-4);">
              ${LANGUAGES.map(lang => `
                <div class="choice-card ${currentLang === lang.code ? 'selected' : ''}" data-lang-code="${lang.code}">
                  <div class="choice-card__content">
                    <div class="choice-card__icon-wrap" style="font-size:20px; font-weight:700;">
                      ${lang.code.toUpperCase()}
                    </div>
                    <div>
                      <div class="choice-card__title indic-text">${lang.native}</div>
                      <div class="choice-card__subtitle">${lang.english}</div>
                    </div>
                  </div>
                  <div class="choice-card__radio"></div>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/welcome" class="btn btn-secondary btn-lg">← Back</a>
            <button id="btnLanguageContinue" class="btn btn-primary btn-touch" style="min-width:260px; justify-content:center;">
              Continue / आगे बढ़ें →
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskLanguage() {
  const cards = document.querySelectorAll('.choice-card[data-lang-code]');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      const code = card.getAttribute('data-lang-code');
      store.setKioskLanguage(code);

      // Re-highlight cards
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      // Play vocal confirmation sample
      const langObj = LANGUAGES.find(l => l.code === code);
      if (langObj) {
        tts.speak(langObj.preview, code);
      }
    });
  });

  const continueBtn = document.getElementById('btnLanguageContinue');
  if (continueBtn) {
    continueBtn.addEventListener('click', () => {
      window.location.hash = '#/kiosk/consent';
    });
  }
}
