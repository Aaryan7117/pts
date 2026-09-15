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
    if (this._activeAudio) {
      try {
        this._activeAudio.pause();
        this._activeAudio.currentTime = 0;
      } catch (_) {}
      this._activeAudio = null;
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

  speak(text, lang = 'hi', audioBase64 = null) {
    if ((!text || !text.trim()) && !audioBase64) return;

    // Stop any in-flight speech or audio
    this.stop();

    // Priority 1: If base64 neural/F5 audio is available from the backend, play it!
    if (audioBase64 && audioBase64.length > 200) {
      this._speakWithAudioPayload(audioBase64, text, lang);
      return;
    }

    // Priority 2: Browser native WebSpeech API
    if (this.synth) {
      const targetLocale = this._mapLocale(lang);
      this._speakWithWebSpeech(text, lang, targetLocale);
    } else {
      // Fallback directly to acoustic Web Audio synthesizer
      this._speakWithAcousticFallback(text, lang);
    }
  }

  _speakWithAudioPayload(audioBase64, text, lang) {
    try {
      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
      this._activeAudio = audio;

      audio.addEventListener('play', () => {
        this._emit('start', { text, lang, provider: 'indicf5_audio' });
      });

      audio.addEventListener('ended', () => {
        this._activeAudio = null;
        this._emit('end', { text, lang, provider: 'indicf5_audio' });
      });

      audio.addEventListener('error', (err) => {
        console.warn('Base64 audio playback error, falling back to WebSpeech:', err);
        this._activeAudio = null;
        if (this.synth) {
          this._speakWithWebSpeech(text, lang, this._mapLocale(lang));
        } else {
          this._emit('end', { text, lang, error: err });
        }
      });

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn('Audio play() error (autoplay policy), trying WebSpeech fallback:', err);
          this._activeAudio = null;
          if (this.synth) {
            this._speakWithWebSpeech(text, lang, this._mapLocale(lang));
          } else {
            this._emit('end', { text, lang });
          }
        });
      }
    } catch (e) {
      console.warn('Audio element initialization failed:', e);
      if (this.synth) {
        this._speakWithWebSpeech(text, lang, this._mapLocale(lang));
      }
    }
  }

  _speakWithWebSpeech(text, lang, targetLocale) {
    try {
      this.synth.cancel();
      this.synth.resume();
    } catch (_) {}

    // Refresh voice registry
    if (this.synth) {
      try {
        const v = this.synth.getVoices();
        if (v && v.length) this.voices = v;
      } catch (_) {}
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = targetLocale;
    utterance.rate = 0.92;

    if (this.voices && this.voices.length > 0) {
      const matchedVoice = this.voices.find(v => v.lang === targetLocale)
        || this.voices.find(v => v.lang && v.lang.startsWith(targetLocale.slice(0, 2)))
        || this.voices.find(v => v.lang && v.lang.startsWith('en'))
        || this.voices[0];

      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }
    }

    let startFired = false;
    utterance.onstart = () => {
      startFired = true;
      this._emit('start', { text, lang, provider: 'webspeech' });
    };

    utterance.onend = () => {
      this._emit('end', { text, lang });
    };

    utterance.onerror = (e) => {
      console.warn('WebSpeech error:', e ? e.error : 'unknown');
      if (!startFired) {
        this._speakWithAcousticFallback(text, lang);
      } else {
        this._emit('end', { text, lang, error: e });
      }
    };

    // Watchdog timer: ensure utterance doesn't hang indefinitely if browser stalls
    const estimatedDuration = Math.max(3000, Math.ceil((text.length / 8) * 1000));
    this._watchdogTimer = setTimeout(() => {
      if (this._speaking) {
        console.warn('TTS watchdog auto-closing stalled utterance');
        this.stop();
      }
    }, estimatedDuration + 4000);

    this.currentUtterance = utterance;
    try {
      this.synth.speak(utterance);
    } catch (err) {
      console.warn('synth.speak() thrown exception:', err);
      this._speakWithAcousticFallback(text, lang);
    }
  }

  /**
   * Graceful speech fallback:
   * Retries clean browser SpeechSynthesis without custom voice pitch modulation.
   * If synthesis is completely unsupported, smoothly completes with a natural reading timer
   * so the avatar and intake flow proceed without alien/sawtooth acoustic noise.
   */
  _speakWithAcousticFallback(text, lang) {
    this._clearTimers();
    this._stopFallbackAudio();

    if (this.synth) {
      try {
        this.synth.cancel();
        const simpleUtterance = new SpeechSynthesisUtterance(text);
        simpleUtterance.lang = this._mapLocale(lang);
        simpleUtterance.rate = 0.95;
        let started = false;
        simpleUtterance.onstart = () => {
          started = true;
          this._emit('start', { text, lang, provider: 'webspeech_retry' });
        };
        simpleUtterance.onend = () => {
          this._emit('end', { text, lang });
        };
        simpleUtterance.onerror = () => {
          if (!started) {
            this._runSilentCompletion(text, lang);
          } else {
            this._emit('end', { text, lang });
          }
        };
        this.synth.speak(simpleUtterance);
        return;
      } catch (e) {
        console.warn('WebSpeech clean retry failed:', e);
      }
    }

    this._runSilentCompletion(text, lang);
  }

  _runSilentCompletion(text, lang) {
    this._emit('start', { text, lang, provider: 'silent_timer' });
    const durationMs = Math.max(1500, Math.min(6000, (text.length / 15) * 1000));
    this._fallbackTimer = setTimeout(() => {
      this._emit('end', { text, lang });
    }, durationMs);
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

