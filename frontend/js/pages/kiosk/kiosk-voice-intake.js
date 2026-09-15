/**
 * MediKiosk Web — Screens 06-07: Conversational Voice Intake
 * Features multi-turn conversational question flow, AI4Bharat IndicF5 speech playback with
 * native WebSpeech failover, noise-resilient ASR, live conversation stream, dynamic clinical fact chips,
 * 3D/2D Doctor Avatar with onboarding pointing animation & real-time synchronization,
 * and touch-typing with localized symptom chips.
 */

import { store } from '../../store.js';
import { sounds } from '../../audio/sound-effects.js';
import { AudioVisualizer } from '../../audio/audio-visualizer.js';
import { AudioRecorder } from '../../audio.js';
import { kioskApi } from '../../api/kiosk.api.js';
import { tts } from '../../audio/tts-reader.js';
import { DoctorAvatar } from '../../components/avatar-3d.js';
import { i18n } from '../../i18n.js';

let visualizer = null;
let activeRecorder = null;
let isRecording = false;
let avatarInstance = null;
let autoPlayTimer = null;
let onboardingTimer = null;
let hasPointedOnboarding = false;
let speechRecognizer = null;
let inputMode = 'voice'; // 'voice' | 'typing'
let currentQuestionText = '';
let currentAudioBase64 = null;
let currentTurnIndex = 0;
let conversationHistory = []; // { sender: 'doctor' | 'patient', text: string }

const SpeechRecognition = typeof window !== 'undefined'
  ? (window.SpeechRecognition || window.webkitSpeechRecognition || null)
  : null;

const OFFLINE_QUESTIONS = [
  {
    step: 'chief_complaint',
    badge: {
      hi: 'प्रश्न १ · मुख्य समस्या',
      en: 'Question 1 · Chief Complaint',
      ta: 'கேள்வி 1 · முக்கிய பிரச்சனை',
      te: 'ప్రశ్న 1 · ప్రధాన సమస్య',
      mr: 'प्रश्न १ · मुख्य तक्रार'
    },
    text: {
      hi: 'नमस्ते! मैं डॉ. वर्मा हूँ। कृपया मुझे बताएं कि आपको क्या परेशानी या बीमारी महसूस हो रही है?',
      en: 'Hello! I am Dr. Verma. Please tell me what main symptoms or discomfort you are experiencing today?',
      ta: 'வணக்கம்! நான் டாக்டர் வர்மா. இன்று உங்களுக்கு என்ன உடல்நல பிரச்சனை உள்ளது என்று சொல்லுங்கள்?',
      te: 'నమస్కారం! నేను డాక్టర్ వర్మ. ఈరోజు మీకు ఎలాంటి అనారోగ్య సమస్య ఉందో దయచేసి చెప్పండి?',
      mr: 'नमस्कार! मी डॉ. वर्मा आहे. कृपया सांगा, आज तुम्हाला काय त्रास किंवा आजार जाणवत आहे?'
    }
  },
  {
    step: 'duration',
    badge: {
      hi: 'प्रश्न २ · अवधि',
      en: 'Question 2 · Duration',
      ta: 'கேள்வி 2 · காலம்',
      te: 'ప్రశ్న 2 · కాలవ్యవధి',
      mr: 'प्रश्न २ · कालावधी'
    },
    text: {
      hi: 'यह समस्या आपको कितने दिनों या समय से हो रही है? क्या यह अचानक शुरू हुई थी?',
      en: 'How long have you had this problem? Did it start suddenly or gradually?',
      ta: 'இந்த பிரச்சனை உங்களுக்கு எத்தனை நாட்களாக உள்ளது? திடீரென தொடங்கியதா?',
      te: 'ఈ సమస్య మీకు ఎన్ని రోజులుగా ఉంది? ఇది హఠాత్తుగా మొదలైందా?',
      mr: 'हा त्रास तुम्हाला किती दिवसांपासून होत आहे? तो अचानक सुरू झाला होता का?'
    }
  },
  {
    step: 'severity',
    badge: {
      hi: 'प्रश्न ३ · तीव्रता',
      en: 'Question 3 · Severity',
      ta: 'கேள்வி 3 · தீவிரம்',
      te: 'ప్రశ్న 3 · తీవ్రత',
      mr: 'प्रश्न ३ · तीव्रता'
    },
    text: {
      hi: 'दर्द या परेशानी कितनी तेज़ है? क्या इससे आपके रोज़मर्रा के कामों में रुकावट आ रही है?',
      en: 'How severe is the pain or discomfort? Is it mild, moderate, or making daily activities difficult?',
      ta: 'வலி அல்லது அசௌகரியம் எவ்வளவு தீவிரமாக உள்ளது? அன்றாட வேலைகளை பாதிக்கிறதா?',
      te: 'నొప్పి లేదా అసౌకర్యం ఎంత తీవ్రంగా ఉంది? దైనందిన పనులకు ఇబ్బందిగా ఉందా?',
      mr: 'त्रास किंवा वेदना किती तीव्र आहे? रोजच्या कामात अडथळा येत आहे का?'
    }
  },
  {
    step: 'associated_symptoms',
    badge: {
      hi: 'प्रश्न ४ · अन्य लक्षण',
      en: 'Question 4 · Other Symptoms',
      ta: 'கேள்வி 4 · பிற அறிகுறிகள்',
      te: 'ప్రశ్న 4 · ఇతర లక్షణాలు',
      mr: 'प्रश्न ४ · इतर लक्षणे'
    },
    text: {
      hi: 'क्या इसके साथ बुखार, चक्कर, उल्टी, या सांस लेने में कोई तकलीफ भी है?',
      en: 'Are you experiencing any other symptoms like fever, dizziness, nausea, or breathlessness?',
      ta: 'இதனுடன் காய்ச்சல், தலைச்சுற்றல் அல்லது வாந்தி போன்ற அறிகுறிகள் ஏதேனும் உள்ளதா?',
      te: 'దీనితో పాటు జ్వరం, మైకం లేదా వాంతులు వంటి ఇతర లక్షణాలు ఉన్నాయా?',
      mr: 'यासोबत ताप, चक्कर येणे, उलटी किंवा श्वास घेण्यास त्रास होत आहे का?'
    }
  },
  {
    step: 'medications',
    badge: {
      hi: 'प्रश्न ५ · पूर्व दवाइयां',
      en: 'Question 5 · Prior Medications',
      ta: 'கேள்வி 5 · மருந்துகள்',
      te: 'ప్రశ్న 5 · ప్రస్తుత మందులు',
      mr: 'प्रश्न ५ · औषधोपचार'
    },
    text: {
      hi: 'क्या आप पहले से बीपी, शुगर, थायराइड की कोई दवा ले रहे हैं? या हाल ही में कोई दवा बंद की है?',
      en: 'Are you currently taking any medications for BP, diabetes, or other chronic conditions?',
      ta: 'நீங்கள் தற்போது ரத்த அழுத்தம், சர்க்கரை நோய்க்கு ஏதேனும் மருந்துகள் எடுத்துக்கொள்கிறீர்களா?',
      te: 'మీరు బీపీ, షుగర్ వంటి వాటికి ప్రస్తుతం ఏవైనా మందులు వాడుతున్నారా?',
      mr: 'तुम्ही रक्तदाब, मधुमेह यासाठी कोणती नियमित औषधे घेत आहात का?'
    }
  }
];

const SYMPTOM_CHIPS = {
  hi: [
    { label: '🔥 तेज़ बुखार', text: 'तेज़ बुखार और कंपकंपी' },
    { label: '🤕 सिरदर्द', text: 'सिर में तेज़ दर्द' },
    { label: '🤧 खांसी व ज़ुकाम', text: 'सूखी खांसी और गले में खराश' },
    { label: '🤢 पेट दर्द', text: 'पेट में दर्द और मरोड़' },
    { label: '🫁 सांस लेने में तकलीफ', text: 'सांस फूलना और भारीपन' },
    { label: '⚡ सीने में दर्द', text: 'सीने में दबाव और बेचैनी' },
    { label: '🦵 जोड़ों में दर्द', text: 'घुटनों और जोड़ों में दर्द व सूजन' },
    { label: '💫 चक्कर व कमजोरी', text: 'चक्कर आना और अत्यधिक कमजोरी' }
  ],
  en: [
    { label: '🔥 High Fever', text: 'High fever with chills' },
    { label: '🤕 Headache', text: 'Severe headache and pressure' },
    { label: '🤧 Cough & Cold', text: 'Dry cough and sore throat' },
    { label: '🤢 Stomach Ache', text: 'Abdominal cramps and pain' },
    { label: '🫁 Shortness of Breath', text: 'Difficulty breathing and chest tightness' },
    { label: '⚡ Chest Pain', text: 'Chest pain and discomfort' },
    { label: '🦵 Joint Pain', text: 'Severe pain and stiffness in joints' },
    { label: '💫 Dizziness', text: 'Feeling dizzy, lightheaded and fatigued' }
  ],
  ta: [
    { label: '🔥 அதிக காய்ச்சல்', text: 'கடுமையான காய்ச்சல் மற்றும் நடுக்கம்' },
    { label: '🤕 தலைவலி', text: 'கடுமையான தலைவலி' },
    { label: '🤧 இருமல்', text: 'வறட்டு இருமல் மற்றும் தொண்டை வலி' },
    { label: '🤢 வயிற்று வலி', text: 'வயிற்று வலி மற்றும் அசெளகரியம்' }
  ],
  te: [
    { label: '🔥 తీవ్ర జ్వరం', text: 'చలితో కూడిన తీవ్ర జ్వరం' },
    { label: '🤕 తలనొప్పి', text: 'తీవ్రమైన తలనొప్పి' },
    { label: '🤧 దగ్గు & జలుబు', text: 'పొడి దగ్గు మరియు గొంతు నొప్పి' },
    { label: '🤢 కడుపు నొప్పి', text: 'కడుపులో విపరీతమైన నొప్పి' }
  ],
  mr: [
    { label: '🔥 तीव्र ताप', text: 'थंडी वाजून तीव्र ताप येणे' },
    { label: '🤕 डोकेदुखी', text: 'तीव्र डोकेदुखी' },
    { label: '🤧 खोकला व सर्दी', text: 'कोरडा खोकला आणि घसा दुखणे' },
    { label: '🤢 पोटदुखी', text: 'पोटात दुखणे व मळमळणे' }
  ]
};

export function renderKioskVoiceIntake() {
  const lang = store.getState().kiosk.language || 'hi';
  const promptText = i18n.t('voice_prompt', lang);
  const subText = i18n.t('voice_sub', lang);

  // Initialize initial question from offline question bank
  const initialEntry = OFFLINE_QUESTIONS[0];
  const initialBadge = initialEntry.badge[lang] || initialEntry.badge.hi;
  const initialQuestion = initialEntry.text[lang] || initialEntry.text.hi;

  return `
    <div class="kiosk-flow-container animate-fade-in">
      <!-- Top Navigation & Progress -->
      <div class="kiosk-top-nav">
        <a href="#/kiosk/care-stream" class="kiosk-back-btn" aria-label="Go Back">
          ← ${i18n.t('back', lang)}
        </a>
        <div class="kiosk-progress-pills">
          <span class="kiosk-step-pill completed">01</span>
          <span class="kiosk-step-pill completed">02</span>
          <span class="kiosk-step-pill completed">03</span>
          <span class="kiosk-step-pill completed">04</span>
          <span class="kiosk-step-pill completed">05</span>
          <span class="kiosk-step-pill active">06</span>
          <span class="kiosk-step-pill">07</span>
          <span class="kiosk-step-pill">08</span>
        </div>
        <div class="kiosk-lang-indicator">${lang.toUpperCase()}</div>
      </div>

      <!-- Main Interactive Content: Left Avatar, Right Question & Live Intake -->
      <div class="kiosk-split-screen" style="display:grid; grid-template-columns: 340px 1fr; gap:var(--space-4); margin-top:var(--space-2); min-height:560px;">
        
        <!-- Left Pane: AI Physician (Dr. Verma) with Live Audio Lip-Sync -->
        <div class="kiosk-left-pane" style="background:var(--bg-surface); border:1px solid var(--border-light); border-radius:var(--radius-xl); padding:var(--space-3); display:flex; flex-direction:column; justify-content:space-between; box-shadow:var(--shadow-sm);">
          <div>
            <div style="display:flex; align-items:center; gap:var(--space-2); margin-bottom:var(--space-1);">
              <span style="font-size:24px;">👨‍⚕️</span>
              <div>
                <h2 style="font-size:16px; font-weight:800; color:var(--text-primary); margin:0;">
                  ${lang === 'en' ? 'Dr. Verma, MD' : 'डॉ. वर्मा (वरिष्ठ चिकित्सक)'}
                </h2>
                <div style="font-size:11px; color:var(--brand-primary); font-weight:700;">
                  ● ${lang === 'en' ? 'AI Clinical Intake Specialist' : 'एआई ओपीडी परामर्श'}
                </div>
              </div>
            </div>
            
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.4; margin:4px 0 8px 0;">
              ${lang === 'en'
                ? 'Dr. Verma conducts an adaptive clinical intake in your language. Listen to each question, then speak or tap your response.'
                : 'डॉ. वर्मा आपसे आपके स्वास्थ्य के बारे में पूछ रहे हैं। प्रश्न सुनें और बोलकर या लिखकर उत्तर दें।'}
            </p>
          </div>

          <!-- Doctor Avatar Display Canvas -->
          <div id="kioskVoiceAvatarContainer" style="margin:var(--space-2) 0; display:flex; justify-content:center;"></div>

          <!-- Live Clinical Extracted Entity Chips -->
          <div style="background:rgba(2,132,199,0.04); border:1px solid rgba(2,132,199,0.15); border-radius:var(--radius-md); padding:10px;">
            <div style="font-size:11px; font-weight:800; color:var(--brand-primary); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
              <span>🩺 ${lang === 'en' ? 'Detected Symptoms' : 'पहचाने गए लक्षण'}:</span>
              <span id="kioskFactCountBadge" class="badge badge-primary" style="font-size:10px; padding:1px 6px;">0</span>
            </div>
            <div id="kioskFactChipsLive" style="display:flex; flex-wrap:wrap; gap:6px; min-height:36px; align-items:center;">
              <span style="font-size:11px; color:var(--text-muted); font-style:italic;">
                ${lang === 'en' ? 'Facts will appear here as you speak...' : 'बोलने पर लक्षण यहाँ दिखाई देंगे...'}
              </span>
            </div>
          </div>
        </div>

        <!-- Right Pane: Doctor Question Banner & Live Intake -->
        <div class="kiosk-right-pane">
          <div class="kiosk-task-canvas" style="display:flex; flex-direction:column; align-items:stretch; text-align:left; gap:var(--space-3);">
            
            <!-- PROMINENT DOCTOR QUESTION BANNER -->
            <div class="doctor-question-banner" id="kioskDoctorQuestionCard" style="background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border: 1.5px solid #93C5FD; border-left: 6px solid var(--brand-primary); border-radius: var(--radius-lg); padding: 16px 20px; box-shadow: var(--shadow-sm); width: 100%;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span id="kioskQuestionStepBadge" class="badge badge-teal" style="font-size: 11px; padding: 4px 10px; font-weight: 800; letter-spacing: 0.04em;">
                  ${initialBadge}
                </span>
                <button type="button" id="btnHearIntakeQuestion" class="btn btn-secondary btn-sm" style="font-size: 12px; padding: 4px 12px; display: inline-flex; align-items: center; gap: 6px;">
                  🔊 ${i18n.t('hear_explanation', lang)}
                </button>
              </div>
              <div id="kioskDoctorQuestionText" style="font-size: 18px; font-weight: 700; color: #0F172A; line-height: 1.5;">
                "${initialQuestion}"
              </div>
            </div>

            <!-- Upstream Onboarding Microphone Instruction Box -->
            <div id="kioskMicrophoneInstructionBox" style="margin-bottom:var(--space-1); padding:8px 16px; border-radius:12px; background:rgba(2,132,199,0.06); border:1px solid rgba(2,132,199,0.2); display:inline-block; transition:all 0.3s ease; text-align:center;">
              <p id="kioskMicrophoneInstruction" style="margin:0; font-size:14px; font-weight:700; color:var(--brand-primary); line-height:1.4;">
                👉 ${subText}
              </p>
            </div>

            <!-- Conversation Stream History -->
            <div id="kioskConversationStream" style="max-height: 140px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding: 8px 12px; background: rgba(241, 245, 249, 0.6); border: 1px solid var(--border-subtle); border-radius: var(--radius-md);">
              <div class="chat-bubble doctor" style="background: #DBEAFE; color: #1E3A8A; font-size: 13px; font-weight: 600; padding: 8px 14px; border-radius: 12px 12px 12px 2px; align-self: flex-start; max-width: 85%;">
                👨‍⚕️ <strong>Dr. Verma:</strong> <span id="initialChatBubble">${initialQuestion}</span>
              </div>
            </div>

            <!-- Mode 1: Voice Recorder Container -->
            <div id="kioskVoiceModeContainer" class="voice-recorder-container" style="display:flex; flex-direction:column; align-items:center; width:100%; margin-top:2px;">
              <div class="mic-btn-wrapper">
                <button id="btnKioskMic" class="mic-btn" aria-label="Tap to Record Speech">
                  <span class="mic-icon" style="font-size:32px;">🎙️</span>
                  <div class="pulse-ring ring-1"></div>
                  <div class="pulse-ring ring-2"></div>
                </button>
              </div>

              <div id="kioskMicStatusText" class="mic-status-label" style="font-size:15px; font-weight:700; margin-top:8px;">
                ${lang === 'en' ? 'Tap microphone to speak' : 'बोलने के लिए माइक दबाएं'}
              </div>

              <!-- Real-time WebAudio Waveform Visualizer -->
              <div class="audio-waveform-container" style="width:100%; max-width:380px; height:44px; margin-top:4px;">
                <canvas id="kioskWaveformCanvas" width="380" height="44" style="width:100%; height:100%; border-radius:var(--radius-md);"></canvas>
              </div>
            </div>

            <!-- Mode 2: Touch Typing Mode Container -->
            <div id="kioskTypingModeContainer" style="display:none; flex-direction:column; width:100%; background:var(--bg-card); border:1px solid var(--border-medium); border-radius:var(--radius-lg); padding:12px; box-shadow:var(--shadow-sm);">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <label for="kioskTypingInput" style="font-weight:700; font-size:13px; color:var(--text-primary);">
                  ⌨️ ${lang === 'en' ? 'Type or Select Your Symptoms' : 'लक्षण लिखें या नीचे से चुनें'}:
                </label>
                <button id="btnClearTyping" class="btn btn-ghost btn-sm" style="font-size:11px; padding:2px 8px;">
                  ✕ ${lang === 'en' ? 'Clear' : 'हटाएं'}
                </button>
              </div>

              <textarea id="kioskTypingInput" class="kiosk-typing-textarea" placeholder="${lang === 'en' ? 'e.g. Fever for 3 days and severe headache...' : 'उदा. ३ दिन से बुखार और सिरदर्द हो रहा है...'}" rows="2"></textarea>

              <div class="kiosk-symptom-chips-container" style="margin-top:6px;">
                <div class="kiosk-symptom-chips-title" style="font-size:11px; font-weight:700;">
                  ⚡ ${lang === 'en' ? 'Quick Symptoms (Tap to add)' : 'सामान्य लक्षण (जोड़ने के लिए दबाएं)'}:
                </div>
                <div class="kiosk-symptom-chips" id="kioskSymptomChips"></div>
              </div>
            </div>

            <!-- Live Speech / Selected Text Display Card -->
            <div class="live-transcript-card" id="kioskLiveTranscript" style="margin-bottom:4px; padding:10px 14px;">
              <span style="color:var(--text-muted); font-style:italic;">
                ${i18n.t('live_transcript_placeholder', lang)}
              </span>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center;">
              <button id="btnToggleInputMode" class="btn btn-secondary btn-sm" style="font-size:12px; padding:4px 14px;">
                ⌨️ ${i18n.t('prefer_typing', lang)}
              </button>
              <span style="font-size:11px; color:var(--text-muted);">
                Auto-saves clinical entities into queue token
              </span>
            </div>
          </div>

          <!-- Dual Action Footer Bar -->
          <div class="kiosk-footer-bar" style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
            <a href="#/kiosk/care-stream" class="btn btn-secondary btn-lg">${i18n.t('back', lang)}</a>
            
            <div style="display:flex; gap:10px;">
              <!-- Send Turn Answer -->
              <button id="btnSubmitAnswer" class="btn btn-primary btn-touch" style="min-width:180px; justify-content:center;" disabled>
                ✓ ${lang === 'en' ? 'Send Answer' : 'उत्तर भेजें'} →
              </button>

              <!-- Finalize & Proceed to Summary -->
              <button id="btnVoiceDone" class="btn btn-ayush btn-touch" style="min-width:200px; justify-content:center;">
                📋 ${lang === 'en' ? 'Review Summary' : 'सारांश देखें'} →
              </button>
            </div>
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
  const submitBtn = document.getElementById('btnSubmitAnswer');
  const doneBtn = document.getElementById('btnVoiceDone');
  const canvas = document.getElementById('kioskWaveformCanvas');
  const toggleBtn = document.getElementById('btnToggleInputMode');
  const voiceContainer = document.getElementById('kioskVoiceModeContainer');
  const typingContainer = document.getElementById('kioskTypingModeContainer');
  const typingInput = document.getElementById('kioskTypingInput');
  const clearTypingBtn = document.getElementById('btnClearTyping');
  const chipsContainer = document.getElementById('kioskSymptomChips');
  const questionCardText = document.getElementById('kioskDoctorQuestionText');
  const questionBadge = document.getElementById('kioskQuestionStepBadge');
  const conversationStream = document.getElementById('kioskConversationStream');
  const instructionBox = document.getElementById('kioskMicrophoneInstructionBox');

  inputMode = 'voice';
  let recordedPatientText = '';
  currentTurnIndex = 0;
  conversationHistory = [];

  const initialEntry = OFFLINE_QUESTIONS[0];
  currentQuestionText = initialEntry.text[lang] || initialEntry.text.hi;
  currentAudioBase64 = null;

  // 1. Doctor Avatar starts strictly in IDLE / LISTENING animation.
  avatarInstance = new DoctorAvatar('kioskVoiceAvatarContainer');
  avatarInstance.mount();
  avatarInstance.setState('idle');

  visualizer = new AudioVisualizer(canvas);

  // 2. INITIAL MICROPHONE INSTRUCTION (Onboarding pointing guidance):
  // When the UI loads:
  // → Play POINTING animation once. Doctor points to the microphone button on the right.
  // → After completion, transition back to IDLE.
  onboardingTimer = setTimeout(() => {
    if (hasPointedOnboarding || !avatarInstance || isRecording) return;
    hasPointedOnboarding = true;

    if (micBtn) {
      micBtn.classList.add('mic-btn-highlight');
    }
    if (instructionBox) {
      instructionBox.style.boxShadow = '0 0 0 4px rgba(2,132,199,0.2)';
      instructionBox.style.background = 'rgba(2,132,199,0.12)';
    }

    avatarInstance.playPointingOnce(() => {
      if (avatarInstance) {
        avatarInstance.setState('idle');
      }
      if (micBtn) {
        micBtn.classList.remove('mic-btn-highlight');
      }
      if (instructionBox) {
        instructionBox.style.boxShadow = '';
        instructionBox.style.background = 'rgba(2,132,199,0.06)';
      }
    });
  }, 700);

  // Audio Question Playback Helper
  function playCurrentQuestion() {
    if (!currentQuestionText) return;
    tts.speak(currentQuestionText, lang, currentAudioBase64);
  }

  // Hear question button (optional user-invoked audio guidance)
  const hearBtn = document.getElementById('btnHearIntakeQuestion');
  if (hearBtn) {
    hearBtn.addEventListener('click', () => {
      playCurrentQuestion();
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
      const currentVal = typingInput ? typingInput.value.trim() : '';
      const newVal = currentVal ? `${currentVal} ${chip.text}` : chip.text;
      if (typingInput) typingInput.value = newVal;
      updateTranscriptDisplay(newVal);
    });
  }

  // Helper to update transcript and enable action buttons
  function updateTranscriptDisplay(text) {
    recordedPatientText = text.trim();
    if (recordedPatientText) {
      if (transcriptCard) {
        transcriptCard.textContent = recordedPatientText;
        transcriptCard.style.color = 'var(--text-primary)';
        transcriptCard.style.fontStyle = 'normal';
      }
      if (submitBtn) submitBtn.disabled = false;
      if (doneBtn) doneBtn.disabled = false;
    } else {
      if (transcriptCard) {
        transcriptCard.innerHTML = `
          <span style="color:var(--text-muted); font-style:italic;">
            ${i18n.t('live_transcript_placeholder', lang)}
          </span>
        `;
      }
      if (submitBtn) submitBtn.disabled = true;
    }
  }

  // Add chat bubble to conversation stream
  function addChatBubble(sender, text, bubbleId = null) {
    if (!conversationStream || !text) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    if (bubbleId) bubble.id = bubbleId;
    if (sender === 'doctor') {
      bubble.style.cssText = 'background:#DBEAFE; color:#1E3A8A; font-size:13px; font-weight:600; padding:8px 14px; border-radius:12px 12px 12px 2px; align-self:flex-start; max-width:85%;';
      bubble.innerHTML = `👨‍⚕️ <strong>Dr. Verma:</strong> ${text}`;
    } else {
      bubble.style.cssText = 'background:#CCFBF1; color:#0F766E; font-size:13px; font-weight:600; padding:8px 14px; border-radius:12px 12px 2px 12px; align-self:flex-end; max-width:85%;';
      bubble.innerHTML = `👤 <strong>${lang === 'en' ? 'You' : 'आप'}:</strong> ${text}`;
    }
    conversationStream.appendChild(bubble);
    conversationStream.scrollTop = conversationStream.scrollHeight;
  }

  // Helper to render live detected fact chips
  function updateFactChipsDisplay() {
    const chipsEl = document.getElementById('kioskFactChipsLive');
    const badgeEl = document.getElementById('kioskFactCountBadge');
    const facts = store.getState().kiosk.extractedFacts || [];

    if (badgeEl) badgeEl.textContent = facts.length;
    if (!chipsEl) return;

    if (facts.length === 0) {
      chipsEl.innerHTML = `
        <span style="font-size:11px; color:var(--text-muted); font-style:italic;">
          ${lang === 'en' ? 'Facts will appear here as you speak...' : 'बोलने पर लक्षण यहाँ दिखाई देंगे...'}
        </span>
      `;
      return;
    }

    chipsEl.innerHTML = facts.map(f => {
      const icon = f.category === 'chief_complaint' ? '🩺' : f.category === 'symptom' ? '⏱️' : '💊';
      return `
        <span class="badge badge-teal" style="font-size:11px; padding:3px 8px; display:inline-flex; align-items:center; gap:4px; font-weight:600;">
          <span>${icon}</span>
          <span>${f.value}</span>
        </span>
      `;
    }).join('');
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
        if (isRecording) stopRecordingAndProcess();
        inputMode = 'typing';
        if (voiceContainer) voiceContainer.style.display = 'none';
        if (typingContainer) typingContainer.style.display = 'flex';
        toggleBtn.innerHTML = `🎙️ ${lang === 'en' ? 'Use Microphone Instead' : 'माइक का उपयोग करें'}`;
        if (typingInput) typingInput.focus();
      } else {
        inputMode = 'voice';
        if (typingContainer) typingContainer.style.display = 'none';
        if (voiceContainer) voiceContainer.style.display = 'flex';
        toggleBtn.innerHTML = `⌨️ ${i18n.t('prefer_typing', lang)}`;
      }
    });
  }

  // Native SpeechRecognition setup (optional preview when online)
  function initSpeechRecognition() {
    if (!SpeechRecognition) return null;
    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;

      const localeMap = { hi: 'hi-IN', en: 'en-IN', ta: 'ta-IN', te: 'te-IN', mr: 'mr-IN' };
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
        console.warn('Browser SpeechRecognition offline or pending (normal in offline kiosk):', err);
      };

      return rec;
    } catch (e) {
      console.warn('SpeechRecognition init skipped:', e);
      return null;
    }
  }

  // Microphone toggle button
  if (micBtn) {
    micBtn.addEventListener('click', async () => {
      if (!isRecording) {
        tts.stop();

        // If onboarding pointing timer is pending, clear it
        if (onboardingTimer) {
          clearTimeout(onboardingTimer);
          onboardingTimer = null;
        }
        hasPointedOnboarding = true;

        // START RECORDING
        isRecording = true;
        micBtn.classList.add('active');
        micBtn.classList.remove('mic-btn-highlight');
        if (instructionBox) {
          instructionBox.style.boxShadow = '';
          instructionBox.style.background = 'rgba(2,132,199,0.06)';
        }
        statusText.textContent = lang === 'en'
          ? 'Listening... Speak naturally (will auto-submit when done)'
          : 'सुन रहा हूँ... बोलिए (बोलने के बाद स्वतः दर्ज होगा)';
        statusText.style.color = 'var(--status-danger)';
        sounds.playStartListening();

        // PATIENT SPEAKING:
        // When the patient activates the microphone and is speaking:
        // → IDLE / LISTENING animation.
        // → Doctor remains seated, attentive, breathing/blinking naturally.
        if (avatarInstance) {
          avatarInstance.setListening(true);
        }

        try {
          activeRecorder = new AudioRecorder();
          await activeRecorder.start();
          visualizer.attachStream(activeRecorder.stream);
          visualizer.start();

          // Auto-submit when silence is detected
          activeRecorder.onSpeechEnd = () => {
            if (isRecording) {
              stopRecordingAndProcess();
            }
          };
        } catch (err) {
          console.warn('Microphone access error:', err);
          statusText.textContent = lang === 'en'
            ? 'Microphone access denied. Please type your symptoms below.'
            : 'माइक्रोफ़ोन की अनुमति नहीं मिली। कृपया नीचे लक्षण लिखें।';
          isRecording = false;
          micBtn.classList.remove('active');
          return;
        }

        speechRecognizer = initSpeechRecognition();
        if (speechRecognizer) {
          try { speechRecognizer.start(); } catch (e) {}
        }

      } else {
        // STOP RECORDING MANUALLY
        await stopRecordingAndProcess();
      }
    });
  }

  async function stopRecordingAndProcess() {
    if (!isRecording) return;
    isRecording = false;
    if (micBtn) micBtn.classList.remove('active');
    sounds.playStopListening();
    if (visualizer) visualizer.stop();
    if (avatarInstance) avatarInstance.setListening(false);

    if (speechRecognizer) {
      try { speechRecognizer.stop(); } catch (_) {}
      speechRecognizer = null;
    }

    if (statusText) {
      statusText.textContent = lang === 'en'
        ? '🎙️ Processing your voice with AI ASR...'
        : '🎙️ आपकी आवाज़ का विश्लेषण किया जा रहा है...';
      statusText.style.color = 'var(--brand-primary)';
    }

    let audioBlob = null;
    if (activeRecorder) {
      try {
        audioBlob = await activeRecorder.stop();
      } catch (err) {
        console.warn('Recorder stop error:', err);
      }
      activeRecorder = null;
    }

    await processTurn(audioBlob);
  }

  // PROCESS TURN
  async function processTurn(audioBlob = null) {
    tts.stop();
    if (isRecording) {
      await stopRecordingAndProcess();
      return;
    }

    const typedText = typingInput ? typingInput.value.trim() : '';
    let previewText = recordedPatientText || typedText;
    if (!previewText && audioBlob) {
      previewText = lang === 'en' ? '🎙️ [Analyzing spoken response...]' : '🎙️ [आवाज़ का विश्लेषण हो रहा है...]';
    } else if (!previewText) {
      previewText = lang === 'en' ? 'General Health Intake' : 'सामान्य स्वास्थ्य परामर्श';
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing...';
    }
    if (statusText) {
      statusText.textContent = 'AI Physician is processing your response...';
      statusText.style.color = 'var(--brand-primary)';
    }

    // Add patient response to chat stream with a unique ID for dynamic update
    const bubbleId = `patient-bubble-${Date.now()}`;
    addChatBubble('patient', previewText, bubbleId);

    // Dynamic rule extraction fallback
    const dynamicFacts = extractClinicalFactsFromText(previewText, lang);

    // Merge with existing facts
    const existingFacts = store.getState().kiosk.extractedFacts || [];
    const mergedFacts = [...existingFacts];
    dynamicFacts.forEach(df => {
      if (!mergedFacts.some(ef => ef.field === df.field && ef.value === df.value)) {
        mergedFacts.push(df);
      }
    });

    store.updateKioskIntake({
      patientWords: previewText,
      extractedFacts: mergedFacts
    });
    updateFactChipsDisplay();

    let nextQuestion = null;
    let nextAudioBase64 = null;
    let isCompleted = false;

    // Send turn to backend
    if (sessionId) {
      try {
        let turnRes = null;
        if (audioBlob && audioBlob.size > 200) {
          turnRes = await kioskApi.sendAudioTurn(sessionId, audioBlob);
        } else if (typedText || recordedPatientText) {
          turnRes = await kioskApi.sendTextTurn(sessionId, typedText || recordedPatientText);
        }

        if (turnRes) {
          // Update bubble with real transcribed text from backend ASR!
          const actualSpoken = turnRes.patient_transcript || (previewText.startsWith('🎙️') ? (lang === 'en' ? 'Voice symptoms recorded' : 'लक्षण दर्ज किए गए') : previewText);
          const bubbleEl = document.getElementById(bubbleId);
          if (bubbleEl) {
            bubbleEl.innerHTML = `👤 <strong>${lang === 'en' ? 'You' : 'आप'}:</strong> ${actualSpoken}`;
          }
          if (transcriptCard) {
            transcriptCard.textContent = actualSpoken;
            transcriptCard.style.color = 'var(--text-primary)';
            transcriptCard.style.fontStyle = 'normal';
          }
          store.updateKioskIntake({ patientWords: actualSpoken });

          nextQuestion = turnRes.next_question_text;
          nextAudioBase64 = turnRes.next_question_audio_base64;
          isCompleted = turnRes.is_completed;

          if (turnRes.extracted_facts && turnRes.extracted_facts.length > 0) {
            turnRes.extracted_facts.forEach(f => {
              const factObj = {
                category: f.category,
                field: f.field,
                value: f.concept || f.value || actualSpoken
              };
              if (!mergedFacts.some(ef => ef.field === factObj.field && ef.value === factObj.value)) {
                mergedFacts.push(factObj);
              }
            });
            store.updateKioskIntake({ extractedFacts: mergedFacts });
            updateFactChipsDisplay();
          }
        }
      } catch (e) {
        console.warn('Backend turn API error, cascading to offline question bank:', e);
      }
    }

    // Offline Question Bank Fallback if backend didn't provide next question
    currentTurnIndex++;
    if (!nextQuestion && currentTurnIndex < OFFLINE_QUESTIONS.length) {
      const qEntry = OFFLINE_QUESTIONS[currentTurnIndex];
      nextQuestion = qEntry.text[lang] || qEntry.text.hi;
    } else if (!nextQuestion) {
      isCompleted = true;
    }

    // Reset inputs for next answer
    recordedPatientText = '';
    if (typingInput) typingInput.value = '';
    document.querySelectorAll('.kiosk-chip-btn.selected').forEach(b => b.classList.remove('selected'));
    updateTranscriptDisplay('');

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = `✓ ${lang === 'en' ? 'Send Answer' : 'उत्तर भेजें'} →`;
    }

    if (isCompleted) {
      const closingSpeech = lang === 'en'
        ? 'Thank you. I have recorded your symptoms. Let us now review your clinical summary.'
        : 'धन्यवाद। मैंने आपकी सभी स्वास्थ्य जानकारी दर्ज कर ली है। अब कृपया सारांश की पुष्टि करें।';
      
      if (questionCardText) questionCardText.textContent = `"${closingSpeech}"`;
      if (statusText) {
        statusText.textContent = 'Intake complete! Moving to summary...';
        statusText.style.color = 'var(--status-success)';
      }
      
      tts.speak(closingSpeech, lang, nextAudioBase64);
      setTimeout(() => {
        window.location.hash = '#/kiosk/summary';
      }, 2500);
      return;
    }

    // Advance to next question
    currentQuestionText = nextQuestion;
    currentAudioBase64 = nextAudioBase64;

    const currentBadgeText = (OFFLINE_QUESTIONS[currentTurnIndex] && OFFLINE_QUESTIONS[currentTurnIndex].badge[lang])
      || `Question ${currentTurnIndex + 1}`;
    
    if (questionBadge) questionBadge.textContent = currentBadgeText;
    if (questionCardText) questionCardText.textContent = `"${currentQuestionText}"`;
    addChatBubble('doctor', currentQuestionText);

    if (statusText) {
      statusText.textContent = lang === 'en'
        ? 'Listening... speak or type your answer'
        : 'बोलें या नीचे लिखें (अगला उत्तर)';
      statusText.style.color = 'var(--brand-primary)';
    }

    // Play new question aloud
    playCurrentQuestion();
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      processTurn();
    });
  }

  // Done button: Proceed immediately to summary verification
  if (doneBtn) {
    doneBtn.addEventListener('click', () => {
      tts.stop();
      if (isRecording) {
        stopRecordingAndProcess();
      }
      const textToSave = recordedPatientText || (typingInput ? typingInput.value.trim() : '');
      if (textToSave) {
        store.updateKioskIntake({ patientWords: textToSave });
      }
      window.location.hash = '#/kiosk/summary';
    });
  }

  // Initial display setup
  updateFactChipsDisplay();
  updateTranscriptDisplay('');
}

function extractClinicalFactsFromText(patientWords, lang) {
  const text = (patientWords || '').toLowerCase();
  
  // 1. Chief Complaint identification
  let problem = 'General Health Consultation';
  if (/fever|बुखार|காய்ச்சல்|జ్వరం|ताप/.test(text)) {
    problem = lang === 'en' ? 'Acute Febrile Illness' : 'तेज़ बुखार (High Fever)';
  } else if (/cough|cold|खांसी|सर्दी|இருமல்|దగ్గు|खोकला/.test(text)) {
    problem = lang === 'en' ? 'Upper Respiratory Tract Infection' : 'खांसी व ज़ुकाम (Cough & Cold)';
  } else if (/chest|breath|सांस|छाती|மார்பு|ఛాతీ|छातीत/.test(text)) {
    problem = lang === 'en' ? 'Chest Discomfort / Dyspnea' : 'सीने में दर्द या सांस फूलना (Chest Pain)';
  } else if (/headache|head|सिरदर्द|सिर|தலைவலி|తలనొప్పి|डोकेदुखी/.test(text)) {
    problem = lang === 'en' ? 'Cephalea (Headache)' : 'सिरदर्द (Severe Headache)';
  } else if (/stomach|abdomen|vomit|diarrhea|पेट|उल्टी|दस्त|வயிறு|కడుపు|पोट/.test(text)) {
    problem = lang === 'en' ? 'Acute Gastroenteritis' : 'पेट दर्द व पाचन विकार (Stomach Pain)';
  } else if (/joint|knee|bone|गठिया|जोड़ों|घुटने|மூட்டு|కీళ్ల|सांधे/.test(text)) {
    problem = lang === 'en' ? 'Arthralgia / Joint Pain' : 'जोड़ों व घुटनों में दर्द (Joint Pain)';
  } else if (/skin|rash|itching|खुजली|त्वचा|தோல்|చర్మ|खाज/.test(text)) {
    problem = lang === 'en' ? 'Skin Rash & Itching' : 'त्वचा एलर्जी व खुजली (Skin Rash)';
  } else if (/weakness|fatigue|dizziness|कमजोरी|चक्कर|களைப்பு|నీரசம்|थकवा/.test(text)) {
    problem = lang === 'en' ? 'General Weakness' : 'कमजोरी व थकान (Weakness)';
  } else {
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
  if (/severe|तेज़|तीव्र|अत्यधिक|கடுமையான|తీవ్రమైన|तीव्र/.test(text)) {
    severity = lang === 'en' ? 'Severe (8/10)' : 'तेज़ (८/१०)';
  } else if (/mild|हल्का|லேசான|తేలికపాటి|सौम्य/.test(text)) {
    severity = lang === 'en' ? 'Mild (3/10)' : 'हल्का (३/१०)';
  }

  return [
    { category: 'chief_complaint', field: 'problem', value: problem },
    { category: 'symptom', field: 'duration', value: duration },
    { category: 'symptom', field: 'severity', value: severity }
  ];
}

export function destroyKioskVoiceIntake() {
  if (onboardingTimer) {
    clearTimeout(onboardingTimer);
    onboardingTimer = null;
  }
  hasPointedOnboarding = false;

  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer);
    autoPlayTimer = null;
  }
  tts.stop();
  if (speechRecognizer) {
    try { speechRecognizer.stop(); } catch (_) {}
    speechRecognizer = null;
  }
  if (activeRecorder) {
    try { activeRecorder.cleanup(); } catch (_) {}
    activeRecorder = null;
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
