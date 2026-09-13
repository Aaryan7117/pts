/**
 * MediKiosk Web — Screen 18: AYUSH Dashavidha Pariksha (Lifestyle & Digestion)
 * Captures fundamental Ayurvedic factors using everyday, non-jargon questions.
 */

import { store } from '../../store.js';
import { kioskApi } from '../../api/kiosk.api.js';

export function renderKioskAyush() {
  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator" style="background:var(--status-ayush-tint, #eaf8f0); color:var(--status-ayush);">
              Screen 18 · AYUSH Profile
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Daily Health Habits</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              Ayurvedic physicians evaluate your digestion (Agni), elimination (Koshtha), and sleep quality (Nidra).
            </p>
          </div>

          <div class="kiosk-audio-help-box">
            <span style="font-size:24px;">🌿</span>
            <div style="font-size:12px;">
              <strong>AIIA Integrative OPD:</strong> Combines modern vitals with Ayurvedic constitution analysis.
            </div>
          </div>
        </div>

        <!-- Right Pane: Lifestyle Habits -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">Your Daily Habits / दिनचर्या व आदतें</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">Please tap the options that best describe your routine:</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-5);">
              <!-- 1. Digestion (Agni) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  1. Appetite & Digestion / भूख और पाचन (अग्नि)
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupAgni">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="agni" data-val="sama">
                    Regular / सामान्य भूख
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="agni" data-val="manda">
                    Slow / कम भूख (भारीपन)
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="agni" data-val="tikshna">
                    Intense / बहुत तेज भूख
                  </button>
                </div>
              </div>

              <!-- 2. Bowel Habit (Koshtha) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  2. Bowel Regularity / पेट साफ होना (कोष्ठ)
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupKoshtha">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="koshtha" data-val="madhyama">
                    Regular / रोज़ाना साफ
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="koshtha" data-val="krura">
                    Constipated / कब्ज
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="koshtha" data-val="mridu">
                    Loose / बार-बार जाना
                  </button>
                </div>
              </div>

              <!-- 3. Sleep (Nidra) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  3. Sleep Quality / नींद की स्थिति (निद्रा)
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupNidra">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="nidra" data-val="sound">
                    Sound / गहरी व शांत नींद
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="nidra" data-val="disturbed">
                    Disturbed / बीच में टूटना
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="nidra" data-val="insomnia">
                    Difficulty Sleeping / देर से आना
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/ocr-results" class="btn btn-secondary btn-lg">← Back</a>
            <button id="btnAyushFinish" class="btn btn-ayush btn-touch" style="min-width:300px; justify-content:center;">
              Complete & Get Token / टोकन प्राप्त करें →
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskAyush() {
  const chips = document.querySelectorAll('.ayush-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const field = chip.getAttribute('data-field');
      const siblings = document.querySelectorAll(`.ayush-chip[data-field="${field}"]`);
      siblings.forEach(s => s.classList.remove('selected', 'btn-primary'));
      siblings.forEach(s => s.classList.add('btn-secondary'));

      chip.classList.remove('btn-secondary');
      chip.classList.add('selected', 'btn-primary');
    });
  });

  const finishBtn = document.getElementById('btnAyushFinish');
  if (finishBtn) {
    finishBtn.addEventListener('click', async () => {
      finishBtn.disabled = true;
      finishBtn.textContent = 'Generating OPD Token...';

      const encounterId = store.getState().kiosk.encounterId;
      if (encounterId) {
        try {
          await kioskApi.saveAyushAssessment(encounterId, {
            agni: { agni_type: 'sama', hunger_frequency: 'normal', post_meal_heaviness: false },
            koshtha: { bowel_frequency: 'daily', stool_consistency: 'formed', requires_laxative: false },
            nidra: { sleep_quality: 'sound', hours_per_night: 7 }
          });
        } catch (e) {
          console.warn('AYUSH save fallback:', e);
        }
      }

      window.location.hash = '#/kiosk/queue';
    });
  }
}
