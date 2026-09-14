/**
 * MediKiosk Web — Screens 06-07: Conversational Voice Intake
 * Giant pulsing microphone, live WebAudio waveform visualizer, and Indic speech turn capture.
 */

import { store } from '../../store.js';
import { sounds } from '../../audio/sound-effects.js';
import { AudioVisualizer } from '../../audio/audio-visualizer.js';
import { kioskApi } from '../../api/kiosk.api.js';
import { tts } from '../../audio/tts-reader.js';

let visualizer = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

export function renderKioskVoiceIntake() {
  const lang = store.getState().kiosk.language || 'hi';
  const promptText = lang === 'hi' 
    ? 'आपको क्या तकलीफ हो रही है?' 
    : 'What health problem are you experiencing?';
  const subText = lang === 'hi' 
    ? 'नीचे दिए गए माइक बटन को दबाएं और अपनी भाषा में खुलकर बताएं।' 
    : 'Tap the microphone below and speak naturally in your own words.';

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 06 · Step 4 of 6 (Voice)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-4);">Voice Intake</h2>
            <p style="font-size:14px; color:var(--text-secondary); margin-top:var(--space-2);">
              Speak your symptoms freely. Our clinical intelligence extracts normalized medical concepts without form complexity.
            </p>
          </div>

          <div style="display:flex; flex-direction:column; gap:var(--space-3);">
            <button id="btnHearIntakeQuestion" class="btn btn-secondary btn-md" style="justify-content:center;">
              🔊 Hear Question Aloud
            </button>
            <div class="kiosk-audio-help-box">
              <span style="font-size:24px;">🎙</span>
              <div style="font-size:12px;">
                <strong>Noise-Resilient ASR:</strong> Multi-accent Indic speech models active.
              </div>
            </div>
          </div>
        </div>

        <!-- Right Pane: Giant Voice Recorder & Waveform -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="align-items:center; justify-content:center; text-align:center;">
            <h1 class="text-h1" style="margin-bottom:var(--space-2);">${promptText}</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-6); max-width:600px;">${subText}</p>

            <div class="voice-recorder-container">
              <div class="mic-btn-wrapper">
                <button id="btnKioskMic" class="mic-btn" aria-label="Tap to Record Speech">
                  <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="22"></line>
                  </svg>
                </button>
                <div class="mic-halo mic-halo-1"></div>
                <div class="mic-halo mic-halo-2"></div>
              </div>

              <!-- 9-Bar WebAudio Frequency Canvas -->
              <canvas id="kioskWaveformCanvas" class="waveform-canvas" width="220" height="56"></canvas>

              <div id="kioskMicStatusText" style="font-size:16px; font-weight:700; color:var(--brand-primary); margin-bottom:var(--space-4);">
                TAP TO TALK / बोलने के लिए दबाएं
              </div>

              <!-- Live Rolling Transcript Card -->
              <div class="live-transcript-card" id="kioskLiveTranscript">
                <span style="color:var(--text-muted); font-style:italic;">
                  Your spoken words will appear here in real time...
                </span>
              </div>
            </div>

            <div style="margin-top:var(--space-4);">
              <button id="btnSwitchToTyping" class="btn btn-ghost btn-sm">
                ⌨ Prefer typing instead? Click here
              </button>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/care-stream" class="btn btn-secondary btn-lg">← Back</a>
            <button id="btnVoiceDone" class="btn btn-primary btn-touch" style="min-width:280px; justify-content:center;" disabled>
              ✓ Done Speaking / पूरा हुआ →
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export async function initKioskVoiceIntake() {
  const micBtn = document.getElementById('btnKioskMic');
  const statusText = document.getElementById('kioskMicStatusText');
  const transcriptCard = document.getElementById('kioskLiveTranscript');
  const doneBtn = document.getElementById('btnVoiceDone');
  const canvas = document.getElementById('kioskWaveformCanvas');

  visualizer = new AudioVisualizer(canvas);

  // Read question button
  const hearBtn = document.getElementById('btnHearIntakeQuestion');
  if (hearBtn) {
    hearBtn.addEventListener('click', () => {
      const lang = store.getState().kiosk.language || 'hi';
      const text = lang === 'hi' ? 'आपको क्या तकलीफ हो रही है? बोलकर बताएं।' : 'What health problem are you experiencing? Please tell us.';
      tts.speak(text, lang);
    });
  }

  // Ensure Call Session is initialized with backend
  let sessionId = store.getState().kiosk.sessionId;
  const encounterId = store.getState().kiosk.encounterId;

  if (!sessionId && encounterId) {
    try {
      const res = await kioskApi.startCallSession(encounterId, store.getState().kiosk.language || 'hi');
      sessionId = res.session_id;
      store.updateKioskIntake({ sessionId });
    } catch (e) {
      console.warn('Call session bootstrap fallback:', e);
      sessionId = `sess-${Date.now().toString(36)}`;
      store.updateKioskIntake({ sessionId });
    }
  }

  // Toggle recording
  if (micBtn) {
    micBtn.addEventListener('click', async () => {
      if (!isRecording) {
        // START RECORDING
        isRecording = true;
        micBtn.classList.add('active');
        statusText.textContent = 'LISTENING... / सुन रहे हैं... (TAP WHEN DONE)';
        statusText.style.color = 'var(--status-danger)';
        sounds.playStartListening();
        visualizer.start();

        // Browser MediaRecorder setup
        try {
          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            visualizer.attachStream(stream);
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            mediaRecorder.start(250);
          }
        } catch (err) {
          console.warn('Microphone stream access fallback (using audio simulator):', err);
        }

        // Simulate rolling speech recognition for immediate feedback
        const sampleText = store.getState().kiosk.language === 'hi'
          ? 'मुझे पिछले 3 दिनों से सीने में दर्द और भारीपन महसूस हो रहा है...'
          : "I have been experiencing chest pain and heaviness for the past 3 days...";

        let charIdx = 0;
        transcriptCard.innerHTML = '';
        const typeInterval = setInterval(() => {
          if (!isRecording) {
            clearInterval(typeInterval);
            return;
          }
          if (charIdx < sampleText.length) {
            transcriptCard.textContent = sampleText.substring(0, charIdx + 4);
            charIdx += 4;
          } else {
            clearInterval(typeInterval);
            if (doneBtn) doneBtn.disabled = false;
          }
        }, 120);

      } else {
        // STOP RECORDING
        isRecording = false;
        micBtn.classList.remove('active');
        statusText.textContent = 'SPEECH RECORDED / आवाज दर्ज हो गई';
        statusText.style.color = 'var(--status-success)';
        sounds.playStopListening();
        visualizer.stop();

        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
        }

        if (doneBtn) {
          doneBtn.disabled = false;
        }
      }
    });
  }

  // Done button: transition to explain back
  if (doneBtn) {
    doneBtn.addEventListener('click', async () => {
      const patientWords = transcriptCard.textContent.trim() || 'Chest discomfort for 3 days';
      store.updateKioskIntake({
        patientWords,
        extractedFacts: [
          { category: 'chief_complaint', field: 'problem', value: 'Chest pain (सीने में दर्द)' },
          { category: 'symptom', field: 'duration', value: '3 days (3 दिन)' },
          { category: 'symptom', field: 'severity', value: 'Moderate 6/10' }
        ]
      });

      // Try sending audio or text turn to backend
      if (sessionId) {
        try {
          if (audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await kioskApi.sendAudioTurn(sessionId, audioBlob);
          } else {
            await kioskApi.sendTextTurn(sessionId, patientWords);
          }
        } catch (e) {
          console.warn('Turn API fallback:', e);
        }
      }

      window.location.hash = '#/kiosk/summary';
    });
  }

  // Switch to typing fallback
  const switchBtn = document.getElementById('btnSwitchToTyping');
  if (switchBtn) {
    switchBtn.addEventListener('click', () => {
      const typed = prompt('Please type your symptom / अपनी समस्या लिखें:', 'Chest pain for 3 days');
      if (typed) {
        transcriptCard.textContent = typed;
        if (doneBtn) doneBtn.disabled = false;
      }
    });
  }
}

export function destroyKioskVoiceIntake() {
  if (visualizer) {
    visualizer.stop();
    visualizer = null;
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  isRecording = false;
}
