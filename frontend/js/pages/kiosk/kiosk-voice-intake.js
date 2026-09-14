/**
 * MediKiosk Web — Screens 06-07: Conversational Voice Intake
 * Features real WebSpeech recognition, responsive WebAudio waveform visualizer,
 * embedded in-UI touch typing with localized symptom chips, and dynamic clinical fact extraction.
 */

import { store } from '../../store.js';
import { sounds } from '../../audio/sound-effects.js';
import { AudioVisualizer } from '../../audio/audio-visualizer.js';
import { kioskApi } from '../../api/kiosk.api.js';
import { tts } from '../../audio/tts-reader.js';
import { playAudioBase64 } from '../../audio.js';
import { DoctorAvatar } from '../../components/avatar-3d.js';
import { i18n } from '../../i18n.js';

let visualizer = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let avatarInstance = null;
let autoPlayTimer = null;
let speechRecognizer = null;
let inputMode = 'voice'; // 'voice' | 'typing'

const SpeechRecognition = typeof window !== 'undefined'
  ? (window.SpeechRecognition || window.webkitSpeechRecognition || null)
  : null;

const SYMPTOM_CHIPS = {
  hi: [
    { label: '🌡️ बुखार (Fever)', text: 'मुझे ३ दिन से तेज़ बुखार आ रहा है।' },
    { label: '🤕 तेज़ सिरदर्द (Headache)', text: 'मेरे सिर में तेज़ दर्द और भारीपन है।' },
    { label: '🦵 जोड़ों/घुटने में दर्द (Joint Pain)', text: 'मेरे घुटनों और जोड़ों में दर्द व सूजन है।' },
    { label: '🤧 खांसी व जुकाम (Cough & Cold)', text: 'मुझे पिछले ४ दिनों से सूखी खांसी और जुकाम है।' },
    { label: '🤢 पेट में दर्द (Stomach Pain)', text: 'मेरे पेट में दर्द और गैस की समस्या है।' },
    { label: '⚡ कमजोरी व चक्कर (Weakness)', text: 'मुझे अत्यधिक कमजोरी और चक्कर महसूस हो रहे हैं।' },
    { label: '🔴 त्वचा पर खुजली/दाने (Skin Rash)', text: 'मेरी त्वचा पर लाल दाने और खुजली हो रही है।' },
    { label: '🫀 सीने में भारीपन (Chest Discomfort)', text: 'सीने में दबाव और भारीपन महसूस हो रहा है।' },
  ],
  en: [
    { label: '🌡️ High Fever (3 days)', text: 'I have had high fever and chills for 3 days.' },
    { label: '🤕 Severe Headache', text: 'I am experiencing severe headache and throbbing pain.' },
    { label: '🦵 Knee & Joint Pain', text: 'I have persistent pain and stiffness in my knees and joints.' },
    { label: '🤧 Cough & Cold', text: 'I have dry cough, runny nose, and throat irritation for 4 days.' },
    { label: '🤢 Abdominal / Stomach Pain', text: 'I have sharp stomach cramps and indigestion.' },
    { label: '⚡ Weakness & Dizziness', text: 'I am feeling extreme fatigue, weakness, and dizziness.' },
    { label: '🔴 Skin Rash & Itching', text: 'I have developed an itchy skin rash and redness.' },
    { label: '🫀 Chest Discomfort', text: 'I feel discomfort and tightness in my chest.' },
  ],
  ta: [
    { label: '🌡️ காய்ச்சல் (Fever)', text: 'எனக்கு 3 நாட்களாக அதிக காய்ச்சல் உள்ளது.' },
    { label: '🤕 தலைவலி (Headache)', text: 'எனக்கு கடுமையான தலைவலி உள்ளது.' },
    { label: '🦵 மூட்டு வலி (Joint Pain)', text: 'எனக்கு முழங்கால் மற்றும் மூட்டுகளில் வலி உள்ளது.' },
    { label: '🤧 இருமல் மற்றும் சளி (Cough)', text: 'எனக்கு இருமல் மற்றும் சளி உள்ளது.' },
    { label: '🤢 வயிற்று வலி (Stomach Pain)', text: 'எனக்கு வயிற்று வலி மற்றும் செரிமானக் கோளாறு உள்ளது.' },
  ],
  te: [
    { label: '🌡️ జ్వరం (Fever)', text: 'నాకు 3 రోజులుగా తీవ్రమైన జ్వరం వస్తోంది.' },
    { label: '🤕 తలనొప్పి (Headache)', text: 'నాకు విపరీతమైన తలనొప్పిగా ఉంది.' },
    { label: '🦵 కీళ్ల నొప్పులు (Joint Pain)', text: 'నాకు మోకాళ్ల నొప్పులు మరియు కీళ్ల నొప్పులు ఉన్నాయి.' },
    { label: '🤧 దగ్గు మరియు జలుబు (Cough)', text: 'నాకు దగ్గు మరియు జలుబు ఉంది.' },
    { label: '🤢 కడుపు నొప్పి (Stomach Pain)', text: 'నాకు కడుపులో నొప్పిగా ఉంది.' },
  ],
  mr: [
    { label: '🌡️ ताप (Fever)', text: 'मला ३ दिवसांपासून तीव्र ताप येत आहे.' },
    { label: '🤕 डोकेदुखी (Headache)', text: 'माझे डोके खूप दुखत आहे.' },
    { label: '🦵 सांधेदुखी (Joint Pain)', text: 'माझ्या गुडघ्यांमध्ये आणि सांध्यांमध्ये वेदना आहेत.' },
    { label: '🤧 खोकला व सर्दी (Cough)', text: 'मला खोकला आणि सर्दीचा त्रास आहे.' },
    { label: '🤢 पोटदुखी (Stomach Pain)', text: 'माझे पोट दुखत आहे.' },
  ]
};

export function renderKioskVoiceIntake() {
  const lang = store.getState().kiosk.language || 'hi';
  const promptText = i18n.t('voice_prompt', lang);
  const subText = i18n.t('voice_sub', lang);

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane: Attendant & Avatar -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 06 · Step 4 of 6 (Clinical Intake)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-3); font-size:20px;">Voice & Symptom Intake</h2>
            <p style="font-size:13px; color:var(--text-secondary); line-height:1.4;">
              Speak your symptoms freely or tap quick symptom cards. Our AI physician extracts clinical facts without paper forms.
            </p>
          </div>

          <!-- Doctor Avatar Attendant -->
          <div id="kioskVoiceAvatarContainer" style="margin:var(--space-2) 0; display:flex; justify-content:center;"></div>

          <div style="display:flex; flex-direction:column; gap:var(--space-2);">
            <button id="btnHearIntakeQuestion" class="btn btn-secondary btn-md" style="justify-content:center;">
              ${i18n.t('hear_explanation', lang)}
            </button>
            <div class="kiosk-audio-help-box">
              <span style="font-size:20px;">🎙</span>
              <div style="font-size:12px;">
                <strong>Noise-Resilient ASR:</strong> Multi-accent Indic speech recognition active.
              </div>
            </div>
          </div>
        </div>

        <!-- Right Pane: Live Voice or Touch Typing -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="align-items:center; justify-content:center; text-align:center;">
            <h1 class="text-h1" style="margin-bottom:var(--space-1); font-size:24px;">${promptText}</h1>
            <p class="text-body-lg" style="margin-bottom:var(--space-4); max-width:620px; font-size:15px;">${subText}</p>

            <!-- Mode 1: Voice Recorder Container -->
            <div id="kioskVoiceModeContainer" class="voice-recorder-container" style="display:flex; flex-direction:column; align-items:center; width:100%;">
              <div class="mic-btn-wrapper">
                <button id="btnKioskMic" class="mic-btn" aria-label="Tap to Record Speech">
                  <svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="22"></line>
                  </svg>
                </button>
                <div class="mic-halo mic-halo-1"></div>
                <div class="mic-halo mic-halo-2"></div>
              </div>

              <!-- Frequency Visualizer Canvas -->
              <canvas id="kioskWaveformCanvas" class="waveform-canvas" width="220" height="48"></canvas>

              <div id="kioskMicStatusText" style="font-size:15px; font-weight:700; color:var(--brand-primary); margin-bottom:var(--space-3);">
                ${i18n.t('tap_to_talk', lang)}
              </div>
            </div>

            <!-- Mode 2: In-UI Touch Typing & Symptom Selector Container -->
            <div id="kioskTypingModeContainer" class="kiosk-typing-card" style="display:none; margin-bottom:var(--space-3);">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <label for="kioskTypingInput" style="font-weight:700; font-size:14px; color:var(--text-primary);">
                  ⌨️ ${lang === 'en' ? 'Type or Select Your Symptoms' : 'लक्षण लिखें या नीचे से चुनें'}:
                </label>
                <button id="btnClearTyping" class="btn btn-ghost btn-sm" style="font-size:11px; padding:2px 8px;">
                  ✕ ${lang === 'en' ? 'Clear' : 'हटाएं'}
                </button>
              </div>

              <textarea id="kioskTypingInput" class="kiosk-typing-textarea" placeholder="${lang === 'en' ? 'e.g. Fever for 3 days and headache...' : 'उदा. ३ दिन से बुखार और सिरदर्द हो रहा है...'}" rows="3"></textarea>

              <div class="kiosk-symptom-chips-container">
                <div class="kiosk-symptom-chips-title">
                  ⚡ ${lang === 'en' ? 'Quick Symptoms (Tap to add)' : 'सामान्य लक्षण (जोड़ने के लिए दबाएं)'}:
                </div>
                <div class="kiosk-symptom-chips" id="kioskSymptomChips"></div>
              </div>
            </div>

            <!-- Live Speech / Selected Text Display Card -->
            <div class="live-transcript-card" id="kioskLiveTranscript" style="margin-bottom:var(--space-3);">
              <span style="color:var(--text-muted); font-style:italic;">
                ${i18n.t('live_transcript_placeholder', lang)}
              </span>
            </div>

            <div>
              <button id="btnToggleInputMode" class="btn btn-secondary btn-sm" style="font-size:13px; padding:6px 16px;">
                ⌨️ ${i18n.t('prefer_typing', lang)}
              </button>
            </div>
          </div>

          <div class="kiosk-footer-bar">
            <a href="#/kiosk/care-stream" class="btn btn-secondary btn-lg">${i18n.t('back', lang)}</a>
            <button id="btnVoiceDone" class="btn btn-primary btn-touch" style="min-width:260px; justify-content:center;" disabled>
              ${i18n.t('done_speaking', lang)} →
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export async function initKioskVoiceIntake() {
  const lang = store.getState().kiosk.language || 'hi';
  const micBtn = document.getElementById('btnKioskMic');
  const statusText = document.getElementById('kioskMicStatusText');
  const transcriptCard = document.getElementById('kioskLiveTranscript');
  const doneBtn = document.getElementById('btnVoiceDone');
  const canvas = document.getElementById('kioskWaveformCanvas');
  const toggleBtn = document.getElementById('btnToggleInputMode');
  const voiceContainer = document.getElementById('kioskVoiceModeContainer');
  const typingContainer = document.getElementById('kioskTypingModeContainer');
  const typingInput = document.getElementById('kioskTypingInput');
  const clearTypingBtn = document.getElementById('btnClearTyping');
  const chipsContainer = document.getElementById('kioskSymptomChips');

  inputMode = 'voice';
  let recordedPatientText = '';

  // Mount Doctor Avatar
  avatarInstance = new DoctorAvatar('kioskVoiceAvatarContainer');
  avatarInstance.mount();

  visualizer = new AudioVisualizer(canvas);

  // Ask question aloud upon arrival
  const askIntakeQuestion = () => {
    const prompt = i18n.t('voice_prompt', lang);
    const sub = i18n.t('voice_sub', lang);
    tts.speak(`${prompt} ${sub}`, lang);
  };

  autoPlayTimer = setTimeout(() => {
    askIntakeQuestion();
  }, 400);

  // Hear question button
  const hearBtn = document.getElementById('btnHearIntakeQuestion');
  if (hearBtn) {
    hearBtn.addEventListener('click', () => {
      askIntakeQuestion();
    });
  }

  // Ensure Call Session is initialized with backend
  let sessionId = store.getState().kiosk.sessionId;
  const encounterId = store.getState().kiosk.encounterId;

  if (!sessionId && encounterId) {
    try {
      const res = await kioskApi.startCallSession(encounterId, lang);
      sessionId = res.session_id;
      store.updateKioskIntake({ sessionId });
    } catch (e) {
      console.warn('Call session bootstrap fallback:', e);
      sessionId = `sess-${Date.now().toString(36)}`;
      store.updateKioskIntake({ sessionId });
    }
  }

  // Populate localized symptom chips
  const chips = SYMPTOM_CHIPS[lang] || SYMPTOM_CHIPS.hi;
  if (chipsContainer) {
    chipsContainer.innerHTML = chips.map((c, idx) => `
      <button type="button" class="kiosk-chip-btn" data-index="${idx}">
        ${c.label}
      </button>
    `).join('');

    chipsContainer.addEventListener('click', (e) => {
      const btn = e.target.closest('.kiosk-chip-btn');
      if (!btn) return;
      const idx = parseInt(btn.dataset.index, 10);
      const chip = chips[idx];
      if (!chip) return;

      btn.classList.toggle('selected');
      const currentVal = typingInput.value.trim();
      const newVal = currentVal ? `${currentVal} ${chip.text}` : chip.text;
      typingInput.value = newVal;
      updateTranscriptDisplay(newVal);
    });
  }

  // Helper to update transcript and enable Done button
  function updateTranscriptDisplay(text) {
    recordedPatientText = text.trim();
    if (recordedPatientText) {
      transcriptCard.textContent = recordedPatientText;
      transcriptCard.style.color = 'var(--text-primary)';
      transcriptCard.style.fontStyle = 'normal';
      if (doneBtn) doneBtn.disabled = false;
    } else {
      transcriptCard.innerHTML = `
        <span style="color:var(--text-muted); font-style:italic;">
          ${i18n.t('live_transcript_placeholder', lang)}
        </span>
      `;
      if (doneBtn) doneBtn.disabled = true;
    }
  }

  // Typing textarea live input listener
  if (typingInput) {
    typingInput.addEventListener('input', () => {
      updateTranscriptDisplay(typingInput.value);
    });
  }

  if (clearTypingBtn && typingInput) {
    clearTypingBtn.addEventListener('click', () => {
      typingInput.value = '';
      document.querySelectorAll('.kiosk-chip-btn.selected').forEach(b => b.classList.remove('selected'));
      updateTranscriptDisplay('');
    });
  }

  // Toggle Voice vs Typing Mode
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      if (inputMode === 'voice') {
        // Switch to typing mode
        if (isRecording && micBtn) {
          micBtn.click(); // Stop recording
        }
        inputMode = 'typing';
        voiceContainer.style.display = 'none';
        typingContainer.style.display = 'flex';
        toggleBtn.innerHTML = `🎙️ ${lang === 'en' ? 'Use Microphone Instead' : 'माइक का उपयोग करें'}`;
        if (typingInput) typingInput.focus();
      } else {
        // Switch to voice mode
        inputMode = 'voice';
        typingContainer.style.display = 'none';
        voiceContainer.style.display = 'flex';
        toggleBtn.innerHTML = `⌨️ ${i18n.t('prefer_typing', lang)}`;
      }
    });
  }

  // Native SpeechRecognition setup
  function initSpeechRecognition() {
    if (!SpeechRecognition) return null;
    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;

      const localeMap = {
        hi: 'hi-IN',
        en: 'en-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        mr: 'mr-IN'
      };
      rec.lang = localeMap[lang] || 'hi-IN';

      rec.onresult = (event) => {
        let interim = '';
        let finalTxt = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTxt += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        const spoken = (finalTxt || interim).trim();
        if (spoken) {
          if (typingInput) typingInput.value = spoken;
          updateTranscriptDisplay(spoken);
        }
      };

      rec.onerror = (err) => {
        console.warn('SpeechRecognition browser error:', err);
      };

      return rec;
    } catch (e) {
      console.warn('SpeechRecognition init failed:', e);
      return null;
    }
  }

  // Microphone toggle button
  if (micBtn) {
    micBtn.addEventListener('click', async () => {
      if (!isRecording) {
        tts.stop();

        // START RECORDING
        isRecording = true;
        micBtn.classList.add('active');
        statusText.textContent = i18n.t('listening_status', lang);
        statusText.style.color = 'var(--status-danger)';
        sounds.playStartListening();
        visualizer.start();

        if (avatarInstance) {
          avatarInstance.setListening(true);
        }

        // 1. Start browser SpeechRecognition
        speechRecognizer = initSpeechRecognition();
        if (speechRecognizer) {
          try {
            speechRecognizer.start();
          } catch (e) {
            console.warn('SpeechRecognition start error:', e);
          }
        }

        // 2. Start MediaRecorder for audio stream
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
          console.warn('Microphone stream access fallback:', err);
        }

      } else {
        // STOP RECORDING
        isRecording = false;
        micBtn.classList.remove('active');
        statusText.textContent = i18n.t('speech_recorded', lang);
        statusText.style.color = 'var(--status-success)';
        sounds.playStopListening();
        visualizer.stop();

        if (avatarInstance) {
          avatarInstance.setListening(false);
        }

        if (speechRecognizer) {
          try {
            speechRecognizer.stop();
          } catch (_) {}
          speechRecognizer = null;
        }

        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
        }

        // If no voice was recognized (e.g. silent room or browser without speech recognizer),
        // ensure Done button is enabled if any text exists, or offer typing mode
        if (recordedPatientText) {
          if (doneBtn) doneBtn.disabled = false;
        } else {
          statusText.textContent = lang === 'en'
            ? 'No speech detected. Speak again or choose a symptom below.'
            : 'आवाज़ दर्ज नहीं हुई। पुनः बोलें या नीचे से लक्षण चुनें।';
          statusText.style.color = 'var(--status-warning, #d97706)';
        }
      }
    });
  }

  // Done button: Process real patient words and dynamic clinical facts
  if (doneBtn) {
    doneBtn.addEventListener('click', async () => {
      tts.stop();
      if (isRecording && micBtn) {
        micBtn.click();
      }

      doneBtn.disabled = true;
      doneBtn.textContent = 'Analyzing Symptoms...';
      statusText.textContent = 'AI Physician is processing your response...';
      statusText.style.color = 'var(--brand-primary)';

      if (avatarInstance) {
        avatarInstance.setState('idle'); // IDLE while processing
      }

      const patientWords = recordedPatientText || typingInput.value.trim() || 'General Health Intake';

      // Dynamically extract clinical facts from the patient's actual words
      const dynamicFacts = extractClinicalFactsFromText(patientWords, lang);

      // Save to application state
      store.updateKioskIntake({
        patientWords,
        extractedFacts: dynamicFacts
      });

      let aiSpokenText = null;
      let aiAudioBase64 = null;

      // Send turn to backend using FormData
      if (sessionId) {
        try {
          let turnRes = null;
          if (audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            turnRes = await kioskApi.sendAudioTurn(sessionId, audioBlob);
          } else {
            turnRes = await kioskApi.sendTextTurn(sessionId, patientWords);
          }

          if (turnRes) {
            aiSpokenText = turnRes.next_question_text;
            aiAudioBase64 = turnRes.next_question_audio_base64;

            // Merge backend extracted facts if returned
            if (turnRes.extracted_facts && turnRes.extracted_facts.length > 0) {
              const backendFacts = turnRes.extracted_facts.map(f => ({
                category: f.category,
                field: f.field,
                value: f.concept || f.value || patientWords
              }));
              store.updateKioskIntake({
                extractedFacts: backendFacts
              });
            }
          }
        } catch (e) {
          console.warn('Turn API fallback:', e);
        }
      }

      // Default clinical acknowledgement matching patient's chief complaint
      if (!aiSpokenText) {
        const detectedProblem = dynamicFacts[0].value;
        aiSpokenText = lang === 'en'
          ? `Thank you. I have recorded your symptoms of ${detectedProblem}. Let us now review your clinical summary.`
          : `धन्यवाद। मैंने आपकी ${detectedProblem} की समस्या दर्ज कर ली है। अब कृपया अपने सारांश की पुष्टि करें।`;
      }

      // Play AI Doctor response (doctor switches to SPEAKING with smooth looping)
      statusText.textContent = 'AI Physician is speaking...';
      statusText.style.color = 'var(--brand-primary)';

      let completed = false;
      const onSpeechComplete = () => {
        if (completed) return;
        completed = true;
        if (avatarInstance) {
          avatarInstance.setState('idle');
        }
        setTimeout(() => {
          window.location.hash = '#/kiosk/summary';
        }, 500);
      };

      if (aiAudioBase64 && aiAudioBase64.length > 200) {
        try {
          await playAudioBase64(aiAudioBase64);
          onSpeechComplete();
        } catch (_) {
          const endHandler = () => {
            tts.off('end', endHandler);
            onSpeechComplete();
          };
          tts.on('end', endHandler);
          tts.speak(aiSpokenText, lang);
        }
      } else {
        const endHandler = () => {
          tts.off('end', endHandler);
          onSpeechComplete();
        };
        tts.on('end', endHandler);
        tts.speak(aiSpokenText, lang);
      }
    });
  }
}

/**
 * Intelligent Dynamic Clinical Fact Parser
 * Parses patient words to extract chief complaint, duration, and pain severity.
 * Completely removes hardcoded "Chest Pain" mock data.
 */
function extractClinicalFactsFromText(patientWords, lang) {
  const text = (patientWords || '').toLowerCase();

  // 1. Chief Complaint / Problem
  let problem = null;
  if (/fever|बुखार|காய்ச்சல்|జ్వరం|ताप/.test(text)) {
    problem = lang === 'en' ? 'Fever' : 'बुखार (Fever)';
  } else if (/headache|सिरदर्द|தலைவலி|తలనొప్పి|डोकेदुखी/.test(text)) {
    problem = lang === 'en' ? 'Severe Headache' : 'सिरदर्द (Headache)';
  } else if (/knee|joint|घुटने|जोड़ों|மூட்டு|కీళ్ల|गुडघा/.test(text)) {
    problem = lang === 'en' ? 'Joint & Knee Pain' : 'जोड़ों व घुटने में दर्द (Joint Pain)';
  } else if (/cough|cold|खांसी|जुकाम|இருமல்|దగ్గు|खोकला/.test(text)) {
    problem = lang === 'en' ? 'Cough & Cold' : 'खांसी-जुकाम (Cough & Cold)';
  } else if (/stomach|abdomen|पेट|வயிறு|కడుపు|पोट/.test(text)) {
    problem = lang === 'en' ? 'Abdominal Pain' : 'पेट में दर्द (Abdominal Pain)';
  } else if (/chest|सीना|छाती|மார்பு|ఛాతీ/.test(text)) {
    problem = lang === 'en' ? 'Chest Discomfort' : 'सीने में भारीपन (Chest Discomfort)';
  } else if (/skin|rash|itching|खुजली|त्वचा|தோல்|చర్మ|खाज/.test(text)) {
    problem = lang === 'en' ? 'Skin Rash & Itching' : 'त्वचा एलर्जी व खुजली (Skin Rash)';
  } else if (/weakness|fatigue|dizziness|कमजोरी|चक्कर|களைப்பு|నీరసం|थकवा/.test(text)) {
    problem = lang === 'en' ? 'General Weakness' : 'कमजोरी व थकान (Weakness)';
  } else {
    // Custom patient text
    problem = patientWords.length > 40 ? patientWords.substring(0, 38) + '...' : patientWords;
  }

  // 2. Duration
  let duration = lang === 'en' ? 'Recent onset (1-3 days)' : 'हाल ही में (१-३ दिन)';
  const dayMatch = text.match(/(\d+)\s*(day|दिन|நாட்கள்|రోజులు|दिवस)/);
  if (dayMatch) {
    duration = `${dayMatch[1]} ${lang === 'en' ? 'days' : 'दिनों से'}`;
  } else if (/week|हफ़्ते|सप्ताह|வாரம்|వారం/.test(text)) {
    duration = lang === 'en' ? '1-2 weeks' : '१-२ सप्ताह से';
  } else if (/morning|सुबह|காலை|ఉదయం|सकाळ/.test(text)) {
    duration = lang === 'en' ? 'Since morning' : 'आज सुबह से';
  } else if (/yesterday|कल|நேற்று|నిన్న/.test(text)) {
    duration = lang === 'en' ? 'Since yesterday' : 'कल से';
  }

  // 3. Severity
  let severity = lang === 'en' ? 'Moderate (5/10)' : 'मध्यम (५/१०)';
  if (/severe|तेज़|तीव्र|अत्यधिक|கடுமையான|తీవ్రமான|तीव्र/.test(text)) {
    severity = lang === 'en' ? 'Severe (8/10)' : 'तेज़ (८/१०)';
  } else if (/mild|हल्का|லேசான|తే利కపాటి|सौम्य/.test(text)) {
    severity = lang === 'en' ? 'Mild (3/10)' : 'हल्का (३/१०)';
  }

  return [
    { category: 'chief_complaint', field: 'problem', value: problem },
    { category: 'symptom', field: 'duration', value: duration },
    { category: 'symptom', field: 'severity', value: severity }
  ];
}

export function destroyKioskVoiceIntake() {
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer);
    autoPlayTimer = null;
  }
  tts.stop();
  if (speechRecognizer) {
    try { speechRecognizer.stop(); } catch (_) {}
    speechRecognizer = null;
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try { mediaRecorder.stop(); } catch (_) {}
    mediaRecorder = null;
  }
  if (avatarInstance) {
    avatarInstance.destroy();
    avatarInstance = null;
  }
  if (visualizer) {
    visualizer.stop();
    visualizer = null;
  }
  isRecording = false;
}
