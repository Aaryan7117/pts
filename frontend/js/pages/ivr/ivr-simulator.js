/**
 * MediKiosk Web — Page 44: 2G IVR Phone Call Simulator & Waterfall Diagnostic
 * Demonstrates the non-internet audio telephone intake channel for rural citizens.
 */

import { ivrApi } from '../../api/ivr.api.js';

export function renderIvrSimulator() {
  return `
    <div style="max-width:1100px; margin:0 auto; padding:var(--space-8) var(--space-6);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-6);">
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <h1 class="text-h2">2G IVR Telephony Studio</h1>
            <span class="badge badge-green">Toll-Free 1800-890-AYUSH</span>
          </div>
          <p style="font-size:14px; color:var(--text-secondary); margin-top:2px;">
            Channel 3: Ingesting conversational speech over basic 2G feature phones without internet or smartphones.
          </p>
        </div>

        <a href="#/doctor/queue" target="_blank" class="btn btn-secondary btn-md">
          Open Doctor Workstation Window 2 ↗
        </a>
      </div>

      <div style="display:grid; grid-template-columns:380px 1fr; gap:var(--space-8); align-items:flex-start;">
        <!-- Left Column: Stylized Smartphone / Feature Phone Dialer -->
        <div class="card" style="background:#0F172A; color:#fff; border-radius:var(--radius-2xl); padding:var(--space-6); box-shadow:var(--shadow-xl); border:3px solid #1E293B;">
          <div style="text-align:center; padding-bottom:var(--space-4); border-bottom:1px solid #334155; margin-bottom:var(--space-4);">
            <div style="font-size:11px; text-transform:uppercase; color:#94a3b8;">Inbound Voice Call</div>
            <div style="font-size:18px; font-weight:700; color:#38BDF8; margin-top:2px;">1800-890-AYUSH</div>
            <div id="ivrCallStatusBadge" class="badge badge-amber" style="margin-top:6px;">Idle · Ready to Dial</div>
          </div>

          <!-- Caller Info Fields -->
          <div style="margin-bottom:var(--space-4);">
            <label style="display:block; font-size:11px; text-transform:uppercase; color:#94a3b8; margin-bottom:4px;">Caller Phone Number</label>
            <input type="text" id="ivrCallerPhoneInput" value="9876543210" class="form-input" style="background:#1E293B; border-color:#475569; color:#fff; font-family:var(--font-family-mono);" />
          </div>

          <!-- Phone Keypad Grid -->
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:var(--space-6);">
            ${['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'].map(k => `
              <button class="btn btn-secondary" style="background:#1E293B; border-color:#334155; color:#fff; font-size:18px; font-weight:700; height:50px; border-radius:12px;" onclick="alert('DTMF Tone: ${k}')">
                ${k}
              </button>
            `).join('')}
          </div>

          <!-- Call Action Buttons -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-3);">
            <button id="btnStartIvrCall" class="btn btn-ayush btn-lg" style="justify-content:center; background:#10B981; border:none;">
              📞 Call AI
            </button>
            <button id="btnEndIvrCall" class="btn btn-danger btn-lg" style="justify-content:center;" disabled>
              🔴 End Call
            </button>
          </div>
        </div>

        <!-- Right Column: 4-Step Location Waterfall & Real-Time Call Dialogue -->
        <div style="display:flex; flex-direction:column; gap:var(--space-6);">
          <!-- 4-Step Waterfall Diagnostic Card -->
          <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-3);">
              <h3 class="text-h3" style="font-size:16px;">4-Step Waterfall Location Routing (2ms, Zero GPS)</h3>
              <button id="btnTestWaterfall" class="btn btn-secondary btn-sm">Run Diagnostic Test</button>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:var(--space-3);" id="waterfallStepsContainer">
              <div style="padding:10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
                <div style="font-size:10px; font-weight:700; color:var(--text-muted);">STEP 1: DIALED DID</div>
                <div style="font-size:12px; font-weight:600; color:var(--status-success); margin-top:2px;">Direct Clinic Map</div>
              </div>
              <div style="padding:10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
                <div style="font-size:10px; font-weight:700; color:var(--text-muted);">STEP 2: CITIZEN ABHA</div>
                <div style="font-size:12px; font-weight:600; color:var(--status-success); margin-top:2px;">Home Clinic Match</div>
              </div>
              <div style="padding:10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
                <div style="font-size:10px; font-weight:700; color:var(--text-muted);">STEP 3: DOT MSC CIR</div>
                <div style="font-size:12px; font-weight:600; color:var(--status-success); margin-top:2px;">Telecom Hub Match</div>
              </div>
              <div style="padding:10px; background:var(--bg-surface-soft); border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
                <div style="font-size:10px; font-weight:700; color:var(--text-muted);">STEP 4: NATIONAL DEF</div>
                <div style="font-size:12px; font-weight:600; color:var(--text-muted); margin-top:2px;">AIIA Central OPD</div>
              </div>
            </div>
            <div id="waterfallResultSummary" style="margin-top:var(--space-3); font-size:13px; color:var(--brand-primary); font-weight:600;">
              Assigned Clinic: All India Institute of Ayurveda (AIIA), New Delhi (Confidence: 100%)
            </div>
          </div>

          <!-- Live Telephone Speech Turns Card -->
          <div class="card" style="min-height:300px; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-4); border-bottom:1px solid var(--border-subtle); padding-bottom:var(--space-3);">
              <h3 class="text-h3" style="font-size:16px;">Live Telephone Turn Dialogue</h3>
              <span class="badge badge-teal" id="ivrCallTimer">00:00</span>
            </div>

            <div id="ivrDialogueTranscript" style="flex:1; display:flex; flex-direction:column; gap:var(--space-3); overflow-y:auto;">
              <div style="color:var(--text-muted); font-size:14px; text-align:center; padding:var(--space-6);">
                Dial 1800-890-AYUSH on the left to start an inbound voice call simulation.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initIvrSimulator() {
  const startBtn = document.getElementById('btnStartIvrCall');
  const endBtn = document.getElementById('btnEndIvrCall');
  const phoneInput = document.getElementById('ivrCallerPhoneInput');
  const statusBadge = document.getElementById('ivrCallStatusBadge');
  const transcriptDiv = document.getElementById('ivrDialogueTranscript');
  const timerBadge = document.getElementById('ivrCallTimer');

  let callActive = false;
  let callSeconds = 0;
  let timerInterval = null;

  if (startBtn) {
    startBtn.addEventListener('click', async () => {
      const phone = phoneInput.value.trim() || '9876543210';
      startBtn.disabled = true;
      endBtn.disabled = false;
      callActive = true;
      statusBadge.className = 'badge badge-green';
      statusBadge.textContent = 'Active Call · Connected';

      timerInterval = setInterval(() => {
        callSeconds += 1;
        const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
        const secs = String(callSeconds % 60).padStart(2, '0');
        if (timerBadge) timerBadge.textContent = `${mins}:${secs}`;
      }, 1000);

      // Call backend incoming call
      try {
        await ivrApi.simulateIncomingCall(phone, '1800-890-AYUSH', 'hi');
      } catch (e) {
        console.warn('IVR simulate incoming call fallback:', e);
      }

      transcriptDiv.innerHTML = `
        <div style="padding:10px 14px; background:var(--bg-surface-soft); border-radius:12px; border:1px solid var(--border-subtle);">
          <strong style="color:var(--brand-primary); font-size:12px; text-transform:uppercase;">AI Attendant (AIIA Voice):</strong>
          <p style="font-size:14px; margin-top:2px;">"नमस्ते! अखिल भारतीय आयुर्वेद संस्थान की टेलीफोन सेवा में आपका स्वागत है। आपको क्या परेशानी हो रही है?"</p>
        </div>
      `;

      // Simulate patient answering after 2 seconds
      setTimeout(() => {
        if (!callActive) return;
        transcriptDiv.innerHTML += `
          <div style="padding:10px 14px; background:var(--brand-tint); border-radius:12px; border:1px solid var(--border-brand); align-self:flex-end; max-width:85%;">
            <strong style="color:var(--brand-primary); font-size:12px; text-transform:uppercase;">Citizen (${phone}):</strong>
            <p style="font-size:14px; margin-top:2px;">"नमस्ते, मुझे पिछले 3 दिनों से सीने में दर्द और भारीपन लग रहा है।"</p>
          </div>
        `;
      }, 2000);

      // Simulate AI follow up
      setTimeout(() => {
        if (!callActive) return;
        transcriptDiv.innerHTML += `
          <div style="padding:10px 14px; background:var(--bg-surface-soft); border-radius:12px; border:1px solid var(--border-subtle);">
            <strong style="color:var(--brand-primary); font-size:12px; text-transform:uppercase;">AI Attendant (AIIA Voice):</strong>
            <p style="font-size:14px; margin-top:2px;">"यह गंभीर हो सकता है। आपकी जानकारी डॉ. एस. वर्मा को प्राथमिक आपातकालीन फ्लैग (RED) के साथ भेज दी गई है। आपका टोकन IVR-402 है।"</p>
          </div>
          <div style="padding:8px 12px; background:var(--status-danger-tint); border:1px solid var(--status-danger); border-radius:8px; font-size:12px; color:var(--status-danger); font-weight:700; text-align:center;">
            🚨 PRIORITY CASE CONVERGED TO DOCTOR WORKSTATION (WINDOW 2)
          </div>
        `;
      }, 4500);
    });
  }

  if (endBtn) {
    endBtn.addEventListener('click', () => {
      callActive = false;
      startBtn.disabled = false;
      endBtn.disabled = true;
      statusBadge.className = 'badge badge-amber';
      statusBadge.textContent = 'Call Ended';
      if (timerInterval) clearInterval(timerInterval);
    });
  }
}
