/**
 * MediKiosk Web — Doctor Avatar Interactive Verification Cockpit
 * Dedicated testbench to evaluate 25 FPS frame rendering, loop smoothness,
 * state switching, and audio/TTS synchronization.
 */

import { DoctorAvatar } from '../../components/avatar-3d.js';
import { tts } from '../../audio/tts-reader.js';

let avatarInstance = null;
let metricsInterval = null;

export function renderKioskAvatarPreview() {
  return `
    <div class="kiosk-shell" style="max-width:1100px; margin:0 auto; padding:var(--space-6);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-6); border-bottom:1px solid var(--border-subtle); padding-bottom:var(--space-4);">
        <div>
          <div class="badge badge-teal" style="margin-bottom:6px;">Clinical 2D Animation Engine</div>
          <h1 class="text-h1" style="font-size:24px;">AI Doctor Avatar — Animation & Speech Sync Lab</h1>
          <p style="color:var(--text-secondary); font-size:14px; margin-top:4px;">
            Benchmarking 25 FPS frame rendering, 150-frame sequence looping, and WebSpeech lifecycle events.
          </p>
        </div>
        <div style="display:flex; gap:12px;">
          <a href="#/kiosk/welcome" class="btn btn-primary btn-md">
            🏥 Go to OPD Kiosk Screen →
          </a>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1.1fr 1fr; gap:var(--space-8); align-items:start;">
        <!-- Left: Avatar Canvas Container -->
        <div style="background:var(--bg-surface); border:1px solid var(--border-default); border-radius:var(--radius-2xl); padding:var(--space-6); box-shadow:var(--shadow-md); text-align:center;">
          <div id="previewAvatarMount" style="margin-bottom:var(--space-4);"></div>

          <!-- Real-time metrics -->
          <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; margin-top:var(--space-4); background:var(--bg-subtle, #f8fafc); border-radius:var(--radius-lg); padding:12px; font-size:12px;">
            <div>
              <div style="color:var(--text-muted); font-size:11px;">STATE</div>
              <strong id="metricState" style="color:var(--brand-primary); font-size:14px;">IDLE</strong>
            </div>
            <div>
              <div style="color:var(--text-muted); font-size:11px;">TARGET FPS</div>
              <strong style="color:var(--status-success); font-size:14px;">25 FPS</strong>
            </div>
            <div>
              <div style="color:var(--text-muted); font-size:11px;">FRAME</div>
              <strong id="metricFrame" style="font-family:monospace; font-size:14px;">0 / 150</strong>
            </div>
            <div>
              <div style="color:var(--text-muted); font-size:11px;">INTERVAL</div>
              <strong style="color:var(--text-secondary); font-size:14px;">40.0 ms</strong>
            </div>
          </div>
        </div>

        <!-- Right: Interactive Controls -->
        <div style="display:flex; flex-direction:column; gap:var(--space-4);">
          <!-- State Controls -->
          <div style="background:var(--bg-surface); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:var(--space-5);">
            <h3 style="font-size:15px; font-weight:700; margin-bottom:var(--space-3);">1. Direct State Control</h3>
            <div style="display:flex; gap:10px;">
              <button id="btnForceIdle" class="btn btn-secondary btn-md" style="flex:1; justify-content:center;">
                ● Force IDLE
              </button>
              <button id="btnForceSpeaking" class="btn btn-primary btn-md" style="flex:1; justify-content:center;">
                🔊 Force SPEAKING
              </button>
            </div>
          </div>

          <!-- Audio & TTS Controls -->
          <div style="background:var(--bg-surface); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:var(--space-5);">
            <h3 style="font-size:15px; font-weight:700; margin-bottom:var(--space-2);">2. TTS Lifecycle Testing</h3>
            <p style="font-size:13px; color:var(--text-secondary); margin-bottom:var(--space-4);">
              Tests automatic switching to SPEAKING on audio start and immediate return to IDLE when speech finishes.
            </p>

            <div style="display:flex; flex-direction:column; gap:10px;">
              <button id="btnPlayLongSpeech" class="btn btn-touch btn-primary" style="justify-content:center; font-size:14px;">
                🗣️ Play Long Clinical Response (> 6s Loop Test)
              </button>
              <button id="btnPlayShortSpeech" class="btn btn-secondary btn-md" style="justify-content:center;">
                👋 Play Short Greeting (Hindi)
              </button>
              <button id="btnPlayShortEnglish" class="btn btn-secondary btn-md" style="justify-content:center;">
                👋 Play Short Greeting (English)
              </button>
              <button id="btnStopSpeech" class="btn btn-outline-danger btn-md" style="justify-content:center;">
                ⏹ Stop Speech Immediately
              </button>
            </div>
          </div>

          <!-- Asset Info Card -->
          <div style="background:var(--bg-surface); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:var(--space-4); font-size:12px; color:var(--text-secondary); line-height:1.6;">
            <div>📁 <strong>Idle Assets:</strong> <code>/avatar/idle/frame-001.webp</code> – <code>frame-150.webp</code> (150 frames)</div>
            <div>📁 <strong>Speaking Assets:</strong> <code>/avatar/speaking/frame-001.webp</code> – <code>frame-150.webp</code> (150 frames)</div>
            <div>⏱ <strong>Source Duration:</strong> 6.0 seconds · <strong>Math:</strong> 150 frames ÷ 6.0s = 25.0 FPS</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initKioskAvatarPreview() {
  avatarInstance = new DoctorAvatar('previewAvatarMount');
  avatarInstance.mount();

  const stateEl = document.getElementById('metricState');
  const frameEl = document.getElementById('metricFrame');

  // Metrics update loop
  metricsInterval = setInterval(() => {
    if (!avatarInstance) return;
    if (stateEl) {
      stateEl.textContent = avatarInstance.state.toUpperCase();
      stateEl.style.color = avatarInstance.state === 'speaking' ? 'var(--brand-primary)' : 'var(--status-teal)';
    }
    if (frameEl) {
      frameEl.textContent = `${avatarInstance.currentFrameIdx + 1} / 150`;
    }
  }, 50);

  // Manual State Toggles
  const btnIdle = document.getElementById('btnForceIdle');
  if (btnIdle) {
    btnIdle.addEventListener('click', () => {
      tts.stop();
      avatarInstance.setState('idle');
    });
  }

  const btnSpeaking = document.getElementById('btnForceSpeaking');
  if (btnSpeaking) {
    btnSpeaking.addEventListener('click', () => {
      avatarInstance.setState('speaking');
    });
  }

  // Audio Testing
  const btnLong = document.getElementById('btnPlayLongSpeech');
  if (btnLong) {
    btnLong.addEventListener('click', () => {
      const longSpeech = "नमस्ते! मैं अखिल भारतीय आयुर्वेद संस्थान में आपका परामर्श चिकित्सक हूँ। कृपया अपनी मुख्य समस्या के बारे में विस्तार से बताएं। क्या आपको सिरदर्द, बुखार, या सांस लेने में कोई परेशानी हो रही है? हम आपकी पूरी केस हिस्ट्री दर्ज कर रहे हैं और जल्द ही आपका ओपीडी टोकन जारी कर दिया जाएगा।";
      tts.speak(longSpeech, 'hi');
    });
  }

  const btnShort = document.getElementById('btnPlayShortSpeech');
  if (btnShort) {
    btnShort.addEventListener('click', () => {
      tts.speak("नमस्ते! आयुष ओपीडी में आपका स्वागत है।", 'hi');
    });
  }

  const btnEnglish = document.getElementById('btnPlayShortEnglish');
  if (btnEnglish) {
    btnEnglish.addEventListener('click', () => {
      tts.speak("Hello! Welcome to All India Institute of Ayurveda OPD reception.", 'en');
    });
  }

  const btnStop = document.getElementById('btnStopSpeech');
  if (btnStop) {
    btnStop.addEventListener('click', () => {
      tts.stop();
      avatarInstance.setState('idle');
    });
  }
}

export function destroyKioskAvatarPreview() {
  tts.stop();
  if (metricsInterval) {
    clearInterval(metricsInterval);
    metricsInterval = null;
  }
  if (avatarInstance) {
    avatarInstance.destroy();
    avatarInstance = null;
  }
}
