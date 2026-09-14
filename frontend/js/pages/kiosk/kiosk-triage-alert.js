/**
 * MediKiosk Web — Screen 11: Red-Flag Emergency Protocol & Triage Alert
 * Visually dominant crimson alert halting standard OPD queue and dispatching urgent assistance.
 */

import { store } from '../../store.js';
import { sounds } from '../../audio/sound-effects.js';
import { i18n } from '../../i18n.js';

export function renderKioskTriageAlert() {
  const lang = store.getState().kiosk.language || 'hi';

  return `
    <div class="kiosk-shell" style="background-color:var(--status-danger-tint);">
      <div style="max-width:900px; margin:0 auto; padding:var(--space-10) var(--space-6); text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:calc(100vh - var(--header-height));">
        
        <div style="width:96px; height:96px; border-radius:50%; background:var(--status-danger); color:#fff; display:flex; align-items:center; justify-content:center; font-size:48px; box-shadow:0 0 30px rgba(200,58,58,0.5); margin-bottom:var(--space-6); animation:emergencyPulse 1.5s infinite alternate;">
          🚨
        </div>

        <div class="badge badge-red" style="font-size:14px; padding:8px 18px; margin-bottom:var(--space-4);">
          ${i18n.t('triage_red_badge', lang)}
        </div>

        <h1 class="text-h1" style="color:var(--status-danger); margin-bottom:var(--space-4);">
          ${i18n.t('triage_immediate_attn', lang)}
        </h1>

        <p class="text-body-lg" style="max-width:640px; color:var(--text-primary); margin-bottom:var(--space-8); line-height:1.6;">
          ${i18n.t('triage_urgent_desc', lang)}
        </p>

        <div class="card" style="width:100%; max-width:600px; text-align:left; border:2px solid var(--status-danger); margin-bottom:var(--space-8); background:#fff;">
          <div style="font-size:13px; font-weight:700; color:var(--status-danger); text-transform:uppercase; margin-bottom:4px;">
            ${i18n.t('triage_action_now', lang)}
          </div>
          <div style="font-size:16px; font-weight:700; color:var(--text-primary);">
            ${i18n.t('triage_proceed_room', lang)}
          </div>
          <div style="font-size:13px; color:var(--text-muted); margin-top:4px;">
            ${i18n.t('triage_nurse_alerted', lang)}
          </div>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:var(--space-4); justify-content:center; width:100%; max-width:600px;">
          <button class="btn btn-danger btn-touch" style="flex:1; min-width:260px; justify-content:center;" onclick="alert('Emergency clinical alert dispatched to Casualty Room 001.')">
            ${i18n.t('triage_alert_nurse', lang)}
          </button>
          <a href="#/kiosk/welcome" class="btn btn-secondary btn-touch" style="min-width:200px; justify-content:center;">
            ${i18n.t('triage_return_welcome', lang)}
          </a>
        </div>
      </div>
    </div>

    <style>
      @keyframes emergencyPulse {
        0% { transform: scale(0.95); box-shadow: 0 0 10px rgba(200,58,58,0.4); }
        100% { transform: scale(1.05); box-shadow: 0 0 35px rgba(200,58,58,0.8); }
      }
    </style>
  `;
}

export function initKioskTriageAlert() {
  sounds.playEmergencyChime();
}
