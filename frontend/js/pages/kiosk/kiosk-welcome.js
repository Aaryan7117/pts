/**
 * MediKiosk Web — Screen 01: Kiosk Welcome
 * Features interactive AI Doctor Avatar, high-visibility touch CTAs, and language quick toggle.
 */

import { store } from '../../store.js';
import { DoctorAvatar } from '../../components/avatar-3d.js';
import { kioskApi } from '../../api/kiosk.api.js';

let avatarInstance = null;

export function renderKioskWelcome() {
  const state = store.getState();
  const lang = state.kiosk.language || 'hi';

  const welcomeHeading = lang === 'hi' ? 'आयुष ओपीडी में आपका स्वागत है' : 'Welcome to MediKiosk OPD';
  const welcomeSub = lang === 'hi' 
    ? 'डॉक्टर से मिलने से पहले, अपनी स्वास्थ्य समस्याओं को सरल शब्दों में दर्ज करें।'
    : 'Before meeting your physician, tell us about your health concerns in simple words.';
  const startBtnText = lang === 'hi' ? 'शुरू करें / START' : 'START INTAKE / शुरू करें';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane (35%): Hospital Brand & Attendant Help -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div style="display:flex; align-items:center; gap:12px;">
              <div style="width:44px; height:44px; border-radius:12px; background:var(--brand-primary); color:#fff; display:flex; align-items:center; justify-content:center;">
                <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2v20M2 12h20"></path>
                </svg>
              </div>
              <div>
                <h2 style="font-size:18px; font-weight:800; line-height:1.1;">All India Institute of Ayurveda</h2>
                <div style="font-size:12px; color:var(--status-ayush); font-weight:600;">Autonomous OPD Intake Kiosk</div>
              </div>
            </div>

            <div class="kiosk-step-indicator" style="margin-top:var(--space-6);">
              Screen 01 · Lobby Reception
            </div>

            <p style="font-size:14px; color:var(--text-secondary); line-height:1.5; margin-top:var(--space-3);">
              This autonomous station prepares your case history, digitizes paper prescriptions, and assigns your queue ticket.
            </p>
          </div>

          <!-- Doctor Station Shortcut & Attendant Help -->
          <div style="display:flex; flex-direction:column; gap:var(--space-3);">
            <div class="kiosk-audio-help-box">
              <span style="font-size:24px;">🔊</span>
              <div style="font-size:13px; color:var(--text-primary);">
                <strong>Voice-Guided:</strong> You can speak naturally in your mother tongue.
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; color:var(--text-muted);">
              <span>Station ID: KIOSK-OPD-01</span>
              <a href="#/doctor/login" style="color:var(--text-muted); text-decoration:none;">🔒 Doctor Login (1234)</a>
            </div>
          </div>
        </div>

        <!-- Right Pane (65%): Doctor Avatar & Oversized Primary CTA -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="align-items:center; justify-content:center; text-align:center;">
            <!-- 3D / Animated Doctor Avatar Canvas Container -->
            <div id="kioskAvatarContainer" style="margin-bottom:var(--space-6);"></div>

            <h1 class="text-h1" style="margin-bottom:var(--space-3);">${welcomeHeading}</h1>
            <p class="text-body-lg" style="max-width:600px; margin-bottom:var(--space-8);">${welcomeSub}</p>

            <button id="btnKioskStart" class="btn btn-primary btn-touch" style="width:100%; max-width:440px; justify-content:center;">
              ${startBtnText} →
            </button>
          </div>

          <div class="kiosk-footer-bar">
            <span style="font-size:13px; color:var(--text-muted);">
              English · हिन्दी · தமிழ் · తెలుగు · मराठी
            </span>
            <a href="#/account-type" class="btn btn-ghost btn-sm">Switch Portal</a>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskWelcome() {
  // Mount Doctor Avatar
  avatarInstance = new DoctorAvatar('kioskAvatarContainer');
  avatarInstance.mount();

  const startBtn = document.getElementById('btnKioskStart');
  if (startBtn) {
    startBtn.addEventListener('click', async () => {
      // Bootstrap encounter with backend
      try {
        startBtn.disabled = true;
        startBtn.textContent = 'Initializing Encounter...';
        const res = await kioskApi.bootstrap({
          device_channel: 'kiosk',
          language: store.getState().kiosk.language || 'hi'
        });
        store.setKioskBootstrapData({
          encounterId: res.encounter_id,
          patientId: res.patient_id,
          tokenNumber: res.token_number
        });
      } catch (e) {
        console.warn('Backend bootstrap fallback to local session:', e);
        store.setKioskBootstrapData({
          encounterId: `enc-${Date.now().toString(36)}`,
          patientId: `pat-${Date.now().toString(36)}`,
          tokenNumber: 'A-261'
        });
      }
      window.location.hash = '#/kiosk/language';
    });
  }
}

export function destroyKioskWelcome() {
  if (avatarInstance) {
    avatarInstance.destroy();
    avatarInstance = null;
  }
}
