/**
 * MediKiosk Web — Hash-Based Client Router & Route Guard Manager
 */

import { renderTopbar } from './components/topbar.js';
import { store } from './store.js';

// Import Views
import { renderWelcomePage } from './pages/public/welcome.js';
import { renderAccountTypePage } from './pages/public/account-type.js';
import { renderKioskWelcome, initKioskWelcome, destroyKioskWelcome } from './pages/kiosk/kiosk-welcome.js';
import { renderKioskLanguage, initKioskLanguage } from './pages/kiosk/kiosk-language.js';
import { renderKioskConsent, initKioskConsent } from './pages/kiosk/kiosk-consent.js';
import { renderKioskCareStream, initKioskCareStream } from './pages/kiosk/kiosk-care-stream.js';
import { renderKioskVoiceIntake, initKioskVoiceIntake, destroyKioskVoiceIntake } from './pages/kiosk/kiosk-voice-intake.js';
import { renderKioskExplainBack, initKioskExplainBack } from './pages/kiosk/kiosk-explain-back.js';
import { renderKioskDocScan, initKioskDocScan, destroyKioskDocScan } from './pages/kiosk/kiosk-doc-scan.js';
import { renderKioskOcrResults, initKioskOcrResults } from './pages/kiosk/kiosk-ocr-results.js';
import { renderKioskAyush, initKioskAyush } from './pages/kiosk/kiosk-ayush.js';
import { renderKioskQueueToken, initKioskQueueToken, destroyKioskQueueToken } from './pages/kiosk/kiosk-queue-token.js';
import { renderKioskTriageAlert, initKioskTriageAlert } from './pages/kiosk/kiosk-triage-alert.js';
import { renderDoctorLogin, initDoctorLogin } from './pages/doctor/doctor-login.js';
import { renderDoctorQueue, initDoctorQueue, destroyDoctorQueue } from './pages/doctor/doctor-queue.js';
import { renderDoctorPatient, initDoctorPatient } from './pages/doctor/doctor-patient.js';
import { renderPatientLogin, initPatientLogin } from './pages/patient/patient-login.js';
import { renderPatientDashboard, initPatientDashboard } from './pages/patient/patient-dashboard.js';
import { renderIvrSimulator, initIvrSimulator } from './pages/ivr/ivr-simulator.js';

let currentDestroyFn = null;

export class Router {
  constructor(appElement) {
    this.app = appElement;
    window.addEventListener('hashchange', () => this.handleRoute());
  }

  start() {
    if (!window.location.hash) {
      window.location.hash = '#/welcome';
    } else {
      this.handleRoute();
    }
  }

  handleRoute() {
    // Teardown previous view
    if (currentDestroyFn) {
      currentDestroyFn();
      currentDestroyFn = null;
    }

    const fullHash = window.location.hash.slice(1) || '/welcome';
    const [path] = fullHash.split('?');

    // Route Guards
    if (path.startsWith('/doctor') && path !== '/doctor/login') {
      if (!store.isDoctorAuthenticated()) {
        window.location.hash = '#/doctor/login';
        return;
      }
    }

    // Dynamic Parameter Matching (e.g. /doctor/patient/:id)
    if (path.startsWith('/doctor/patient/')) {
      const encounterId = path.replace('/doctor/patient/', '');
      this._renderView(path, () => renderDoctorPatient(encounterId), () => initDoctorPatient(encounterId));
      return;
    }

    switch (path) {
      // Public
      case '/':
      case '/welcome':
        this._renderView(path, renderWelcomePage);
        break;
      case '/account-type':
        this._renderView(path, renderAccountTypePage);
        break;

      // Kiosk Walk-in Flow
      case '/kiosk/welcome':
        this._renderView(path, renderKioskWelcome, initKioskWelcome, destroyKioskWelcome);
        break;
      case '/kiosk/language':
        this._renderView(path, renderKioskLanguage, initKioskLanguage);
        break;
      case '/kiosk/consent':
        this._renderView(path, renderKioskConsent, initKioskConsent);
        break;
      case '/kiosk/care-stream':
        this._renderView(path, renderKioskCareStream, initKioskCareStream);
        break;
      case '/kiosk/intake':
        this._renderView(path, renderKioskVoiceIntake, initKioskVoiceIntake, destroyKioskVoiceIntake);
        break;
      case '/kiosk/summary':
        this._renderView(path, renderKioskExplainBack, initKioskExplainBack);
        break;
      case '/kiosk/triage':
        this._renderView(path, renderKioskTriageAlert, initKioskTriageAlert);
        break;
      case '/kiosk/documents':
        this._renderView(path, renderKioskDocScan, initKioskDocScan, destroyKioskDocScan);
        break;
      case '/kiosk/ocr-results':
        this._renderView(path, renderKioskOcrResults, initKioskOcrResults);
        break;
      case '/kiosk/ayush':
        this._renderView(path, renderKioskAyush, initKioskAyush);
        break;
      case '/kiosk/queue':
        this._renderView(path, renderKioskQueueToken, initKioskQueueToken, destroyKioskQueueToken);
        break;

      // Doctor Portal
      case '/doctor/login':
        this._renderView(path, renderDoctorLogin, initDoctorLogin);
        break;
      case '/doctor/queue':
        this._renderView(path, renderDoctorQueue, initDoctorQueue, destroyDoctorQueue);
        break;

      // Patient Portal
      case '/patient/login':
        this._renderView(path, renderPatientLogin, initPatientLogin);
        break;
      case '/patient/dashboard':
      case '/patient/queue':
        this._renderView(path, renderPatientDashboard, initPatientDashboard);
        break;

      // IVR Studio
      case '/ivr':
        this._renderView(path, renderIvrSimulator, initIvrSimulator);
        break;

      default:
        window.location.hash = '#/welcome';
        break;
    }
  }

  _renderView(path, renderFn, initFn = null, destroyFn = null) {
    currentDestroyFn = destroyFn;
    this.app.innerHTML = `
      ${renderTopbar(path)}
      <div id="pageContent">${renderFn()}</div>
      <div id="toastContainer" class="toast-container"></div>
    `;

    if (initFn) {
      initFn();
    }
  }
}
