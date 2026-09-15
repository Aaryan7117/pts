/**
 * MediKiosk Web — Screens 06-07: Conversational Voice Intake
 * Features multi-turn conversational question flow, AI4Bharat IndicF5 speech playback with
 * native WebSpeech failover, noise-resilient ASR, live conversation stream, dynamic clinical fact chips,
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
      mr: 'प्रश्न १ · मुख्य समस्या'
    },
    text: {
      hi: 'नमस्ते, मैं अखिल भारतीय आयुर्वेद संस्थान का डिजिटल सहायक हूँ। आपको क्या परेशानी है? अपनी मुख्य शिकायत बताइए।',
      en: 'Hello, I am the AIIA clinical assistant. What symptoms or primary health concerns are you experiencing today?',
      ta: 'வணக்கம், நான் அகில இந்திய ஆயுர்வேத நிறுவனத்தின் டிஜிட்டல் உதவியாளர். உங்கள் முக்கிய பிரச்சனை என்ன?',
      te: 'నమస్కారం, నేను అఖిల భారత ఆయుర్వేద సంస్థ డిజిటల్ సహాయకుడిని. మీ ప్రధాన సమస్య ఏమిటి?',
      mr: 'नमस्कार, मी अखिल भारतीय आयुर्वेद संस्थेचा डिजिटल सहाय्यक आहे. तुमची मुख्य समस्या काय आहे?'
    }
  },
  {
    step: 'duration',
    badge: {
      hi: 'प्रश्न २ · अवधि (Duration)',
      en: 'Question 2 · Symptom Duration',
      ta: 'கேள்வி 2 · காலம்',
      te: 'ప్రశ్న 2 · వ్యవధి',
      mr: 'प्रश्न २ · कालावधी'
    },
    text: {
      hi: 'यह समस्या कब से है? कितने दिन, हफ्ते या महीने से तकलीफ हो रही है?',
      en: 'How long have you had this problem? Days, weeks, or months?',
      ta: 'இந்தப் பிரச்சனை எவ்வளவு காலமாக உள்ளது? எத்தனை நாட்கள் அல்லது வாரங்கள்?',
      te: 'ఈ సమస్య ఎంతకాలంగా ఉంది? ఎన్ని రోజులు లేదా వారాలుగా బాధపడుతున్నారు?',
      mr: 'ही समस्या किती दिवसांपासून किंवा आठवड्यांपासून आहे?'
    }
  },
  {
    step: 'severity',
    badge: {
      hi: 'प्रश्न ३ · दर्द का स्तर (Severity)',
      en: 'Question 3 · Severity Scale',
      ta: 'கேள்வி 3 · தீவிரம்',
      te: 'ప్రశ్న 3 · తీవ్రత',
      mr: 'प्रश्न ३ · तीव्रता'
    },
    text: {
      hi: '१ से १० के पैमाने पर दर्द या परेशानी कितनी महसूस हो रही है?',
      en: 'On a scale of 1 to 10, how severe is the pain or discomfort?',
      ta: '1 முதல் 10 வரை வலி அல்லது அசௌகரியம் எவ்வளவு கடுமையானது?',
      te: '1 నుండి 10 వరకు నొప్పి లేదా అసౌకర్యం ఎంత తీవ్రంగా ఉంది?',
      mr: '१ ते १० च्या प्रमाणात वेदना किती तीव्र आहे?'
    }
  },
  {
    step: 'medications',
    badge: {
      hi: 'प्रश्न ४ · वर्तमान दवाइयाँ',
      en: 'Question 4 · Current Medications',
      ta: 'கேள்வி 4 · மருந்துகள்',
      te: 'ప్రశ్న 4 · మందులు',
      mr: 'प्रश्न ४ · औषधे'
    },
    text: {
      hi: 'क्या आप इस समय कोई दवाई ले रहे हैं? या हाल ही में कोई दवा बंद की है?',
      en: 'Are you currently taking any medicines, or recently stopped any medications?',
      ta: 'தற்போது ஏதேனும் மருந்துகள் எடுத்துக்கொள்கிறீர்களா?',
      te: 'ప్రస్తుతం ఏవైనా మందులు వాడుతున్నారా?',
      mr: 'सध्या तुम्ही कोणती औषधे घेत आहात का?'
    }
  },
  {
    step: 'allergies',
    badge: {
      hi: 'प्रश्न ५ · एलर्जी व इतिहास',
      en: 'Question 5 · Allergies & History',
      ta: 'கேள்வி 5 · ஒவ்வாமை',
      te: 'ప్రశ్న 5 · అలర్జీలు',
      mr: 'प्रश्न ५ · ॲलर्जी'
    },
    text: {
      hi: 'क्या आपको किसी दवाई या खाद्य पदार्थ से एलर्जी है? या पहले से कोई बीमारी है?',
      en: 'Do you have any drug or food allergies, or any chronic conditions like diabetes or BP?',
      ta: 'உங்களுக்கு ஏதேனும் மருந்து அல்லது உணவு ஒவ்வாமை உள்ளதா?',
      te: 'మీకు ఏదైనా మందు లేదా ఆహార అలర్జీ ఉందా?',
      mr: 'तुम्हाला कोणत्याही औषधाची किंवा अन्नाची ॲलर्जी आहे का?'
    }
  }
];

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
  const initialQuestion = OFFLINE_QUESTIONS[0].text[lang] || OFFLINE_QUESTIONS[0].text.hi;
  const initialBadge = OFFLINE_QUESTIONS[0].badge[lang] || OFFLINE_QUESTIONS[0].badge.hi;

  return `
    <div class="kiosk-shell">
      <div class="kiosk-split">
        <!-- Left Pane: Attendant & Avatar -->
        <div class="kiosk-left-pane">
          <div class="kiosk-brand-card">
            <div class="kiosk-step-indicator">
              Screen 06 · Step 4 of 6 (Clinical Intake)
            </div>
            <h2 class="text-h2" style="margin-top:var(--space-3); font-size:20px;">AI Doctor Consultation</h2>
            <p style="font-size:13px; color:var(--text-secondary); line-height:1.4;">
              Dr. Verma conducts an adaptive clinical intake in your language. Listen to each question, then speak or tap your response.
            </p>
          </div>

          <!-- Doctor Avatar Attendant -->
          <div id="kioskVoiceAvatarContainer" style="margin:var(--space-2) 0; display:flex; justify-content:center;"></div>

          <!-- Live Captured Facts Panel -->
          <div style="background:var(--bg-surface); border:1px solid var(--border-default); border-radius:var(--radius-lg); padding:12px; margin-top:4px;">
            <div style="font-size:11px; font-weight:800; color:var(--brand-primary); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
              <span>🩺 Recognized Clinical Facts</span>
              <span id="factCountBadge" class="badge badge-green" style="font-size:10px; padding:1px 6px;">0 Captured</span>
            </div>
            <div id="kioskFactChipsLive" style="display:flex; flex-wrap:wrap; gap:6px; min-height:36px; align-items:center;">
              <span style="font-size:12px; color:var(--text-muted); font-style:italic;">
                ${lang === 'en' ? 'Facts will appear here as you speak...' : 'बोलने पर लक्षण यहाँ दिखाई देंगे...'}
              </span>
            </div>
          </div>

          <div style="display:flex; flex-direction:column; gap:var(--space-2); margin-top:8px;">
            <div class="kiosk-audio-help-box">
              <span style="font-size:20px;">🔊</span>
              <div style="font-size:12px;">
                <strong>Dual Voice Engine:</strong> AI4Bharat IndicF5 on-device neural voice + WebSpeech offline failover.
              </div>
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
              <canvas id="kioskWaveformCanvas" class="waveform-canvas" width="220" height="38"></canvas>

              <div id="kioskMicStatusText" style="font-size:14px; font-weight:700; color:var(--brand-primary); margin:4px 0 8px;">
                ${i18n.t('tap_to_talk', lang)}
              </div>
            </div>

            <!-- Mode 2: In-UI Touch Typing & Symptom Selector Container -->
            <div id="kioskTypingModeContainer" class="kiosk-typing-card" style="display:none; margin-bottom:4px;">
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
  const conversationStream = document.getElementById('kios  // Add chat bubble to conversation stream
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

        // START RECORDING
        isRecording = true;
        micBtn.classList.add('active');
        statusText.textContent = lang === 'en'
          ? 'Listening... Speak naturally (will auto-submit when done)'
          : 'सुन रहा हूँ... बोलिए (बोलने के बाद स्वतः दर्ज होगा)';
        statusText.style.color = 'var(--status-danger)';
        sounds.playStartListening();

        if (avatarInstance) avatarInstance.setListening(true);

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
      window.location.hash = '#/kiosk/summary';
    });
  }
}

/**
 * Intelligent Dynamic Clinical Fact Parser
 * Parses patient words to extract chief complaint, duration, and pain severity.
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
}��ेजें'} →`;
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
    submitBtn.addEventListener('click', processTurn);
  }

  // Done button: Proceed immediately to summary verification
  if (doneBtn) {
    doneBtn.addEventListener('click', () => {
      tts.stop();
      if (isRecording && micBtn) micBtn.click();
      window.location.hash = '#/kiosk/summary';
    });
  }
}

/**
 * Intelligent Dynamic Clinical Fact Parser
 * Parses patient words to extract chief complaint, duration, and pain severity.
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
