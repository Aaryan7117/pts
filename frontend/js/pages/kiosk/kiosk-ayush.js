/**
 * MediKiosk Web — Screen 18: AYUSH Dashavidha Pariksha (Lifestyle & Digestion)
 * Captures fundamental Ayurvedic factors using everyday, non-jargon questions.
 */

import { store } from '../../store.js';
import { kioskApi } from '../../api/kiosk.api.js';
import { i18n } from '../../i18n.js';

export function renderKioskAyush() {
  const lang = store.getState().kiosk.language || 'hi';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator" style="background:var(--status-ayush-tint, #eaf8f0); color:var(--status-ayush);">
              Screen 18 · AYUSH Profile
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">${i18n.t('ayush_step_title', lang)}</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              ${i18n.t('ayush_step_desc', lang)}
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
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">${i18n.t('ayush_title', lang)}</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6);">${i18n.t('ayush_sub', lang)}</p>

            <div style="display:flex; flex-direction:column; gap:var(--space-5);">
              <!-- 1. Digestion (Agni) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  ${i18n.t('appetite_digestion', lang)}
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupAgni">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="agni" data-val="sama">
                    ${i18n.t('regular_hunger', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="agni" data-val="manda">
                    ${i18n.t('slow_hunger', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="agni" data-val="tikshna">
                    ${i18n.t('intense_hunger', lang)}
                  </button>
                </div>
              </div>

              <!-- 2. Bowel Habit (Koshtha) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  ${i18n.t('bowel_regularity', lang)}
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupKoshtha">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="koshtha" data-val="madhyama">
                    ${i18n.t('bowel_regular', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="koshtha" data-val="krura">
                    ${i18n.t('bowel_constipated', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="koshtha" data-val="mridu">
                    ${i18n.t('bowel_loose', lang)}
                  </button>
                </div>
              </div>

              <!-- 3. Sleep (Nidra) -->
              <div class="card card-sm">
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:var(--space-3);">
                  ${i18n.t('sleep_quality', lang)}
                </div>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3);" id="groupNidra">
                  <button class="btn btn-secondary btn-md ayush-chip selected" data-field="nidra" data-val="sound">
                    ${i18n.t('sleep_sound', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="nidra" data-val="disturbed">
                    ${i18n.t('sleep_disturbed', lang)}
                  </button>
                  <button class="btn btn-secondary btn-md ayush-chip" data-field="nidra" data-val="insomnia">
                    ${i18n.t('sleep_difficulty', lang)}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/ocr-results" class="btn btn-secondary btn-lg">${i18n.t('back', lang)}</a>
            <button id="btnAyushFinish" class="btn btn-ayush btn-touch" style="min-width:300px; justify-content:center;">
              ${i18n.t('btn_complete_token', lang)}
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

      const selectedAgni = document.querySelector('.ayush-chip.selected[data-field="agni"]')?.getAttribute('data-val') || 'sama';
      const selectedKoshtha = document.querySelector('.ayush-chip.selected[data-field="koshtha"]')?.getAttribute('data-val') || 'madhyama';
      const selectedNidra = document.querySelector('.ayush-chip.selected[data-field="nidra"]')?.getAttribute('data-val') || 'sound';

      const ayushAssessment = {
        agni: {
          agni_type: selectedAgni,
          hunger_frequency: selectedAgni === 'sama' ? 'normal' : (selectedAgni === 'tikshna' ? 'intense' : 'sluggish'),
          post_meal_heaviness: selectedAgni === 'manda'
        },
        koshtha: {
          bowel_frequency: selectedKoshtha === 'krura' ? 'irregular' : 'daily',
          stool_consistency: selectedKoshtha === 'mridu' ? 'loose' : (selectedKoshtha === 'krura' ? 'hard' : 'formed'),
          requires_laxative: selectedKoshtha === 'krura'
        },
        nidra: {
          sleep_quality: selectedNidra,
          hours_per_night: selectedNidra === 'sound' ? 7 : (selectedNidra === 'insomnia' ? 4 : 5)
        }
      };

      store.updateKioskIntake({ ayushRecord: ayushAssessment });

      const encounterId = store.getState().kiosk.encounterId;
      if (encounterId) {
        try {
          await kioskApi.saveAyushAssessment(encounterId, ayushAssessment);
        } catch (e) {
          console.warn('AYUSH save fallback:', e);
        }
      }

      window.location.hash = '#/kiosk/queue';
    });
  }
}
