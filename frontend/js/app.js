/**
 * MediKiosk — Main Application (SPA Router + Screen Controller)
 *
 * Manages screen transitions, global state, and wires up all UI interactions.
 */
import { api } from './api.js';
import { AudioRecorder, WaveformVisualizer, playAudioBase64, playDing } from './audio.js';
import { CameraCapture } from './camera.js';
import { DoctorScene } from './three/scene.js';
import { DoctorCharacter } from './three/doctor.js';

// ── Global State ──
const state = {
  currentScreen: 'welcome',
  encounterId: null,
  patientId: null,
  tokenNumber: null,
  sessionId: null,
  language: 'en',
  isRecording: false,
  isOnline: false,
  facts: [],
  doctorAuthenticated: false,
  selectedEncounterId: null,
};

// ── 3D Doctor ──
let doctorScene = null;
let doctor = null;
let doctorAnimFrame = null;

// ── Audio ──
const recorder = new AudioRecorder();
let waveformViz = null;

// ── Camera ──
let camera = null;

// ── Queue polling ──
let queuePollInterval = null;

// ============================================================
//  INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  initDoctor();
  initWelcomeScreen();
  initVoiceScreen();
  initScanScreen();
  initQueueScreen();
  initDoctorDashboard();
  initPinModal();
  checkHealth();
});

// ============================================================
//  3D DOCTOR AVATAR
// ============================================================

function initDoctor() {
  const container = document.getElementById('doctorContainerWelcome');
  if (!container) return;

  doctorScene = new DoctorScene(container);
  doctor = new DoctorCharacter();
  doctor.addToScene(doctorScene.scene);

  // Custom update loop for procedural animations
  function updateDoctor() {
    doctorAnimFrame = requestAnimationFrame(updateDoctor);
    const delta = doctorScene.clock.getDelta();
    doctor.update(delta);
  }
  updateDoctor();

  // Start directly with the pointing pose directing patient to microphone
  doctor.setState('point');
}

function moveDoctorToPip() {
  if (!doctorScene) return;
  const pipContainer = document.getElementById('doctorContainerPip');
  if (!pipContainer) return;

  // Move the renderer canvas to PiP container
  const canvas = doctorScene.renderer.domElement;
  pipContainer.appendChild(canvas);
  doctorScene.container = pipContainer;
  doctorScene.setPipMode();
  doctorScene.resize();
}

function moveDoctorToHero() {
  if (!doctorScene) return;
  const heroContainer = document.getElementById('doctorContainerWelcome');
  if (!heroContainer) return;

  const canvas = doctorScene.renderer.domElement;
  heroContainer.appendChild(canvas);
  doctorScene.container = heroContainer;
  doctorScene.setHeroMode();
  doctorScene.resize();
}

// ============================================================
//  SCREEN ROUTER
// ============================================================

function navigateTo(screen) {
  const currentEl = document.getElementById(`screen${capitalize(state.currentScreen)}`);
  const nextEl = document.getElementById(`screen${capitalize(screen)}`);

  if (currentEl) {
    currentEl.classList.remove('active');
    currentEl.classList.add('exiting');
    setTimeout(() => currentEl.classList.remove('exiting'), 500);
  }

  if (nextEl) {
    nextEl.classList.add('active');
  }

  // Status bar visibility
  const statusBar = document.getElementById('statusBar');
  statusBar.style.display = (screen === 'welcome' || screen === 'doctor') ? 'none' : 'flex';

  // Token badge
  const tokenBadge = document.getElementById('tokenBadge');
  if (state.tokenNumber) {
    tokenBadge.textContent = `🎫 ${state.tokenNumber}`;
    tokenBadge.style.display = 'inline-flex';
  }

  state.currentScreen = screen;

  // Screen-specific setup
  if (screen === 'voice') {
    moveDoctorToPip();
    doctor?.setState('listen');
  } else if (screen === 'welcome') {
    moveDoctorToHero();
    doctor?.setState('wave');
    setTimeout(() => doctor?.setState('point'), 2500);
  }
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ============================================================
//  HEALTH CHECK
// ============================================================

async function checkHealth() {
  try {
    const data = await api.health();
    state.isOnline = data.network === 'ONLINE';
    updateNetworkBadge();
  } catch {
    state.isOnline = false;
    updateNetworkBadge();
  }
}

function updateNetworkBadge() {
  const badge = document.getElementById('networkBadge');
  if (state.isOnline) {
    badge.className = 'badge badge-online';
    badge.textContent = 'Online';
  } else {
    badge.className = 'badge badge-offline';
    badge.textContent = 'Offline';
  }
}

// ============================================================
//  SCREEN 1: WELCOME
// ============================================================

function initWelcomeScreen() {
  const micBtn = document.getElementById('welcomeMicBtn');
  const typeBtn = document.getElementById('welcomeTypeBtn');
  const loginBtn = document.getElementById('doctorLoginBtn');
  const langPills = document.querySelectorAll('#welcomeLangPills .lang-pill');
  const micLabel = document.getElementById('welcomeMicLabel');

  const langLabels = {
    en: 'Tap to speak in English',
    hi: 'हिंदी में बोलने के लिए माइक दबाएं',
    ta: 'தமிழில் பேச தொடவும்',
    te: 'తెలుగులో మాట్లాడటానికి నొక్కండి',
    mr: 'मराठीत बोलण्यासाठी टॅप करा'
  };

  langPills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      e.stopPropagation();
      const chosenLang = pill.dataset.lang;
      state.language = chosenLang;
      langPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      if (micLabel) micLabel.textContent = langLabels[chosenLang] || 'Tap to speak';
    });
  });

  async function startIntakeSession(openKeyboard = false) {
    playDing();
    try {
      micBtn.disabled = true;
      if (typeBtn) typeBtn.disabled = true;

      const data = await api.bootstrap(state.language, 'kiosk');
      state.encounterId = data.encounter_id;
      state.patientId = data.patient_id;
      state.tokenNumber = data.token_number;

      // Start call session
      const callData = await api.startCall(data.encounter_id, state.language);
      state.sessionId = callData.session_id;

      // Navigate to voice intake
      navigateTo('voice');

      // Play opening question
      if (callData.opening_audio_base64) {
        doctor?.setState('talk');
        await playAudioBase64(callData.opening_audio_base64);
        doctor?.setState('listen');
      }

      addChatBubble('doctor', callData.opening_text || 'How can I help you today?');

      if (openKeyboard) {
        showKeyboardDrawer();
      } else {
        await startRecording();
      }
    } catch (err) {
      console.error('Bootstrap failed:', err);
      micBtn.disabled = false;
      if (typeBtn) typeBtn.disabled = false;
      alert('Could not start intake. Is the backend running?');
    }
  }

  micBtn.addEventListener('click', () => startIntakeSession(false));
  if (typeBtn) {
    typeBtn.addEventListener('click', () => startIntakeSession(true));
  }

  loginBtn.addEventListener('click', () => {
    showPinModal();
  });
}

// ============================================================
//  SCREEN 2: VOICE INTAKE
// ============================================================

function initVoiceScreen() {
  const micBtn = document.getElementById('voiceMicBtn');
  const finishBtn = document.getElementById('voiceFinishBtn');
  const typeToggleBtn = document.getElementById('voiceTypeToggleBtn');
  const sendBtn = document.getElementById('keyboardSendBtn');
  const closeBtn = document.getElementById('keyboardCloseBtn');
  const input = document.getElementById('keyboardInput');

  micBtn.addEventListener('click', () => {
    hideKeyboardDrawer();
    if (state.isRecording) {
      stopRecordingAndProcess();
    } else {
      startRecording();
    }
  });

  if (typeToggleBtn) {
    typeToggleBtn.addEventListener('click', () => {
      toggleKeyboardDrawer();
    });
  }

  if (sendBtn && input) {
    sendBtn.addEventListener('click', submitTextTurn);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') submitTextTurn();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', hideKeyboardDrawer);
  }

  finishBtn.addEventListener('click', async () => {
    if (state.isRecording) {
      await recorder.stop();
      state.isRecording = false;
    }
    waveformViz?.stop();
    hideKeyboardDrawer();

    try {
      updateVoiceStatus('Finishing intake...');
      const result = await api.endCall(state.sessionId);
      state.tokenNumber = result.assigned_token;

      doctor?.setState('idle');

      // Navigate to scan screen
      navigateTo('scan');
    } catch (err) {
      console.error('End call failed:', err);
      updateVoiceStatus('Error finishing intake');
    }
  });

  // Init waveform visualizer
  const canvas = document.getElementById('waveformCanvas');
  waveformViz = new WaveformVisualizer(canvas);

  // Wire Voice Activity Detection (VAD) auto-submit on silence
  recorder.onSpeechEnd = () => {
    if (state.isRecording) {
      console.log('VAD: Speech ended, auto-processing turn...');
      updateVoiceStatus('Detected silence. Processing response...');
      stopRecordingAndProcess();
    }
  };
}

function showKeyboardDrawer() {
  const drawer = document.getElementById('keyboardDrawer');
  if (drawer) {
    drawer.style.display = 'block';
    const input = document.getElementById('keyboardInput');
    input?.focus();
    updateVoiceStatus('Type your message and click Send');
  }
}

function hideKeyboardDrawer() {
  const drawer = document.getElementById('keyboardDrawer');
  if (drawer) drawer.style.display = 'none';
}

function toggleKeyboardDrawer() {
  const drawer = document.getElementById('keyboardDrawer');
  if (drawer?.style.display === 'none' || !drawer?.style.display) {
    showKeyboardDrawer();
  } else {
    hideKeyboardDrawer();
  }
}

async function startRecording() {
  try {
    await recorder.start();
    state.isRecording = true;

    const micBtn = document.getElementById('voiceMicBtn');
    micBtn.classList.add('recording');

    waveformViz?.start(recorder);
    doctor?.setState('listen');
    updateVoiceStatus('Listening... Speak naturally (auto-submits when done)');
  } catch (err) {
    console.error('Mic access denied:', err);
    updateVoiceStatus('Microphone access denied. You can use the keyboard below to type.');
    showKeyboardDrawer();
  }
}

async function stopRecordingAndProcess() {
  const audioBlob = await recorder.stop();
  state.isRecording = false;

  const micBtn = document.getElementById('voiceMicBtn');
  micBtn.classList.remove('recording');
  waveformViz?.stop();

  if (!audioBlob) return;

  updateVoiceStatus('Processing your response...');
  doctor?.setState('idle');

  try {
    const result = await api.audioTurn(state.sessionId, audioBlob);
    await handleTurnResult(result);
  } catch (err) {
    console.error('Audio turn failed:', err);
    updateVoiceStatus('Error processing audio. Try speaking again or type.');
    await startRecording();
  }
}

async function submitTextTurn() {
  const input = document.getElementById('keyboardInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  if (state.isRecording) {
    await recorder.stop();
    state.isRecording = false;
    document.getElementById('voiceMicBtn')?.classList.remove('recording');
    waveformViz?.stop();
  }

  input.value = '';
  updateVoiceStatus('Processing your message...');
  doctor?.setState('idle');

  try {
    const result = await api.textTurn(state.sessionId, text);
    await handleTurnResult(result);
  } catch (err) {
    console.error('Text turn failed:', err);
    updateVoiceStatus('Error sending message. Please try again.');
  }
}

async function handleTurnResult(result) {
  // Show patient transcript
  addChatBubble('patient', result.patient_transcript);

  // Add extracted facts
  for (const fact of result.extracted_facts) {
    addFactCard(fact);
  }

  // Update language if detected
  if (result.detected_language) {
    state.language = result.detected_language;
  }

  // If there's a next question, display and play it
  if (result.next_question_text) {
    addChatBubble('doctor', result.next_question_text);
    doctor?.setState('talk');

    if (result.next_question_audio_base64) {
      await playAudioBase64(result.next_question_audio_base64);
    }

    doctor?.setState('listen');

    // Auto-resume recording if interview continues and keyboard is not active
    const drawer = document.getElementById('keyboardDrawer');
    if (!result.is_completed && (!drawer || drawer.style.display === 'none')) {
      await startRecording();
    } else if (!result.is_completed) {
      updateVoiceStatus('Type your next answer or tap mic to speak');
    }
  }

  if (result.is_completed) {
    hideKeyboardDrawer();
    updateVoiceStatus('Intake complete! Moving to prescription scan...');
    doctor?.setState('idle');
    setTimeout(() => navigateTo('scan'), 2000);
  }

  // Doctor nods when clinical facts are recognized
  if (result.extracted_facts.length > 0) {
    doctor?.setState('nod');
    setTimeout(() => {
      if (!state.isRecording && !result.is_completed) doctor?.setState('listen');
    }, 1500);
  }
}

function addChatBubble(sender, text) {
  const area = document.getElementById('conversationArea');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${sender}`;
  bubble.textContent = text;
  area.appendChild(bubble);
  area.scrollTop = area.scrollHeight;
}

function addFactCard(fact) {
  state.facts.push(fact);

  const scroll = document.getElementById('factsScroll');
  const card = document.createElement('div');
  card.className = 'fact-card';

  const categoryIcons = {
    chief_complaint: '🩺',
    symptom: '🤒',
    medication: '💊',
    allergy: '⚠️',
    history: '📋',
    ayush: '🌿',
    lab_result: '🧪',
    vital: '❤️',
  };

  const icon = categoryIcons[fact.category] || '📌';
  card.innerHTML = `
    <div class="fact-card__category">${icon} ${fact.category?.replace('_', ' ')}</div>
    <div class="fact-card__value">${fact.concept || fact.field}</div>
    <div class="fact-card__meta">${Math.round((fact.confidence || 0) * 100)}% • ${fact.provenance || ''}</div>
  `;
  scroll.appendChild(card);
  scroll.scrollLeft = scroll.scrollWidth;

  // Update count
  document.getElementById('factsCount').textContent = `${state.facts.length} facts`;
}

function updateVoiceStatus(text) {
  document.getElementById('voiceStatus').textContent = text;
}

// ============================================================
//  SCREEN 3: SCAN PRESCRIPTION
// ============================================================

function initScanScreen() {
  const captureBtn = document.getElementById('captureBtn');
  const skipBtn = document.getElementById('scanSkipBtn');
  const doneBtn = document.getElementById('scanDoneBtn');
  const uploadBtn = document.getElementById('uploadFileBtn');
  const fileInput = document.getElementById('prescriptionFileInput');

  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async () => {
      const file = fileInput.files?.[0];
      if (!file) return;
      uploadBtn.disabled = true;
      uploadBtn.textContent = '⏳ Processing Prescription...';
      try {
        const result = await api.uploadDocument(state.encounterId, file);
        showScanResults(result);
        camera?.stop();
      } catch (err) {
        console.error('File upload failed:', err);
        alert('Failed to process prescription image: ' + err.message);
      } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = '📁 Upload Prescription Image';
      }
    });
  }

  captureBtn.addEventListener('click', async () => {
    if (!camera?.stream) {
      camera = new CameraCapture(document.getElementById('cameraVideo'));
      try {
        await camera.start();
      } catch (e) {
        alert('Camera could not be accessed. Please click "Upload Prescription Image" below.');
        return;
      }
    }

    captureBtn.disabled = true;
    try {
      const imageBlob = await camera.capture();
      const result = await api.uploadDocument(state.encounterId, imageBlob);
      showScanResults(result);
      camera.stop();
    } catch (err) {
      console.error('Document capture/upload failed:', err);
      alert('Could not capture clear image: ' + err.message + '. Please use the Upload button below.');
    } finally {
      captureBtn.disabled = false;
    }
  });

  skipBtn.addEventListener('click', () => {
    camera?.stop();
    navigateTo('queue');
    startQueuePolling();
  });

  doneBtn.addEventListener('click', () => {
    camera?.stop();
    navigateTo('queue');
    startQueuePolling();
  });

  // Auto-start camera when scan screen becomes active
  const observer = new MutationObserver(() => {
    const scanScreen = document.getElementById('screenScan');
    if (scanScreen.classList.contains('active') && !camera) {
      camera = new CameraCapture(document.getElementById('cameraVideo'));
      camera.start().catch((err) => {
        console.warn('Auto camera start skipped or blocked:', err);
      });
    }
  });
  observer.observe(document.getElementById('screenScan'), { attributes: true, attributeFilter: ['class'] });
}

function showScanResults(result) {
  const resultsPanel = document.getElementById('scanResults');
  const medsList = document.getElementById('scanMedsList');
  const alertsDiv = document.getElementById('scanAlerts');
  const evidenceDiv = document.getElementById('scanEvidence');
  const doneBtn = document.getElementById('scanDoneBtn');

  resultsPanel.style.display = 'block';
  doneBtn.style.display = 'inline-flex';

  // Medications
  medsList.innerHTML = '';
  if (result.extracted_medications?.length) {
    for (const med of result.extracted_medications) {
      const item = document.createElement('div');
      item.className = 'scan-screen__med-item';
      item.innerHTML = `
        <span>💊</span>
        <div>
          <div class="scan-screen__med-name">${med.name}</div>
          <div class="scan-screen__med-dose">${med.dose || ''} ${med.frequency || ''}</div>
        </div>
        <span class="badge badge-teal">${Math.round((med.confidence || 0) * 100)}%</span>
      `;
      medsList.appendChild(item);
    }
  } else {
    medsList.innerHTML = '<div class="empty-state"><span>No medications detected</span></div>';
  }

  // Drug interaction alerts
  alertsDiv.innerHTML = '';
  if (result.flagged_interactions?.length) {
    for (const alert of result.flagged_interactions) {
      const severity = alert.severity === 'CRITICAL' ? 'danger' : 'warning';
      const icon = alert.severity === 'CRITICAL' ? '🔴' : '⚠️';
      const el = document.createElement('div');
      el.className = `alert alert-${severity}`;
      el.innerHTML = `
        <div class="alert__icon">${icon}</div>
        <div class="alert__content">
          <div class="alert__title">${alert.severity} Drug Interaction</div>
          <div class="alert__text">${alert.warning}</div>
        </div>
      `;
      alertsDiv.appendChild(el);
    }
  }

  // Evidence image
  if (result.highlighted_image_url) {
    evidenceDiv.innerHTML = `<img src="${result.highlighted_image_url}" alt="Evidence-boxed prescription" />`;
  }
}

// ============================================================
//  SCREEN 4: QUEUE STATUS
// ============================================================

function initQueueScreen() {
  document.getElementById('queueNewBtn').addEventListener('click', () => {
    stopQueuePolling();
    resetState();
    navigateTo('welcome');
  });
}

function startQueuePolling() {
  updateQueueDisplay();
  queuePollInterval = setInterval(updateQueueDisplay, 10000);
}

function stopQueuePolling() {
  if (queuePollInterval) {
    clearInterval(queuePollInterval);
    queuePollInterval = null;
  }
}

async function updateQueueDisplay() {
  if (!state.tokenNumber) return;

  try {
    const data = await api.queueStatus(state.tokenNumber);
    document.getElementById('queueToken').textContent = data.token;
    document.getElementById('queuePosition').textContent = data.patients_ahead;
    document.getElementById('queueWait').textContent =
      data.estimated_wait_minutes > 0
        ? `~${data.estimated_wait_minutes} min estimated wait`
        : 'You\'re next!';

    const statusBadge = document.getElementById('queueStatusBadge');
    if (data.status === 'CALLED') {
      statusBadge.innerHTML = '<span class="badge badge-green" style="font-size: var(--text-lg); padding: var(--space-3) var(--space-6);">✅ CALLED — Please proceed to the doctor</span>';
      stopQueuePolling();
    } else {
      statusBadge.innerHTML = '<span class="badge badge-yellow">⏳ WAITING</span>';
    }
  } catch (err) {
    console.error('Queue poll failed:', err);
  }
}

// ============================================================
//  SCREEN 5: DOCTOR DASHBOARD
// ============================================================

function initDoctorDashboard() {
  const callNextBtn = document.getElementById('callNextBtn');
  const exitBtn = document.getElementById('doctorExitBtn');

  if (exitBtn) {
    exitBtn.addEventListener('click', () => {
      navigateTo('welcome');
    });
  }

  callNextBtn.addEventListener('click', async () => {
    let targetEncounterId = state.selectedEncounterId;
    if (!targetEncounterId) {
      const firstEntry = document.querySelector('.queue-entry');
      if (firstEntry) {
        firstEntry.click();
        targetEncounterId = state.selectedEncounterId;
      }
    }

    if (!targetEncounterId) {
      alert('No patients waiting in queue.');
      return;
    }

    try {
      callNextBtn.textContent = '📢 Calling Patient...';
      callNextBtn.disabled = true;
      playDing();
      await api.callNext(targetEncounterId);
      callNextBtn.textContent = '✓ Patient Called to Room 102';
      setTimeout(() => {
        callNextBtn.textContent = '▶ Call Next Patient';
        callNextBtn.disabled = false;
        loadDoctorQueue();
      }, 2500);
    } catch (err) {
      console.error('Call next failed:', err);
      callNextBtn.textContent = '▶ Call Next Patient';
      callNextBtn.disabled = false;
    }
  });
}

async function loadDoctorQueue() {
  try {
    const data = await api.doctorQueue();
    const list = document.getElementById('doctorQueueList');
    const totalBadge = document.getElementById('queueTotalBadge');
    totalBadge.textContent = data.total_waiting;

    if (!data.queue?.length) {
      list.innerHTML = '<div class="empty-state"><div class="empty-state__icon">📋</div><div class="empty-state__text">No patients in queue</div></div>';
      return;
    }

    list.innerHTML = '';
    for (const entry of data.queue) {
      const el = document.createElement('div');
      el.className = 'queue-entry';
      if (entry.encounter_id === state.selectedEncounterId) {
        el.classList.add('selected');
      }

      const severityClass = entry.severity_badge === 'RED' ? 'badge-red'
        : entry.severity_badge === 'YELLOW' ? 'badge-yellow' : 'badge-green';
      const severityIcon = entry.severity_badge === 'RED' ? '🔴 CRITICAL'
        : entry.severity_badge === 'YELLOW' ? '⚠️ MODERATE' : '✅ ROUTINE';

      el.innerHTML = `
        <div class="queue-entry__token">${entry.token_number}</div>
        <div class="queue-entry__summary">
          <div class="queue-entry__text">${entry.summary_30_words}</div>
          <div class="queue-entry__facts">${entry.fact_count} facts • ${entry.channel}</div>
        </div>
        <div>
          <span class="badge ${severityClass}">${severityIcon}</span>
          ${entry.has_medication_conflict ? '<span class="badge badge-red" style="margin-top: 4px;">💊 Conflict</span>' : ''}
        </div>
      `;

      el.addEventListener('click', () => {
        state.selectedEncounterId = entry.encounter_id;
        list.querySelectorAll('.queue-entry').forEach(e => e.classList.remove('selected'));
        el.classList.add('selected');
        loadPatientDetail(entry.encounter_id);
      });

      list.appendChild(el);
    }

    // Auto-select first patient if none selected
    if (data.queue.length > 0 && (!state.selectedEncounterId || !data.queue.some(q => q.encounter_id === state.selectedEncounterId))) {
      state.selectedEncounterId = data.queue[0].encounter_id;
      const firstCard = list.querySelector('.queue-entry');
      firstCard?.classList.add('selected');
      loadPatientDetail(data.queue[0].encounter_id);
    }
  } catch (err) {
    console.error('Load queue failed:', err);
  }
}

async function loadPatientDetail(encounterId) {
  const mainPanel = document.getElementById('doctorMain');

  try {
    mainPanel.innerHTML = '<div class="empty-state"><div class="spinner spinner-lg"></div><div>Loading patient data...</div></div>';
    const data = await api.patientDetail(encounterId);

    const enc = data.encounter;
    const severityClass = enc.severity_badge === 'RED' ? 'badge-red'
      : enc.severity_badge === 'YELLOW' ? 'badge-yellow' : 'badge-green';
    const severityLabel = enc.severity_badge === 'RED' ? '🔴 CRITICAL'
      : enc.severity_badge === 'YELLOW' ? '⚠️ MODERATE' : '✅ ROUTINE';

    let html = `
      <div class="doctor-screen__patient-header">
        <div>
          <div class="doctor-screen__patient-name">
            Patient ${enc.token_number}
            <span class="badge ${severityClass}" style="margin-left: 8px;">${severityLabel}</span>
          </div>
          <div style="color: var(--text-secondary); font-size: var(--text-sm); margin-top: 4px;">
            ${enc.channel} • Language: ${enc.language?.toUpperCase() || 'EN'} • Registered: ${enc.created_at || ''}
          </div>
        </div>
      </div>
    `;

    // Clinical Summary Banner
    const summaryText = enc.summary_text || enc.summary_30_words || 'Intake in progress via Kiosk.';
    html += `
      <div class="card" style="margin-bottom: var(--space-4); background: var(--accent-light); border-left: 4px solid var(--accent); padding: var(--space-4);">
        <div style="font-size: var(--text-xs); font-weight: 700; color: var(--accent-dark); text-transform: uppercase; margin-bottom: 4px;">
          📋 30-Second Clinical Triage Summary
        </div>
        <div style="font-size: var(--text-base); color: var(--text-primary); font-weight: 500;">
          ${summaryText}
        </div>
      </div>
    `;

    // Drug interaction alerts
    if (data.drug_interaction_alerts?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">🔴 Drug Interaction Alerts</div><div class="doctor-screen__alerts-list">';
      for (const alert of data.drug_interaction_alerts) {
        const sev = alert.severity === 'CRITICAL' ? 'danger' : 'warning';
        const icon = alert.severity === 'CRITICAL' ? '🔴' : '⚠️';
        html += `
          <div class="alert alert-${sev}">
            <div class="alert__icon">${icon}</div>
            <div class="alert__content">
              <div class="alert__title">${alert.drugs_involved?.join(' + ') || alert.severity} Interaction</div>
              <div class="alert__text">${alert.warning}</div>
              <div style="font-size: var(--text-xs); margin-top: 4px; opacity: 0.7;">Source: ${alert.source || 'Clinical Database'}</div>
            </div>
          </div>
        `;
      }
      html += '</div></div>';
    }

    // Clinical gap alerts
    if (data.clinical_gap_alerts?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">🔍 Clinical Gaps Detected</div><div class="doctor-screen__alerts-list">';
      for (const gap of data.clinical_gap_alerts) {
        html += `
          <div class="alert alert-warning">
            <div class="alert__icon">🔍</div>
            <div class="alert__content">
              <div class="alert__title">${gap.missing_question}</div>
              <div class="alert__text">${gap.clinical_rationale}</div>
            </div>
          </div>
        `;
      }
      html += '</div></div>';
    }

    // Extracted Clinical Facts
    if (data.clinical_facts?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">🩺 Extracted Clinical Facts (' + data.clinical_facts.length + ')</div><div class="doctor-screen__facts-grid">';
      for (const fact of data.clinical_facts) {
        const catIcons = {
          chief_complaint: '🎯',
          symptom: '🤒',
          medication: '💊',
          allergy: '⚠️',
          vital: '💓',
          ayush_agni: '🔥',
          ayush_prakriti: '🌿',
          ayush_ahara: '🥗'
        };
        const catIcon = catIcons[fact.category] || '📌';
        const isNegated = fact.is_negated ? '<span class="badge badge-red" style="margin-left: 6px;">❌ Denied</span>' : '';
        const confPercent = Math.round((fact.confidence || 0) * 100);
        const conceptDisplay = fact.normalized_concept || fact.value || fact.field;
        const codeDisplay = fact.concept_code ? `<span class="badge badge-teal" style="font-size: 11px;">${fact.concept_code}</span>` : '';

        html += `
          <div class="doctor-fact-card">
            <div class="doctor-fact-card__header">
              <span class="doctor-fact-card__category">${catIcon} ${fact.category?.replace('_', ' ')}</span>
              ${codeDisplay}
            </div>
            <div class="doctor-fact-card__value">${conceptDisplay} ${isNegated}</div>
            ${fact.patient_words ? `<div class="doctor-fact-card__words">"${fact.patient_words}"</div>` : ''}
            <div class="doctor-fact-card__meta">
              <span>Confidence: ${confPercent}%</span>
              <span>•</span>
              <span>Tier: ${fact.provenance_tier || 'VOICE'}</span>
            </div>
          </div>
        `;
      }
      html += '</div></div>';
    } else {
      html += `
        <div class="doctor-screen__section">
          <div class="card" style="padding: var(--space-4); text-align: center; color: var(--text-muted);">
            ℹ️ No clinical facts recorded for this encounter yet.
          </div>
        </div>
      `;
    }

    // Lab result alerts
    if (data.lab_result_alerts?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">🧪 Lab Results</div><div class="doctor-screen__alerts-list">';
      for (const lab of data.lab_result_alerts) {
        const labSev = lab.is_critical ? 'danger' : lab.is_abnormal ? 'warning' : 'info';
        html += `
          <div class="alert alert-${labSev}">
            <div class="alert__content">
              <div class="alert__title">${lab.test_name}: ${lab.value} ${lab.unit || ''}</div>
              <div class="alert__text">${lab.interpretation || ''}</div>
            </div>
          </div>
        `;
      }
      html += '</div></div>';
    }

    // Medication timeline
    if (data.medication_timeline?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">💊 Medication Timeline</div><div class="doctor-screen__facts-grid">';
      for (const med of data.medication_timeline) {
        const statusColor = med.temporal_state === 'stopped' ? 'severity-red' : 'accent';
        html += `
          <div class="card">
            <div style="font-weight: 600; color: var(--${statusColor});">${med.medication}</div>
            <div style="font-size: var(--text-sm); color: var(--text-secondary);">
              ${med.dose || ''} ${med.frequency || ''}<br/>
              Status: ${med.temporal_state || 'active'}
            </div>
          </div>
        `;
      }
      html += '</div></div>';
    }

    // Documents with evidence images
    if (data.documents?.length) {
      html += '<div class="doctor-screen__section"><div class="doctor-screen__section-title">📄 Uploaded Documents</div>';
      for (const doc of data.documents) {
        if (doc.highlighted_path) {
          const imgUrl = `/static/evidence/${doc.id}-boxed.jpg`;
          html += `
            <div class="doctor-screen__evidence-container" style="margin-bottom: var(--space-4);">
              <img src="${imgUrl}" alt="Evidence-boxed prescription" loading="lazy" />
            </div>
          `;
        }
        if (doc.ocr_raw_text) {
          html += `
            <div class="card" style="margin-bottom: var(--space-3);">
              <div style="font-size: var(--text-xs); font-weight: 600; color: var(--text-muted); margin-bottom: 4px;">RAW OCR TEXT</div>
              <div style="font-size: var(--text-sm); white-space: pre-wrap; font-family: var(--font-mono);">${doc.ocr_raw_text}</div>
            </div>
          `;
        }
      }
      html += '</div>';
    }

    mainPanel.innerHTML = html;
  } catch (err) {
    console.error('Load patient detail failed:', err);
    mainPanel.innerHTML = '<div class="empty-state"><div class="empty-state__icon">❌</div><div class="empty-state__text">Failed to load patient data</div></div>';
  }
}

// ============================================================
//  PIN MODAL
// ============================================================

function initPinModal() {
  const overlay = document.getElementById('pinModal');
  const inputs = document.querySelectorAll('.pin-digit');
  const submitBtn = document.getElementById('pinSubmitBtn');
  const cancelBtn = document.getElementById('pinCancelBtn');
  const errorEl = document.getElementById('pinError');

  // Auto-focus next input
  inputs.forEach((input, i) => {
    input.addEventListener('input', () => {
      if (input.value && i < inputs.length - 1) {
        inputs[i + 1].focus();
      }
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && i > 0) {
        inputs[i - 1].focus();
      }
    });
  });

  submitBtn.addEventListener('click', async () => {
    const pin = Array.from(inputs).map(i => i.value).join('');
    if (pin.length !== 4) return;

    try {
      errorEl.style.display = 'none';
      await api.doctorAuth(pin);
      state.doctorAuthenticated = true;
      hidePinModal();
      navigateTo('doctor');
      loadDoctorQueue();
    } catch {
      errorEl.style.display = 'block';
      inputs.forEach(i => { i.value = ''; });
      inputs[0].focus();
    }
  });

  cancelBtn.addEventListener('click', hidePinModal);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) hidePinModal();
  });
}

function showPinModal() {
  const overlay = document.getElementById('pinModal');
  overlay.classList.add('visible');
  document.querySelector('.pin-digit').focus();
}

function hidePinModal() {
  const overlay = document.getElementById('pinModal');
  overlay.classList.remove('visible');
  document.querySelectorAll('.pin-digit').forEach(i => { i.value = ''; });
  document.getElementById('pinError').style.display = 'none';
}

// ============================================================
//  UTILITY
// ============================================================

function resetState() {
  state.encounterId = null;
  state.patientId = null;
  state.tokenNumber = null;
  state.sessionId = null;
  state.language = 'hi';
  state.isRecording = false;
  state.facts = [];

  // Clear UI
  document.getElementById('conversationArea').innerHTML = '';
  document.getElementById('factsScroll').innerHTML = '';
  document.getElementById('factsCount').textContent = '0 facts';
  document.getElementById('tokenBadge').style.display = 'none';
  document.getElementById('scanResults').style.display = 'none';
  document.getElementById('scanDoneBtn').style.display = 'none';
}
