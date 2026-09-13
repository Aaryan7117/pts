/**
 * MediKiosk Web — Page 02: Role Selector Hub
 * RetinopathyScan-level role gateway for Kiosk, Patient, Doctor, and IVR Simulator.
 */

export function renderAccountTypePage() {
  return `
    <div style="max-width:1100px; margin:0 auto; padding:var(--space-10) var(--space-6); text-align:center;">
      <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; background:var(--brand-tint); border-radius:var(--radius-full); color:var(--brand-primary); font-size:13px; font-weight:700; margin-bottom:var(--space-3);">
        ✨ Select Your Interaction Portal
      </div>
      <h1 class="text-h1" style="margin-bottom:var(--space-3);">
        Unified Clinical <span style="color:var(--brand-primary);">Intake & Care Hub</span>
      </h1>
      <p class="text-body-lg" style="margin-bottom:var(--space-10); max-width:620px; margin-left:auto; margin-right:auto;">
        Select your portal to interact with MediKiosk AI, track live queue tokens and verified medical records, or manage clinical consultations.
      </p>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:var(--space-6); text-align:left;">
        <!-- Card 1: Kiosk Terminal -->
        <a href="#/kiosk/welcome" class="card card-interactive" style="text-decoration:none; display:flex; flex-direction:column; justify-content:space-between; min-height:280px;">
          <div>
            <div style="width:52px; height:52px; border-radius:var(--radius-lg); background:var(--brand-tint); color:var(--brand-primary); display:flex; align-items:center; justify-content:center; font-size:26px; margin-bottom:var(--space-4);">
              🏥
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
              <h3 class="text-h3" style="color:var(--text-primary);">Physical OPD Kiosk</h3>
              <span class="badge badge-blue">Primary Target</span>
            </div>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.5;">
              Walk-in intake for rural and elderly patients. Features interactive 3D Doctor Avatar, multilingual voice conversation, and prescription scanner.
            </p>
          </div>
          <div style="margin-top:var(--space-6); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; color:var(--brand-primary); font-size:14px;">Launch Kiosk Mode →</span>
            <span class="badge badge-teal">Lobby Station</span>
          </div>
        </a>

        <!-- Card 2: Patient Portal -->
        <a href="#/patient/dashboard" class="card card-interactive" style="text-decoration:none; display:flex; flex-direction:column; justify-content:space-between; min-height:280px;">
          <div>
            <div style="width:52px; height:52px; border-radius:var(--radius-lg); background:#F3E8FF; color:#7E22CE; display:flex; align-items:center; justify-content:center; font-size:26px; margin-bottom:var(--space-4);">
              👤
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
              <h3 class="text-h3" style="color:var(--text-primary);">Patient Health Portal</h3>
              <span class="badge badge-purple">ABHA Citizen</span>
            </div>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.5;">
              Citizens can log in with ABHA ID to view digital health cards, check live OPD token queue position, review doctor-verified prescriptions, and upload documents.
            </p>
          </div>
          <div style="margin-top:var(--space-6); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; color:#7E22CE; font-size:14px;">Open Patient Portal →</span>
            <span class="badge badge-blue">Citizen Access</span>
          </div>
        </a>

        <!-- Card 3: Doctor Workstation -->
        <a href="#/doctor/queue" class="card card-interactive" style="text-decoration:none; display:flex; flex-direction:column; justify-content:space-between; min-height:280px;">
          <div>
            <div style="width:52px; height:52px; border-radius:var(--radius-lg); background:var(--status-warning-tint); color:var(--status-warning); display:flex; align-items:center; justify-content:center; font-size:26px; margin-bottom:var(--space-4);">
              🩺
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
              <h3 class="text-h3" style="color:var(--text-primary);">Doctor Station</h3>
              <span class="badge badge-amber">PIN: 1234</span>
            </div>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.5;">
              Single Pane of Glass where all 3 intake channels converge. 30-second triage synthesis, AYUSH Dashavidha Pariksha, and 1-click verification sign-off.
            </p>
          </div>
          <div style="margin-top:var(--space-6); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; color:var(--status-warning); font-size:14px;">Doctor Login (1234) →</span>
            <span class="badge badge-teal">Chamber 102</span>
          </div>
        </a>

        <!-- Card 4: 2G IVR Telephony Simulator -->
        <a href="#/ivr" class="card card-interactive" style="text-decoration:none; display:flex; flex-direction:column; justify-content:space-between; min-height:280px;">
          <div>
            <div style="width:52px; height:52px; border-radius:var(--radius-lg); background:var(--status-success-tint); color:var(--status-success); display:flex; align-items:center; justify-content:center; font-size:26px; margin-bottom:var(--space-4);">
              📞
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
              <h3 class="text-h3" style="color:var(--text-primary);">2G IVR Studio</h3>
              <span class="badge badge-green">Toll-Free 1800</span>
            </div>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.5;">
              Phone call intake simulator for rural citizens without internet. Tests 4-step location waterfall routing and conversational speech turns.
            </p>
          </div>
          <div style="margin-top:var(--space-6); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; color:var(--status-success); font-size:14px;">Open IVR Simulator ↗</span>
            <span class="badge badge-green">Zero Internet</span>
          </div>
        </a>
      </div>
    </div>
  `;
}
