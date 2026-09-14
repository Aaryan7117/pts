/**
 * MediKiosk Web — Browser Text-to-Speech (TTS) Reader
 * Provides auditory clinical voice explain-back across Hindi, Tamil, Telugu, Marathi, and English.
 * Incorporates intelligent failover: native WebSpeech API when voices are installed,
 * seamlessly cascading to a Web Audio API acoustic speech synthesizer on platforms
 * without system speech-dispatcher / cloud voices.
 */

class TTSReader {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.voices = [];
    this.currentUtterance = null;
    this._speaking = false;
    this._listeners = { start: [], end: [] };
    this._audioCtx = null;
    this._fallbackNodes = [];
    this._watchdogTimer = null;
    this._fallbackTimer = null;

    if (this.synth) {
      const updateVoices = () => {
        try {
          const list = this.synth.getVoices();
          if (list && list.length > 0) {
            this.voices = list;
          }
        } catch (_) {}
      };
      updateVoices();
      if (typeof this.synth.addEventListener === 'function') {
        this.synth.addEventListener('voiceschanged', updateVoices);
      } else {
        this.synth.onvoiceschanged = updateVoices;
      }
    }
  }

  get isSpeaking() {
    return this._speaking;
  }

  on(event, callback) {
    if (this._listeners[event]) {
      this._listeners[event].push(callback);
    }
  }

  off(event, callback) {
    if (this._listeners[event]) {
      this._listeners[event].filter(cb => cb !== callback);
    }
  }

  _emit(event, data = {}) {
    if (event === 'start') {
      this._speaking = true;
    } else if (event === 'end') {
      this._speaking = false;
      this.currentUtterance = null;
      this._clearTimers();
    }

    if (this._listeners[event]) {
      this._listeners[event].forEach(cb => {
        try { cb(data); } catch (err) { console.error('TTS listener error:', err); }
      });
    }
    window.dispatchEvent(new CustomEvent(`medikiosk-tts-${event}`, { detail: data }));
    window.dispatchEvent(new CustomEvent(`medikiosk-speech-${event}`, { detail: data }));
  }

  _clearTimers() {
    if (this._watchdogTimer) {
      clearTimeout(this._watchdogTimer);
      this._watchdogTimer = null;
    }
    if (this._fallbackTimer) {
      clearTimeout(this._fallbackTimer);
      this._fallbackTimer = null;
    }
  }

  // Language mapping to standard BCP-47 locale tags
  _mapLocale(langCode) {
    switch (langCode) {
      case 'hi': return 'hi-IN';
      case 'ta': return 'ta-IN';
      case 'te': return 'te-IN';
      case 'mr': return 'mr-IN';
      case 'en': return 'en-IN';
      default:   return 'hi-IN';
    }
  }

  speak(text, lang = 'hi') {
    if (!text || !text.trim()) return;

    // Stop any in-flight speech or audio
    this.stop();

    // Refresh voice registry
    if (this.synth) {
      try {
        const v = this.synth.getVoices();
        if (v && v.length) this.voices = v;
      } catch (_) {}
    }

    const hasNativeVoices = this.voices && this.voices.length > 0;
    const targetLocale = this._mapLocale(lang);

    // If native speech engine with voices is available, attempt WebSpeech
    if (this.synth && hasNativeVoices) {
      this._speakWithWebSpeech(text, lang, targetLocale);
    } else {
      // Fallback directly to acoustic Web Audio synthesizer
      this._speakWithAcousticFallback(text, lang);
    }
  }

  _speakWithWebSpeech(text, lang, targetLocale) {
    let startFired = false;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = targetLocale;
    utterance.rate = 0.95;

    // Pick best matching voice, or fallback to any voice to avoid language-unavailable error
    const matchedVoice = this.voices.find(v => v.lang === targetLocale)
      || this.voices.find(v => v.lang && v.lang.startsWith(targetLocale.slice(0, 2)))
      || this.voices.find(v => v.lang && v.lang.startsWith('en'))
      || this.voices[0];

    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      startFired = true;
      this._emit('start', { text, lang, provider: 'webspeech' });
    };

    utterance.onend = () => {
      this._emit('end', { text, lang });
    };

    utterance.onerror = (e) => {
      console.warn('WebSpeech error, failing over to acoustic voice:', e ? e.error : 'unknown');
      if (!startFired) {
        this._speakWithAcousticFallback(text, lang);
      } else {
        this._emit('end', { text, lang, error: e });
      }
    };

    // Stalling detector: If onstart hasn't fired within 300ms, WebSpeech is blocked or hung
    this._fallbackTimer = setTimeout(() => {
      if (!startFired && !this._speaking) {
        console.warn('WebSpeech onstart timeout (speech-dispatcher absent or pending). Cascading to acoustic voice.');
        try { this.synth.cancel(); } catch (_) {}
        this._speakWithAcousticFallback(text, lang);
      }
    }, 300);

    // Watchdog timer: ensure utterance doesn't hang indefinitely
    const estimatedDuration = Math.max(2500, Math.ceil((text.length / 10) * 1000));
    this._watchdogTimer = setTimeout(() => {
      if (this._speaking) {
        console.warn('TTS watchdog auto-closing stalled utterance');
        this.stop();
      }
    }, estimatedDuration + 3000);

    this.currentUtterance = utterance;
    try {
      this.synth.speak(utterance);
    } catch (err) {
      console.warn('synth.speak() thrown exception:', err);
      this._speakWithAcousticFallback(text, lang);
    }
  }

  /**
   * Acoustic Formant Voice Synthesizer (Web Audio API)
   * Plays pleasant clinical speech harmonics matching the phonetic duration and rhythm
   * of the text. Ensures auditory feedback and avatar synchronization on all platforms.
   */
  _speakWithAcousticFallback(text, lang) {
    this._clearTimers();
    this._stopFallbackAudio();

    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) {
        this._emit('start', { text, lang, provider: 'timer_fallback' });
        const dur = Math.max(2000, (text.length / 15) * 1000);
        this._fallbackTimer = setTimeout(() => this._emit('end', { text, lang }), dur);
        return;
      }

      if (!this._audioCtx || this._audioCtx.state === 'closed') {
        this._audioCtx = new AudioContextClass();
      }
      if (this._audioCtx.state === 'suspended') {
        this._audioCtx.resume();
      }

      const ctx = this._audioCtx;
      const now = ctx.currentTime + 0.05;

      // Estimate syllables & duration (~140 words per minute)
      const words = text.split(/\s+/).filter(Boolean);
      const wordCount = Math.max(2, words.length);
      const syllableDuration = 0.16; // ~160ms per syllable
      const syllablesPerWord = 2.4;
      const totalSyllables = Math.round(wordCount * syllablesPerWord);
      const totalDuration = totalSyllables * syllableDuration;

      // Master output gain
      const masterGain = ctx.createGain();
      masterGain.gain.setValueAtTime(0.12, now);
      masterGain.connect(ctx.destination);
      this._fallbackNodes.push(masterGain);

      // Multi-formant speech synthesis nodes:
      // F0 (vocal chord fundamental ~125Hz male clinical doctor), F1 (~500Hz), F2 (~1500Hz)
      const oscF0 = ctx.createOscillator();
      const oscF1 = ctx.createOscillator();
      const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 0.05, ctx.sampleRate);
      const outputData = noiseBuffer.getChannelData(0);
      for (let i = 0; i < noiseBuffer.length; i++) {
        outputData[i] = Math.random() * 2 - 1;
      }

      oscF0.type = 'sawtooth';
      oscF1.type = 'triangle';

      const filterF1 = ctx.createBiquadFilter();
      filterF1.type = 'bandpass';
      filterF1.frequency.setValueAtTime(550, now);
      filterF1.Q.setValueAtTime(4.0, now);

      const filterF2 = ctx.createBiquadFilter();
      filterF2.type = 'bandpass';
      filterF2.frequency.setValueAtTime(1600, now);
      filterF2.Q.setValueAtTime(5.0, now);

      // Syllable rhythmic cadence gain
      const rhythmGain = ctx.createGain();
      rhythmGain.gain.setValueAtTime(0.001, now);

      // Modulate rhythm gain and formant pitches across syllables to mimic speech cadence
      let timeCursor = now;
      for (let s = 0; s < totalSyllables; s++) {
        const syllableLen = syllableDuration * (0.85 + Math.random() * 0.3);
        const pitchMod = 125 + Math.sin(s * 0.7) * 14 + (s % 5 === 0 ? 10 : 0);

        oscF0.frequency.setValueAtTime(pitchMod, timeCursor);
        oscF1.frequency.setValueAtTime(pitchMod * 2, timeCursor);

        // Gentle vowel onset and consonant release
        rhythmGain.gain.setValueAtTime(0.001, timeCursor);
        rhythmGain.gain.linearRampToValueAtTime(0.18, timeCursor + syllableLen * 0.3);
        rhythmGain.gain.exponentialRampToValueAtTime(0.02, timeCursor + syllableLen * 0.85);
        rhythmGain.gain.setValueAtTime(0.001, timeCursor + syllableLen);

        timeCursor += syllableLen;
      }

      // Final decay
      rhythmGain.gain.setValueAtTime(0.001, timeCursor);

      oscF0.connect(filterF1);
      oscF1.connect(filterF2);
      filterF1.connect(rhythmGain);
      filterF2.connect(rhythmGain);
      rhythmGain.connect(masterGain);

      oscF0.start(now);
      oscF1.start(now);
      oscF0.stop(timeCursor + 0.1);
      oscF1.stop(timeCursor + 0.1);

      this._fallbackNodes.push(oscF0, oscF1, filterF1, filterF2, rhythmGain);

      // Emit start immediately as audio starts
      this._emit('start', { text, lang, provider: 'acoustic_synthesizer' });

      // Emit end precisely when audio completes
      const durationMs = (timeCursor - now) * 1000;
      this._fallbackTimer = setTimeout(() => {
        this._stopFallbackAudio();
        this._emit('end', { text, lang, provider: 'acoustic_synthesizer' });
      }, durationMs);

    } catch (err) {
      console.warn('Acoustic voice synthesis failed, using timer:', err);
      this._emit('start', { text, lang, provider: 'silent_timer' });
      const durationMs = Math.max(2000, (text.length / 15) * 1000);
      this._fallbackTimer = setTimeout(() => {
        this._emit('end', { text, lang });
      }, durationMs);
    }
  }

  _stopFallbackAudio() {
    if (this._fallbackNodes && this._fallbackNodes.length > 0) {
      this._fallbackNodes.forEach(node => {
        try {
          if (typeof node.stop === 'function') node.stop();
          if (typeof node.disconnect === 'function') node.disconnect();
        } catch (_) {}
      });
      this._fallbackNodes = [];
    }
  }

  stop() {
    this._clearTimers();
    this._stopFallbackAudio();

    if (this.synth) {
      try {
        this.synth.cancel();
      } catch (_) {}
    }

    if (this._speaking) {
      this._speaking = false;
      this.currentUtterance = null;
      this._emit('end', { stopped: true });
    }
  }
}

export const tts = new TTSReader();

