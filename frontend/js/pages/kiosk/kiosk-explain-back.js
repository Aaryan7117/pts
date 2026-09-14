/**
 * MediKiosk Web — Screen 10: Closed-Loop Explain-Back Confirmation
 * Zero patient clinical editing burden: large YES / NO verification controls.
 */

import { store } from '../../store.js';
import { tts } from '../../audio/tts-reader.js';

export function renderKioskExplainBack() {
  const kioskState = store.getState().kiosk;
  const lang = kioskState.language || 'hi';

  const headingText = lang === 'hi' 
    ? 'क्या हमने सही समझा?' 
    : 'Did we understand you correctly?';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 10 · Step 5 of 6 (Verification)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Explain-Back Review</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              We reflect back our clinical understanding. Confirm with a single tap.
            </p>
          </div>

          <button id="btnReadSummaryAloud" class="btn btn-secondary btn-md" style="justify-content:center;">
            🔊 Hear Summary Aloud
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
                    Here is the summary prepared for your physician:
                  </div>
                </div>
                <span class="badge badge-teal">AI Synthesized</span>
              </div>

              <div class="explain-back-card__fact-list">
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">Main Problem / मुख्य समस्या</span>
                  <span class="explain-back-card__fact-value">Chest Pain (सीने में दर्द)</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">Duration / कितने दिनों से</span>
                  <span class="explain-back-card__fact-value">3 Days (3 दिन)</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">Pain Level / दर्द की तीव्रता</span>
                  <span class="explain-back-card__fact-value">Moderate 6 / 10</span>
                </div>
                <div class="explain-back-card__fact-row">
                  <span class="explain-back-card__fact-label">Breathing Difficulty / सांस फूलना</span>
                  <span class="explain-back-card__fact-value" style="color:var(--status-success);">None Reported</span>
                </div>
              </div>

              <!-- Two Massive Verification Actions -->
              <div class="explain-back-card__actions">
                <button id="btnExplainBackNo" class="btn btn-outline-danger btn-touch" style="justify-content:center;">
                  ↻ NO, SAY AGAIN / नहीं
                </button>
                <button id="btnExplainBackYes" class="btn btn-ayush btn-touch" style="justify-content:center;">
                  ✓ YES, THAT'S RIGHT / हाँ सही है →
                </button>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/intake" class="btn btn-secondary btn-lg">← Re-record</a>
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
  const summaryVoice = lang === 'hi'
    ? 'हमने समझा कि आपको 3 दिनों से सीने में दर्द है और सांस लेने में तकलीफ नहीं है। क्या यह सही है?'
    : 'We understood you have had chest pain for 3 days with no breathing difficulty. Is this correct?';

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
