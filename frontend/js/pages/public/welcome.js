/**
 * MediKiosk Web — Page 01: Welcome Landing Screen
 */

export function renderWelcomePage() {
  return `
    <div class="welcome-landing" style="max-width:1200px; margin:0 auto; padding:var(--space-10) var(--space-6); display:grid; grid-template-columns:1.2fr 1fr; gap:var(--space-10); align-items:center; min-height:calc(100vh - var(--header-height) - 80px);">
      <div>
        <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; background:var(--status-ayush-tint, #eaf8f0); border-radius:var(--radius-full); color:var(--status-ayush); font-size:13px; font-weight:700; margin-bottom:var(--space-4);">
          🏥 Ministry of AYUSH / AIIA · SIH26047 Production Solution
        </div>
        <h1 class="text-display" style="margin-bottom:var(--space-4); color:var(--text-primary);">
          Intelligent Clinical <span style="color:var(--text-primary);">Intake & Patient Care</span>
        </h1>
        <p class="text-body-lg" style="margin-bottom:var(--space-8); max-width:540px;">
          Empowering public hospital OPDs with multimodal AI: natural voice history in 5 Indian languages, prescription OCR with verifiable line-level evidence, and a single pane of glass doctor workstation.
        </p>

        <div style="display:flex; flex-wrap:wrap; gap:var(--space-4); margin-bottom:var(--space-10);">
          <a href="#/account-type" class="btn btn-primary btn-touch">
            Launch Portal Hub →
          </a>
          <a href="#/kiosk/welcome" class="btn btn-secondary btn-touch">
            🏥 OPD Kiosk Terminal
          </a>
        </div>

        <div style="display:grid; grid-template-columns:1fr; gap:var(--space-4); border-top:1px solid var(--border-default); padding-top:var(--space-6);">
          <div>
            <strong style="color:var(--brand-dark); font-size:18px; display:block;">3 Intake Channels</strong>
            <span style="font-size:13px; color:var(--text-muted);">In-Clinic Kiosk, Mobile BYOD & 2G IVR</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Visual Showcase -->
      <div>
        <div class="welcome-landing__showcase" style="padding:var(--space-8); text-align:center;">
          <div class="welcome-landing__icon" aria-hidden="true">
            <img src="/aiia-seal.png" alt="" class="welcome-landing__aiia-seal" width="88" height="88" />
          </div>
          <h3 class="text-h3" style="margin-bottom:var(--space-2);">All India Institute of Ayurveda</h3>
          <p style="font-size:14px; color:var(--text-secondary); margin-bottom:var(--space-6);">
            Hospital OPD Waiting Lobby · Autonomous Intake Terminal
          </p>

          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:var(--radius-lg); padding:var(--space-4); text-align:left; display:flex; flex-direction:column; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:12px; font-weight:700; color:var(--brand-dark);">QUICK ACCESS CREDENTIALS</span>
              <span class="badge badge-green">Ready</span>
            </div>
            <div style="font-size:13px;">🩺 <strong>Doctor Station:</strong> PIN <code>1234</code></div>
            <div style="font-size:13px;">👤 <strong>Patient Portal:</strong> Mobile <code>9876543210</code> / <code>patient123</code></div>
            <div style="font-size:13px;">🏥 <strong>Kiosk Mode:</strong> 1-Tap Walk-In (No login required)</div>
          </div>
        </div>

        <div class="welcome-landing__video-wrap">
          <video
            class="welcome-landing__video"
            src="/home_page_video.mp4"
            autoplay
            muted
            loop
            playsinline
            controls
            aria-label="MediKiosk home page overview video"
          ></video>
        </div>
      </div>
    </div>
  `;
}
