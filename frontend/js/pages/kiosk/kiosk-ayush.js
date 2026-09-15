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

      const agniByType = {
        sama: { appetite_pattern: 'regular', post_meal_heaviness: false, bowel_regularity: 'regular' },
        manda: { appetite_pattern: 'low_absent', post_meal_heaviness: true, bowel_regularity: 'sluggish_mucus' },
        tikshna: { appetite_pattern: 'excessive_burning', post_meal_heaviness: false, bowel_regularity: 'loose_burning' },
      };
      const koshthaByType = {
        madhyama: { bowel_frequency: 'once_daily', stool_consistency: 'soft_formed' },
        krura: { bowel_frequency: 'once_or_less_daily', stool_consistency: 'hard_dry' },
        mridu: { bowel_frequency: 'twice_or_more_daily', stool_consistency: 'soft_loose' },
      };
      const sleepByNidra = {
        sound: 'moderate_sound',
        disturbed: 'light_interrupted',
        insomnia: 'light_interrupted',
      };

      const kioskState = store.getState().kiosk || {};
      const symptoms = (kioskState.extractedFacts || [])
        .filter(f => f.category === 'chief_complaint' || f.category === 'symptom')
        .map(f => f.value)
        .filter(Boolean);

      const calculatePayload = {
        prakriti: {
          body_frame: 'medium_muscular',
          skin_texture: 'warm_reddish_sweaty',
          weather_sensitivity: 'intolerant_to_heat',
          sleep_pattern: sleepByNidra[selectedNidra] || 'moderate_sound',
        },
        agni: agniByType[selectedAgni] || agniByType.sama,
        koshtha: koshthaByType[selectedKoshtha] || koshthaByType.madhyama,
        symptoms,
      };

      const encounterId = kioskState.encounterId;
      if (encounterId && !String(encounterId).startsWith('enc-offline')) {
        try {
          // Match monolith flow: calculate → persist scored AyurvedicIntakeRecord
          const calculatedRecord = await kioskApi.calculateAyush(calculatePayload);
          await kioskApi.saveAyushAssessment(encounterId, calculatedRecord);
          store.updateKioskIntake({ ayushRecord: calculatedRecord });
        } catch (e) {
          console.warn('AYUSH save fallback:', e);
          store.updateKioskIntake({ ayushRecord: calculatePayload });
          store.addToast('AYUSH saved locally — server sync pending', 'warning');
        }
      } else {
        store.updateKioskIntake({ ayushRecord: calculatePayload });
        store.addToast('No active encounter — AYUSH kept on this device only', 'warning');
      }

      window.location.hash = '#/kiosk/queue';
    });
  }
}
