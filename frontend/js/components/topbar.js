/**
 * MediKiosk Web — Unified Institutional Header Component
 */

import { store } from '../store.js';

export function renderTopbar(currentPath) {
  const state = store.getState();
  const isOnline = state.ui.networkOnline;
  const isDoctorAuth = store.isDoctorAuthenticated();
  const isPatientAuth = state.auth.isAuthenticated && state.auth.role === 'patient';
  const patientName = state.auth.user ? state.auth.user.full_name : null;

  return `
    <header class="topbar">
      <!-- Left: Institutional Brand -->
      <a href="#/welcome" class="topbar__brand">
        <div class="topbar__brand-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M2 12h20"></path>
          </svg>
        </div>
        <div>
          <div class="topbar__title">MediKiosk <span style="font-weight:400; color:var(--brand-primary); font-size:14px;">AI</span></div>
          <div class="topbar__subtitle">AIIA New Delhi · AYUSH OPD</div>
        </div>
      </a>

      <!-- Center: Portal Switcher Navigation -->
      <nav class="topbar__portal-nav">
        <a href="#/account-type" class="topbar__portal-btn ${currentPath === '/account-type' ? 'active' : ''}">
          🌐 Role Hub
        </a>
        <a href="#/kiosk/welcome" class="topbar__portal-btn ${currentPath.startsWith('/kiosk') ? 'active' : ''}">
          🏥 OPD Kiosk
        </a>
        <a href="#/patient/dashboard" class="topbar__portal-btn ${currentPath.startsWith('/patient') ? 'active' : ''}">
          👤 Patient Portal
        </a>
        <a href="#/doctor/queue" class="topbar__portal-btn ${currentPath.startsWith('/doctor') ? 'active' : ''}">
          🩺 Doctor Station
        </a>
        <a href="#/ivr" class="topbar__portal-btn ${currentPath.startsWith('/ivr') ? 'active' : ''}">
          📞 2G IVR Studio
        </a>
      </nav>

      <!-- Right: System Status & User Action -->
      <div class="topbar__actions">
        <span class="badge ${isOnline ? 'badge-green' : 'badge-amber'}" title="Backend Connectivity">
          <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:currentColor;"></span>
          ${isOnline ? 'Edge Hub Online' : 'Offline Mode'}
        </span>

        ${isDoctorAuth ? `
          <span class="badge badge-blue">Dr. S. Verma (Cabin 102)</span>
          <button class="btn btn-ghost btn-sm" onclick="window.doctorLogout()">Sign Out</button>
        ` : isPatientAuth ? `
          <span class="badge badge-teal">${patientName || 'Patient'}</span>
          <button class="btn btn-ghost btn-sm" onclick="window.patientLogout()">Sign Out</button>
        ` : `
          <a href="#/account-type" class="btn btn-secondary btn-sm">Select Portal</a>
        `}
      </div>
    </header>
  `;
}

// Global logout handlers
window.doctorLogout = () => {
  store.setDoctorAuthenticated(false);
  window.location.hash = '#/doctor/login';
};

window.patientLogout = () => {
  store.setUser(null);
  window.location.hash = '#/patient/login';
};
